"""
agents/synthesis_agent.py (SADA-Solana)

Synthesis Agent: reconcilia, para cada instrucao analisada, os achados do Static
Agent com os resultados do Dynamic Agent e decide o relatorio final.

Como no SADA original (Secao 5.4), e uma instancia "limpa" do modelo: nao recebe a
base de conhecimento nem o codigo do programa, so os dois relatorios. Diferencas da
versao EVM (adaptacoes, registradas na metodologia):
1. Saida em JSON com uma decisao por achado (report | discard), em vez de Markdown
   livre. As metricas saem dessa decisao, sem extrator por palavras-chave (na EVM o
   extrator contou recomendacoes genericas como achados).
2. O agente so decide sobre categorias que o Static apontou: categoria nova e
   descartada pelo codigo, e achado omitido pelo LLM e mantido (ver normalize).
3. Temperatura 0, como os outros agentes da versao Solana.
O relatorio em Markdown e gerado a partir do JSON (render_markdown).
"""

import hashlib
import json

from agents.llm import LLMResult, chat_json, parse_json
from agents.static_agent import CATEGORIES

PROMPT_VERSION = "synthesis-v1"
MAX_TOKENS = 2500

SYSTEM_PROMPT = """Voce e o componente de SINTESE de um sistema multiagente (SADA) que audita programas da blockchain Solana.

Voce recebe, para uma instrucao de um programa, dois relatorios independentes:
1. ANALISE ESTATICA: possiveis vulnerabilidades apontadas a partir do codigo-fonte, cada uma com categoria,
   evidencia, explicacao e hipotese de ataque.
2. ANALISE DINAMICA: para cada achado estatico, o resultado de uma tentativa de explorar a hipotese executando
   o binario compilado num ambiente Solana simulado (Mollusk):
   - "confirmed": um uso legitimo funcionou, o ataque foi aceito e o dano foi verificado no estado das contas;
   - "not_confirmed": o uso legitimo funcionou, mas o ataque foi rejeitado pelo programa (codigo de erro
     informado) ou foi aceito sem dano;
   - "inconclusive": nenhuma tentativa conseguiu montar um cenario valido; a execucao nao fornece evidencia
     nem a favor nem contra.

Sua tarefa e decidir, para CADA achado estatico, se ele entra no relatorio final ("report") ou nao ("discard"),
pesando as duas evidencias, e redigir o relatorio consolidado.

REGRAS:
- Decida sobre todos os achados recebidos, um por categoria, e somente sobre eles. Nao crie categorias novas.
- Justifique cada decisao citando a evidencia estatica e o resultado da execucao.
- Para cada achado reportado, atribua severidade (critica | alta | media | baixa) e confianca (alta | media | baixa),
  e escreva uma recomendacao de correcao especifica.

FORMATO DE SAIDA (somente JSON valido):
{
  "summary": "<2 a 3 frases sobre a postura de seguranca da instrucao>",
  "findings": [
    {
      "category": "<uma das chaves recebidas>",
      "decision": "report" | "discard",
      "severity": "critica" | "alta" | "media" | "baixa" | null,
      "confidence": "alta" | "media" | "baixa",
      "justification": "<por que reportar ou descartar>",
      "recommendation": "<correcao especifica, ou null se descartado>"
    }
  ]
}"""

USER_TEMPLATE = """Instrucao analisada: `{instruction}` (framework: {framework})

RELATORIO DE ANALISE ESTATICA E RESULTADOS DA ANALISE DINAMICA:
{items}

Gere o JSON pedido, com uma decisao para cada categoria: {keys}."""

ITEM_TEMPLATE = """--- Achado {n}: {key} ({name}) ---
[Estatica] confianca: {confidence}
evidencia:
{evidence}
explicacao: {explanation}
hipotese de ataque: {hypothesis}
[Dinamica] veredito: {verdict}
resultado do ataque: {attack_result}
plano executado: {plan}
motivo: {reason}"""


def prompt_fingerprint() -> dict:
    blob = SYSTEM_PROMPT + USER_TEMPLATE + ITEM_TEMPLATE + PROMPT_VERSION
    return {"synthesis_prompt_version": PROMPT_VERSION,
            "synthesis_prompt_sha256": hashlib.sha256(blob.encode()).hexdigest()[:16]}


def _dynamic_view(dyn: dict) -> dict:
    """So o que vai ao LLM: veredito, resultado, plano e motivo. O codigo dos cenarios e os
    rastros de execucao ficam fora (o motivo ja resume os efeitos medidos)."""
    if not dyn:
        return {"verdict": "nao executada", "attack_result": "-", "plan": "-", "reason": "-"}
    last_plan = next((a.get("plan") for a in reversed(dyn.get("attempts", [])) if a.get("plan")), "")
    return {"verdict": dyn.get("verdict", "-"), "attack_result": dyn.get("attack_result") or "-",
            "plan": last_plan or "-", "reason": (dyn.get("reason") or "-")[:1200]}


