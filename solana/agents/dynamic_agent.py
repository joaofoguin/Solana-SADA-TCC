"""
agents/dynamic_agent.py (SADA-Solana)

Agente de Analise Dinamica. Equivalente ao agents/dynamic_agent.py da EVM, que
chamava funcoes view/pure via Web3.py com parametros mock.

Alterado para Solana:
- Recebe um achado do Static Agent (categoria + hipotese de ataque) e o codigo
  sanitizado da instrucao.
- O LLM escreve um cenario Mollusk (Rust) sobre um harness pronto
  (dynamic/harness): uso legitimo ("baseline"), ataque ("attack") e condicoes de
  dano ("effect"). O cenario roda contra o .so compilado do programa.
- A decisao vem da execucao, nao do texto do LLM:
    confirmed      baseline com sucesso, ataque aceito e ao menos um efeito verdadeiro
                   (ou nenhum efeito registrado) em alguma tentativa;
    not_confirmed  houve cenario valido (baseline com sucesso) e em nenhuma
                   tentativa o ataque foi aceito com dano;
    inconclusive   nenhum cenario valido (erro de compilacao, baseline falhando,
                   panico) em todas as tentativas.
- Ate 5 tentativas; o LLM recebe de volta apenas erros de compilacao do proprio
  cenario e o resultado das execucoes (status e codigo de erro, com o nome dos
  erros genericos do Anchor). Ataque rejeitado tambem gera nova tentativa (o
  ataque pode ter sido mal montado); o LLM pode encerrar com "blocked". Os logs do
  programa (msg!) NUNCA voltam ao LLM: o binario foi compilado do codigo nao
  sanitizado e os logs revelariam o rotulo.

Protocolo: igual ao Static Agent. Prompt e harness so mudam com base no
Development Set; toda execucao registra versao e hash.
"""

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

from agents.llm import LLMResult, chat_json, parse_json

PROMPT_VERSION = "dynamic-v5.1"
MAX_ATTEMPTS = 5
MAX_TOKENS = 4000
HERE = Path(__file__).resolve().parents[1]  # ~/sada-tcc/solana
HARNESS = HERE / "dynamic" / "harness"
ATTEMPT_RS = HARNESS / "tests" / "attempt.rs"
CARGO_TIMEOUT_S = 600

CATEGORY_EFFECTS = {
    "SIGNER": "a operacao restrita foi executada sem a assinatura da autoridade (estado ou lamports alterados).",
    "OWNER": "uma conta forjada pelo atacante, com dono diferente do programa, foi aceita e usada.",
    "CPI": "o programa invocou um programa fornecido pelo atacante no lugar do esperado.",
    "PDA": ("uma conta com endereco diferente do PDA canonico foi aceita. Um endereco com bump nao canonico e "
            "Pubkey::create_program_address(&[seeds..., &[bump]], &env.program_id) com bump menor que o canonico "
            "(procure o primeiro bump abaixo do canonico para o qual a funcao retorna Ok)."),
    "SYSVAR": "uma conta forjada no lugar de um sysvar foi aceita.",
    "MATH": "um valor contabil deu a volta (overflow ou underflow) em vez de a instrucao falhar.",
    "COSPLAY": "uma conta de outro tipo foi aceita no lugar do tipo esperado.",
    "REINIT": "uma conta ja inicializada foi inicializada de novo e teve o estado sobrescrito.",
}

