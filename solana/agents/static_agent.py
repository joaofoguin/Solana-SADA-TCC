"""
agents/static_agent.py (SADA-Solana)

Agente de Analise Estatica, adaptado de agents/static_agent.py da replicacao EVM.

Mantido da EVM: Llama 3.3 70B via Groq, sem fine-tuning; base de conhecimento
injetada no system prompt; regra de priorizar precisao.

Alterado para Solana:
- A base de conhecimento fica em agents/knowledge_base.md, escrita pelo autor a
  partir das fontes citadas (no lugar de OWASP/SWC).
- Unidade de analise: uma instrucao-alvo.
- Saida em JSON com categoria de um conjunto fechado (sem extracao por
  palavras-chave, como no evaluation/metrics.py da EVM).
- Cada achado traz uma hipotese de ataque, que sera a entrada do Dynamic Agent.

Protocolo: o prompt e a base de conhecimento so podem ser ajustados com base em
execucoes no Development Set. Toda execucao registra a versao e o hash.
"""

import hashlib
from pathlib import Path

from agents.llm import LLMResult, chat_json, parse_json

PROMPT_VERSION = "static-v1"
KB_PATH = Path(__file__).resolve().parent / "knowledge_base.md"

CATEGORIES = {
    "SIGNER": "Missing Signer Check",
    "OWNER": "Improper Owner Check",
    "CPI": "Arbitrary CPI",
    "PDA": "Improper PDA Validation / Canonicalization",
    "SYSVAR": "Sysvar Account Check",
    "MATH": "Integer Overflow / Underflow",
    "COSPLAY": "Type Cosplay",
    "REINIT": "Reinitialization Attacks",
}

SYSTEM_TEMPLATE = """Voce e o componente de ANALISE ESTATICA de um sistema multiagente (SADA) que audita programas da blockchain Solana escritos em Rust (Anchor ou nativo).

Voce examina o codigo-fonte SEM executa-lo e decide se a INSTRUCAO-ALVO indicada contem alguma das categorias da base de conhecimento abaixo.

BASE DE CONHECIMENTO:
{knowledge_base}

REGRAS:
- Analise somente a instrucao-alvo: o handler, a struct de contas que ele recebe e as funcoes auxiliares que ele chama. Ignore as demais instrucoes do arquivo.
- Use somente estas chaves de categoria: {keys}.
- Considere as verificacoes feitas pelo framework (tipos e constraints do Anchor) e pelo proprio codigo antes de reportar.
- Nomes de funcoes e variaveis nao indicam se o codigo e seguro; decida pelo comportamento do codigo.
- Cite o trecho de codigo que sustenta cada achado.
- Priorize precisao: e melhor omitir uma suspeita fraca do que gerar um falso positivo.
- Se nao houver achado, devolva "findings": [].

FORMATO DE SAIDA (somente JSON valido, sem texto fora dele):
{{
  "instruction": "<nome da instrucao-alvo>",
  "findings": [
    {{
      "category": "<uma das chaves>",
      "confidence": "high | medium | low",
      "evidence": "<trecho de codigo>",
      "explanation": "<por que o trecho configura a categoria>",
      "attack_hypothesis": "<quais contas ou argumentos um atacante forneceria e qual resultado esperaria>"
    }}
  ],
  "summary": "<uma frase>"
}}
"""

USER_TEMPLATE = """Instrucao-alvo: `{instruction}`

```rust
{code}
```"""


def load_knowledge_base() -> str:
    if not KB_PATH.exists():
        raise FileNotFoundError(f"Base de conhecimento nao encontrada: {KB_PATH}")
    text = KB_PATH.read_text(encoding="utf-8").strip()
    missing = [k for k in CATEGORIES if k not in text]
    if missing:
        raise ValueError(f"Base de conhecimento sem as chaves: {', '.join(missing)}")
    return text


def build_system_prompt() -> str:
    return SYSTEM_TEMPLATE.format(knowledge_base=load_knowledge_base(), keys=", ".join(CATEGORIES))


def prompt_fingerprint() -> dict:
    sp = build_system_prompt() + USER_TEMPLATE
    return {"prompt_version": PROMPT_VERSION, "prompt_sha256": hashlib.sha256(sp.encode()).hexdigest()[:16]}


def normalize(parsed: dict, target: str) -> dict:
    """Valida o JSON e separa achados validos dos descartados (com o motivo)."""
    kept, dropped = [], []
    for f in parsed.get("findings") or []:
        if not isinstance(f, dict):
            dropped.append({"finding": f, "reason": "formato invalido"})
            continue
        cat = str(f.get("category", "")).strip().upper()
        if cat not in CATEGORIES:
            dropped.append({"finding": f, "reason": f"categoria desconhecida: {cat!r}"})
            continue
        f["category"] = cat
        kept.append(f)
    return {
        "instruction": parsed.get("instruction", target),
        "findings": kept,
        "dropped": dropped,
        "summary": parsed.get("summary", ""),
        "predicted": sorted({f["category"] for f in kept}),
    }


def run_static_analysis(target_instruction: str, code: str, client=None) -> dict:
    system = build_system_prompt()
    user = USER_TEMPLATE.format(instruction=target_instruction, code=code)
    res: LLMResult = chat_json(system, user, client=client)
    record = {
        "llm": {"model": res.model, "prompt_tokens": res.prompt_tokens,
                "completion_tokens": res.completion_tokens, "latency_s": res.latency_s,
                "attempts": res.attempts},
        "raw": res.text,
    }
    try:
        record.update(normalize(parse_json(res.text), target_instruction))
        record["parse_error"] = None
    except (ValueError, TypeError) as e:
        record.update({"findings": [], "dropped": [], "predicted": [], "summary": "",
                       "parse_error": str(e)})
    return record