def build_user_prompt(case_ctx: dict, pairs: list) -> str:
    items = []
    for n, (f, dyn) in enumerate(pairs, 1):
        d = _dynamic_view(dyn)
        items.append(ITEM_TEMPLATE.format(
            n=n, key=f["category"], name=CATEGORIES[f["category"]], confidence=f.get("confidence", "-"),
            evidence=f.get("evidence", ""), explanation=f.get("explanation", ""),
            hypothesis=f.get("attack_hypothesis", ""), **d))
    return USER_TEMPLATE.format(instruction=case_ctx["instruction"], framework=case_ctx["framework"],
                                items="\n\n".join(items), keys=", ".join(f["category"] for f, _ in pairs))


def normalize(parsed: dict, input_keys: list) -> dict:
    """Uma decisao por categoria de entrada. Categoria fora da entrada: descartada pelo codigo
    (o Synthesis nao cria achados). Categoria de entrada omitida pelo LLM: mantida como 'report'
    (o achado estatico nao foi refutado por ninguem) e contada em 'omitted'."""
    decided, extra = {}, []
    for f in parsed.get("findings") or []:
        if not isinstance(f, dict):
            continue
        key = str(f.get("category", "")).strip().upper()
        if key not in input_keys:
            extra.append(f)
            continue
        if key in decided:
            continue
        dec = str(f.get("decision", "")).strip().lower()
        f["category"], f["decision"] = key, dec if dec in ("report", "discard") else "report"
        decided[key] = f
    omitted = [k for k in input_keys if k not in decided]
    for k in omitted:
        decided[k] = {"category": k, "decision": "report", "severity": None, "confidence": None,
                      "justification": "omitido pelo Synthesis; mantido o achado estatico", "recommendation": None}
    findings = [decided[k] for k in input_keys]
    return {"summary": str(parsed.get("summary", "")), "findings": findings,
            "predicted": sorted(f["category"] for f in findings if f["decision"] == "report"),
            "extra_categories": extra, "omitted": omitted}


def run_synthesis(case_ctx: dict, pairs: list, client=None) -> dict:
    """case_ctx: instruction, framework. pairs: [(achado estatico, registro do Dynamic ou None)],
    um por categoria. Sem achados, nao chama o LLM."""
    if not pairs:
        return {"llm": None, "raw": None, "summary": "Nenhum achado da analise estatica.", "findings": [],
                "predicted": [], "extra_categories": [], "omitted": [], "parse_error": None}
    keys = [f["category"] for f, _ in pairs]
    res: LLMResult = chat_json(SYSTEM_PROMPT, build_user_prompt(case_ctx, pairs), client=client,
                               max_tokens=MAX_TOKENS)
    rec = {"llm": {"model": res.model, "prompt_tokens": res.prompt_tokens,
                   "completion_tokens": res.completion_tokens, "latency_s": res.latency_s,
                   "attempts": res.attempts},
           "raw": res.text}
    try:
        rec.update(normalize(parse_json(res.text), keys))
        rec["parse_error"] = None
    except (ValueError, TypeError, AttributeError) as e:
        # JSON invalido: nenhum achado foi refutado, mantem os do Static
        rec.update({"summary": "", "findings": [], "predicted": sorted(keys), "extra_categories": [],
                    "omitted": keys, "parse_error": str(e)})
    rec["inputs"] = [{"category": f["category"], "dynamic_verdict": (d or {}).get("verdict")} for f, d in pairs]
    return rec


def render_markdown(case_id: str, case_ctx: dict, rec: dict) -> str:
    """Relatorio consolidado legivel, gerado do JSON (nao entra nas metricas)."""
    verdicts = {i["category"]: i["dynamic_verdict"] for i in rec.get("inputs", [])}
    out = [f"# Relatorio consolidado: {case_id} (`{case_ctx['instruction']}`)", "", "## Resumo", "",
           rec.get("summary") or "-", ""]
    rep = [f for f in rec["findings"] if f["decision"] == "report"]
    dis = [f for f in rec["findings"] if f["decision"] == "discard"]
    out += ["## Vulnerabilidades reportadas", ""]
    if not rep:
        out += ["Nenhuma.", ""]
    for f in rep:
        origin = "Estatica + Dinamica" if verdicts.get(f["category"]) == "confirmed" else "Estatica"
        out += [f"### {CATEGORIES[f['category']]} ({f['category']})", "",
                f"- **Origem:** {origin} (execucao: {verdicts.get(f['category']) or 'nao executada'})",
                f"- **Severidade:** {f.get('severity') or '-'}",
                f"- **Confianca:** {f.get('confidence') or '-'}",
                f"- **Justificativa:** {f.get('justification') or '-'}",
                f"- **Recomendacao:** {f.get('recommendation') or '-'}", ""]
    if dis:
        out += ["## Achados descartados", ""]
        for f in dis:
            out += [f"- **{f['category']}** (execucao: {verdicts.get(f['category'])}): {f.get('justification') or '-'}"]
        out.append("")
    return "\n".join(out)