HARNESS_API = r"""
API DO HARNESS (crate dynamic_harness, ja importado com `use dynamic_harness::prelude::*;`):
  env.program_id: Pubkey                       program id do programa-alvo (ja carregado no Mollusk)
  env.attacker_program: Option<Pubkey>         programa do atacante, que aceita qualquer instrucao (pode ser None)
  env.anchor_ix(nome, &args, metas) -> Instruction
        instrucao Anchor: discriminador de `nome` + argumentos. `args` e qualquer valor serializavel em Borsh:
        um valor (&valor_u64), uma tupla na ordem dos parametros (&(bump_u8, valor_u64)) ou &() sem argumentos.
        Campos de tipos diferentes vao em TUPLA, nunca em array; nao use pares ("nome", valor).
        Use o nome da instrucao exatamente como aparece no codigo.
  env.raw_ix(&dados, metas) -> Instruction     instrucao com dados brutos (Rust nativo / Pinocchio); mesmos tipos de `args`
  env.baseline(nota, &ix, &contas) -> InstructionResult   uso legitimo; PRECISA ter sucesso
  env.attack(nota, &ix, &contas) -> InstructionResult     a tentativa de ataque (chame exatamente uma vez)
  env.effect(nota, bool)                        condicao sobre o estado depois do ataque que demonstra o dano
  anchor_account_data("Tipo", &(campo1, campo2, ...)) -> Vec<u8>
        dados de conta Anchor: discriminador do tipo + campos na ordem da struct (Pubkey, u64, bool, u8...).
  anchor_account_discriminator("Tipo") -> [u8; 8]
  account(&dono, &dados, Some(lamports) ou None) -> AccountSharedData   (None = minimo isento de aluguel)
  wallet(lamports) -> AccountSharedData         carteira (dono: System Program)
  empty_account() -> AccountSharedData          conta ainda nao criada (para `init`)
  system_program_account() -> (Pubkey, AccountSharedData)   passe-a quando a instrucao recebe o System Program
  program_account(&id) -> AccountSharedData     conta executavel de programa (ex.: para env.attacker_program)
  after(&resultado, &chave) -> &AccountSharedData   conta depois da execucao (.lamports(), .data(), .owner())
  read_u64(&dados, offset) -> u64 ; read_pubkey(&dados, offset) -> Pubkey
  resultado.resulting_accounts: Vec<(Pubkey, AccountSharedData)>   estado depois da execucao (use para encadear)
  resultado.program_result: ProgramResult      Success | Failure(ProgramError) | UnknownError(..)
  Serializacao (trait Fields): inteiros LE, bool = 1 byte, Pubkey = 32 bytes, Option<T>, tuplas e arrays fixos =
  campos concatenados; Vec<u8> e &[u8] entram como bytes ja serializados. valor.bytes() -> Vec<u8>.
  Tambem disponiveis: Pubkey::new_unique(), Pubkey::find_program_address, Pubkey::create_program_address,
  AccountMeta::new(chave, assina) (gravavel), AccountMeta::new_readonly(chave, assina).

  Notas:
  - Conta criada pela instrucao (constraint `init`): passe empty_account(), marque a nova conta como signer
    (se nao for PDA) e inclua system_program_account() nas contas e nos metas.
  - Conta Anchor que a instrucao recebe como Account<'info, T> SEM `init` precisa existir antes:
        account(&env.program_id, &anchor_account_data("T", &(campos...)), None)
    (passar empty_account() nesse caso gera AccountNotInitialized).
  - Apenas o harness e o solana_sdk (tambem acessivel como solana_program) estao disponiveis; nao ha anchor_lang.
  - Padrao para medir o efeito sem entrar em panico quando o ataque e rejeitado:
        let r = env.attack("...", &ix, &contas);
        if r.program_result == ProgramResult::Success {
            env.effect("...", read_u64(after(&r, &conta).data(), 40) == valor_esperado);
        }
"""

SYSTEM_TEMPLATE = """Voce e o componente de ANALISE DINAMICA de um sistema multiagente (SADA) que audita programas da blockchain Solana.

O Static Agent apontou uma possivel vulnerabilidade em uma instrucao. Sua tarefa e escrever um cenario de execucao no Mollusk (SVM em memoria) que tente explorar essa hipotese contra o binario compilado do programa. O resultado da execucao decide se a vulnerabilidade e confirmada; nao e a sua opiniao.

{harness_api}

O QUE O CENARIO DEVE FAZER:
1. Montar as contas como o programa espera encontra-las (layout dos dados, dono, PDAs com as mesmas seeds do codigo).
2. Chamar env.baseline com um uso LEGITIMO da instrucao-alvo (ou de outra instrucao do programa que prepare o estado). O baseline precisa ter sucesso: ele prova que o cenario esta montado corretamente. Se o ataque depende de um estado anterior (ex.: conta ja inicializada), produza esse estado com o baseline e use resultado.resulting_accounts.
3. Chamar env.attack exatamente uma vez, com a menor mudanca em relacao ao uso legitimo que realiza a hipotese de ataque.
   Para {category}, o harness so aceita o ataque como valido se {requirement} (compara com o baseline da mesma instrucao).
4. Depois do ataque, registrar com env.effect as condicoes que demonstram o dano, lendo o estado resultante com after(..). Para a categoria {category}, o dano esperado e: {effect}
   Se o ataque for rejeitado, nao tente ler o estado resultante (os efeitos podem simplesmente nao ser registrados).

REGRAS:
- Ataque a instrucao-alvo; nao altere o programa e nao simule o resultado.
- Nao use assert!, unwrap ou expect sobre resultados de execucao; o harness ja registra tudo.
- O efeito precisa ser uma comparacao real com o estado depois do ataque, nunca uma constante. Registre so condicoes
  que o ataque bem-sucedido torna verdadeiras; basta uma condicao verdadeira para demonstrar o dano.
- O efeito precisa ser algo que o uso legitimo nao produziria (ex.: o valor que a propria instrucao grava
  normalmente nao e dano).
- Escreva apenas o corpo da funcao de teste (ja existe `let env = Env::load();` antes dele).

FORMATO DE SAIDA (somente JSON valido):
{{
  "plan": "<2 a 4 frases: estado preparado, uso legitimo, ataque e efeito medido>",
  "scenario": "<corpo Rust da funcao de teste>"
}}
Somente quando uma tentativa anterior mostrou o ataque rejeitado e voce concluir que o programa de fato bloqueia
a hipotese (nao que o cenario estava errado), responda {{"conclusion": "blocked", "plan": "<por que>"}}.
"""

USER_TEMPLATE = """Instrucao-alvo: `{instruction}` (framework: {framework})

Achado do Static Agent:
- categoria: {category}
- evidencia: {evidence}
- explicacao: {explanation}
- hipotese de ataque: {attack_hypothesis}

Codigo do programa:
```rust
{code}
```"""

RETRY_TEMPLATE = """{base}

TENTATIVA ANTERIOR ({n} de {max}):
Cenario enviado:
```rust
{scenario}
```
Resultado: {problem}

Corrija o cenario (ou conclua "blocked", se for o caso) e devolva o JSON completo."""

TEST_FILE = """// Gerado pelo Dynamic Agent a cada tentativa. Nao editar.
#![allow(unused_imports, unused_variables, unused_mut, dead_code)]
use dynamic_harness::prelude::*;

#[test]
fn scenario() {{
    let env = Env::load();
    // ---- inicio do cenario gerado ----
{body}
    // ---- fim do cenario gerado ----
}}
"""

ANCHOR_ERRORS = {
    100: "InstructionMissing", 101: "InstructionFallbackNotFound", 102: "InstructionDidNotDeserialize",
    2000: "ConstraintMut", 2001: "ConstraintHasOne", 2002: "ConstraintSigner", 2003: "ConstraintRaw",
    2004: "ConstraintOwner", 2006: "ConstraintSeeds", 2012: "ConstraintAddress",
    3001: "AccountDiscriminatorNotFound", 3002: "AccountDiscriminatorMismatch", 3003: "AccountDidNotDeserialize",
    3005: "AccountNotEnoughKeys", 3006: "AccountNotMutable", 3007: "AccountOwnedByWrongProgram",
    3008: "InvalidProgramId", 3009: "InvalidProgramExecutable", 3010: "AccountNotSigner",
    3011: "AccountNotSystemOwned", 3012: "AccountNotInitialized", 3015: "AccountSysvarMismatch",
}


def explain(result: str) -> str:
    """Acrescenta o nome dos erros genericos do Anchor; erros >= 6000 sao do proprio programa."""
    m = re.search(r"Custom\((\d+)\)", result or "")
    if not m:
        return result
    code = int(m.group(1))
    if code in ANCHOR_ERRORS:
        return f"{result} = {ANCHOR_ERRORS[code]} (erro do Anchor)"
    if code >= 6000:
        return f"{result} = variante {code - 6000} do enum de erros do programa (#[error_code])"
    return result


RUNTIME_TRACE = re.compile(r"Program (\w{32,44}) (invoke \[\d+\]|success|failed: .*|consumed .*)$")


def build_system_prompt(category: str) -> str:
    return SYSTEM_TEMPLATE.format(harness_api=HARNESS_API, category=category,
                                  effect=CATEGORY_EFFECTS.get(category, "dano observavel no estado."),
                                  requirement=ATTACK_REQUIREMENT.get(category, "o ataque executar a hipotese"))


def prompt_fingerprint() -> dict:
    blob = SYSTEM_TEMPLATE + HARNESS_API + json.dumps(CATEGORY_EFFECTS, sort_keys=True) \
        + json.dumps(ATTACK_REQUIREMENT, sort_keys=True) + json.dumps(RUNTIME_ERRORS) + PROMPT_VERSION + USER_TEMPLATE \
        + RETRY_TEMPLATE + TEST_FILE + (HARNESS / "src" / "lib.rs").read_text(encoding="utf-8")
    return {"dynamic_prompt_version": PROMPT_VERSION,
            "dynamic_prompt_sha256": hashlib.sha256(blob.encode()).hexdigest()[:16]}


# ---------------------------------------------------------------------------
# Execucao de um cenario
# ---------------------------------------------------------------------------

def _compile_errors(stderr: str, limit: int = 40) -> str:
    """Somente os erros do cenario gerado (sem caminhos locais)."""
    out, keep = [], 0
    for line in stderr.splitlines():
        if line.startswith("error"):
            keep = 12
        if keep:
            out.append(line.replace(str(HARNESS), "harness"))
            keep -= 1
        if len(out) >= limit:
            break
    return "\n".join(out) or stderr[-2000:]


def execute_scenario(body: str, target: dict) -> dict:
    """Compila e roda o cenario. target: so_path, program_id, target_name, target_disc, attacker_so."""
    # normalizacao sintatica: `&[]` (lista vazia sem tipo) nao compila com a API generica; equivale a `&()`
    # (so nos argumentos de anchor_ix/raw_ix; em account(dono, &[], ..) a lista vazia ja e &[u8])
    body = re.sub(r'(anchor_ix\(\s*"[^"]*"\s*,\s*)&\[\s*\]', r"\1&()", body)
    body = re.sub(r"(raw_ix\(\s*)&\[\s*\]", r"\1&()", body)
    ATTEMPT_RS.parent.mkdir(parents=True, exist_ok=True)
    ATTEMPT_RS.write_text(TEST_FILE.format(body="\n".join("    " + ln for ln in body.splitlines())),
                          encoding="utf-8")
    env = {**os.environ,
           "DYN_SO_PATH": str(target["so_path"]),
           "DYN_PROGRAM_ID": target["program_id"],
           "DYN_TARGET_NAME": target["target_name"],
           "DYN_TARGET_DISC": target.get("target_disc") or "",
           "DYN_ATTACKER_SO": str(target.get("attacker_so") or ""),
           "RUST_BACKTRACE": "0"}
    t0 = time.monotonic()
    try:
        p = subprocess.run(["cargo", "test", "--manifest-path", str(HARNESS / "Cargo.toml"),
                            "--test", "attempt", "-q", "--", "--nocapture", "--test-threads=1"],
                           capture_output=True, text=True, env=env, timeout=CARGO_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"kind": "timeout", "events": [], "detail": "execucao excedeu o tempo limite"}
    elapsed = round(time.monotonic() - t0, 1)
    events = [json.loads(ln[6:]) for ln in p.stdout.splitlines() if ln.startswith("@@DYN ")]
    trace = [m.group(0) for ln in p.stderr.splitlines() if (m := RUNTIME_TRACE.search(ln))]
    if "could not compile" in p.stderr or "error[E" in p.stderr:
        return {"kind": "compile_error", "events": [], "detail": _compile_errors(p.stderr), "elapsed_s": elapsed}
    if not any(e["step"] == "setup" for e in events):
        raise RuntimeError("harness nao carregou o programa (verifique o .so e o program id):\n"
                           + (p.stdout + p.stderr)[-1500:])
    attacker = next(e["attacker_program"] for e in events if e["step"] == "setup")
    if attacker and any(f"Program {attacker} invoke" in t for t in trace):
        events.append({"step": "effect", "note": "programa do atacante foi invocado (rastro do runtime)",
                       "holds": True, "automatic": True})
    panic = next((ln for ln in (p.stdout + p.stderr).splitlines() if "panicked at" in ln), None)
    if panic:
        idx = (p.stdout + p.stderr).splitlines().index(panic)
        msg = " ".join((p.stdout + p.stderr).splitlines()[idx:idx + 2]).replace(str(HARNESS), "harness")
        return {"kind": "panic", "events": events, "detail": msg[:600], "runtime_trace": trace, "elapsed_s": elapsed}
    return {"kind": "ran", "events": events, "runtime_trace": trace, "elapsed_s": elapsed}


# O ataque precisa exercitar a categoria em relacao ao uso legitimo: compara, posicao a
# posicao, as contas do ataque com as de um baseline da mesma instrucao. Sem isso, uma
# chamada legitima com efeito normal (ex.: valor gravado) seria "confirmada".
ATTACK_REQUIREMENT = {
    "SIGNER": "uma conta que assina no baseline nao assina no ataque",
    "OWNER": "uma conta do ataque tem dono diferente da conta na mesma posicao do baseline",
    "COSPLAY": "uma conta do ataque tem discriminador (8 primeiros bytes) diferente da conta na mesma posicao do baseline",
    "PDA": "uma conta do ataque esta em endereco diferente da conta na mesma posicao do baseline",
    "SYSVAR": "uma conta do ataque esta em endereco diferente da conta na mesma posicao do baseline",
    "CPI": ("uma conta do ataque esta em endereco diferente da conta na mesma posicao do baseline "
            "(ex.: o programa do atacante no lugar do esperado)"),
    "REINIT": ("a instrucao do ataque seja a mesma do baseline e uma conta com dados chegue ao ataque com estado diferente "
               "do que tinha no baseline (ex.: o estado ja inicializado em resultado.resulting_accounts)"),
}


def _pair_holds(category: str, b: dict, a: dict) -> bool:
    ba, aa = b.get("accounts") or [], a.get("accounts") or []
    pairs = list(zip(ba, aa))
    if category == "SIGNER":
        return any(x["signer"] and not y["signer"] for x, y in pairs)
    if category == "OWNER":
        return any("?" not in (x["owner"], y["owner"]) and x["owner"] != y["owner"] for x, y in pairs)
    if category == "COSPLAY":
        return any(y["data_len"] > 0 and x["head"] != y["head"] for x, y in pairs)
    if category in ("PDA", "SYSVAR", "CPI"):
        return any(x["key"] != y["key"] for x, y in pairs)
    if category == "REINIT":
        return b.get("ix_head") == a.get("ix_head") and any(
            x["key"] == y["key"] and y["data_len"] > 0 and x["digest"] != y["digest"] for x, y in pairs)
    return True


def attack_exercises(category: str, baselines: list, attack: dict, attacker_invoked: bool = False) -> bool:
    if category not in ATTACK_REQUIREMENT or "accounts" not in attack:
        return True
    if category == "CPI" and attacker_invoked:
        return True
    same = [b for b in baselines if b.get("ix_head") == attack.get("ix_head")] or baselines
    return any(_pair_holds(category, b, attack) for b in same)


def _post_state(attack: dict) -> str:
    rows = [f"conta #{i} ({acc['key'][:8]}..): {len(acc['post']) // 2} bytes = {acc['post']}"
            for i, acc in enumerate(attack.get("accounts") or []) if acc.get("writable") and acc.get("post")]
    return ("\nEstado das contas gravaveis depois do ataque (hex, ate 256 bytes; confira os offsets):\n"
            + "\n".join(rows)) if rows else ""


# Erros do runtime (nao do programa): o programa aceitou a entrada e tentou uma operacao
# que a SVM proibe para qualquer programa (ex.: gravar em conta de outro dono). Isso nao e
# defesa do programa analisado, entao nao conta como rejeicao do ataque.
RUNTIME_ERRORS = ("ExternalAccountDataModified", "ExternalAccountLamportSpend", "ReadonlyDataModified",
                  "ReadonlyLamportChange", "ExecutableDataModified", "ExecutableLamportChange",
                  "ModifiedProgramId", "UnbalancedInstruction")


def judge(run: dict, category: str = "") -> tuple:
    """(verdict, motivo). verdict None = cenario invalido (nova tentativa). Regras fixas, sem LLM.
    'not_confirmed' tambem permite nova tentativa: o ataque pode ter sido mal montado."""
    if run["kind"] == "compile_error":
        return None, "erro de compilacao:\n" + run["detail"]
    if run["kind"] == "timeout":
        return None, run["detail"]
    ev = run["events"]
    baselines = [e for e in ev if e["step"] == "baseline"]
    attacks = [e for e in ev if e["step"] == "attack"]
    effects = [e for e in ev if e["step"] == "effect"]
    failed_base = [e for e in baselines if e["result"] != "Success"]
    if failed_base:
        b = failed_base[0]
        return None, (f"o baseline '{b['note']}' falhou com {explain(b['result'])}; o uso legitimo precisa ter "
                      "sucesso (revise layout das contas, seeds, flags de assinatura/escrita e argumentos)")
    if run["kind"] == "panic" and not attacks:
        return None, "o cenario entrou em panico antes do ataque: " + run["detail"]
    if not baselines:
        return None, "nenhum env.baseline foi executado antes do ataque"
    if len(attacks) != 1:
        return None, f"env.attack deve ser chamado exatamente uma vez (foi chamado {len(attacks)} vezes)"
    att = attacks[0]
    attacker_invoked = any(e["step"] == "effect" and e["note"].startswith("programa do atacante") for e in effects)
    if not attack_exercises(category, baselines, att, attacker_invoked):
        return None, (f"o ataque nao exercita a hipotese de {category}: e preciso que {ATTACK_REQUIREMENT[category]}. "
                      "Mantenha o baseline como uso legitimo e faca no ataque exatamente essa mudanca.")
    rt = next((e for e in RUNTIME_ERRORS if e in att["result"]), None)
    if rt:
        return None, (f"o ataque parou com {att['result']}, erro do runtime da Solana e nao do programa: o programa "
                      "aceitou a entrada e tentou uma operacao que nenhum programa pode fazer (ex.: gravar em conta "
                      "cujo dono e outro programa). Demonstre o dano por outra via, por exemplo uma decisao do "
                      "programa tomada a partir dos dados da conta forjada, gravada numa conta que pertence a ele.")
    if att["result"] != "Success":
        return "not_confirmed", f"baseline ok; ataque rejeitado: {explain(att['result'])}"
    if run["kind"] == "panic":
        return None, "o ataque foi aceito, mas o cenario entrou em panico ao medir o efeito: " + run["detail"]
    held = [e for e in effects if e["holds"]]
    if effects and not held:
        return "not_confirmed", ("ataque aceito, mas nenhuma condicao de dano foi verdadeira: "
                                 + "; ".join(e["note"] for e in effects) + _post_state(att))
    return "confirmed", "ataque aceito" + (" e dano verificado: " + "; ".join(e["note"] for e in held)
                                           if held else " (nenhum efeito registrado)")


def run_dynamic_analysis(case_ctx: dict, finding: dict, target: dict, client=None) -> dict:
    """case_ctx: instruction, framework, code. finding: achado do Static Agent."""
    category = finding["category"]
    system = build_system_prompt(category)
    base_user = USER_TEMPLATE.format(
        instruction=case_ctx["instruction"], framework=case_ctx["framework"], category=category,
        evidence=finding.get("evidence", ""), explanation=finding.get("explanation", ""),
        attack_hypothesis=finding.get("attack_hypothesis", ""), code=case_ctx["code"])
    user, attempts, final, reason, why, seen_rejection, seen_no_damage = base_user, [], None, "", "", None, None
    last_body, last_why, last_rejected = "", "", False
    for n in range(1, MAX_ATTEMPTS + 1):
        res: LLMResult = chat_json(system, user, client=client, max_tokens=MAX_TOKENS)
        rec = {"attempt": n, "llm": {"model": res.model, "prompt_tokens": res.prompt_tokens,
                                     "completion_tokens": res.completion_tokens, "latency_s": res.latency_s},
               "raw": res.text}
        try:
            out = parse_json(res.text)
            if out.get("conclusion") == "blocked" and not last_rejected:
                # "blocked" so vale depois de um ataque REJEITADO pelo programa; ataque aceito sem
                # dano medido indica efeito mal medido, nao bloqueio
                rec.update({"plan": str(out.get("plan", "")), "problem": "blocked sem ataque rejeitado"})
                attempts.append(rec)
                user = RETRY_TEMPLATE.format(
                    base=base_user, n=n, max=MAX_ATTEMPTS, scenario=last_body or "(nenhum)",
                    problem=(last_why + "\n\nVoce respondeu \"blocked\", mas o ultimo ataque valido nao foi rejeitado pelo programa: "
                             "ele foi ACEITO. Confira no estado acima se o dano ocorreu e corrija a medicao do efeito "
                             "(offsets e valores esperados)."))
                continue
            if out.get("conclusion") == "blocked":
                rec.update({"plan": str(out.get("plan", "")), "verdict": "not_confirmed",
                            "reason": "LLM concluiu que o programa bloqueia o ataque"})
                attempts.append(rec)
                final, reason = "not_confirmed", seen_rejection
                break
            body, plan = str(out["scenario"]), str(out.get("plan", ""))
        except (ValueError, KeyError, TypeError, AttributeError) as e:
            rec["problem"] = f"JSON invalido: {e}"
            attempts.append(rec)
            user = RETRY_TEMPLATE.format(base=base_user, n=n, max=MAX_ATTEMPTS, scenario="(nenhum)",
                                         problem="a resposta nao era o JSON pedido com as chaves plan e scenario")
            continue
        run = execute_scenario(body, target)
        verdict, why = judge(run, category)
        rec.update({"plan": plan, "scenario": body, "run": run, "verdict": verdict, "reason": why})
        attempts.append(rec)
        if verdict == "confirmed":
            final, reason = verdict, why
            break
        if verdict == "not_confirmed":
            last_rejected = not why.startswith("ataque aceito")
            if last_rejected:
                seen_rejection = why
            else:
                seen_no_damage = why
        if verdict is not None or not last_body:
            last_body, last_why = body, why
        user = RETRY_TEMPLATE.format(base=base_user, n=n, max=MAX_ATTEMPTS, scenario=body, problem=why)
    if final is None:
        # cenario valido com ataque rejeitado em alguma tentativa -> not_confirmed; nenhum valido -> inconclusive
        seen = seen_rejection or seen_no_damage
        final, reason = ("not_confirmed", seen) if seen else ("inconclusive", reason or why)
    last_run = next((a["run"] for a in reversed(attempts) if "run" in a), {})
    attack = next((e for e in last_run.get("events", []) if e["step"] == "attack"), None)
    return {
        "category": category,
        "verdict": final,
        "exploit_successful": final == "confirmed",
        "attack_result": attack["result"] if attack else None,
        "reason": reason,
        "attempts_used": len(attempts),
        "attempts": attempts,
    }
