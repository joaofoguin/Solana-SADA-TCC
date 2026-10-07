#!/usr/bin/env python3
"""Gera dataset/ground_truth.json do SADA-Solana (51 casos).

Unidade de analise: uma instrucao (handler) de um programa.
Regra de rotulo: o rotulo vem do comportamento verificado, nao do nome da pasta.
"""
import json
from pathlib import Path

CAT = {
    "SIGNER": "Missing Signer Check",
    "OWNER": "Improper Owner Check",
    "CPI": "Arbitrary CPI",
    "PDA": "Improper PDA Validation / Canonicalization",
    "SYSVAR": "Sysvar Account Check",
    "MATH": "Integer Overflow / Underflow",
    "COSPLAY": "Type Cosplay",
    "REINIT": "Reinitialization Attacks",
}

SOURCES = {
    "ssp": {"name": "Solana Security Patterns",
            "repo": "justFiveDev/solana-security-pattern",
            "commit": "a128ce9ceacadda7bb8ed686ce6a694439277dc5"},
    "sealevel": {"name": "Sealevel Attacks",
                 "repo": "coral-xyz/sealevel-attacks",
                 "commit": "24555d044802db4022112a94d6d70e74291a4b6d"},
    "hacks": {"name": "Solana Hacks",
              "repo": "El-Merovingio/solana-hacks",
              "commit": "7a0bebc9f40591eeb7e273ce57d166c759ec0d7f"},
}

cases = []


def add(id_, source, framework, path, instruction, label, cat, split,
        drop=(), other=(), evidence=None, notes="", ported_path=None, authored_by_student=False):
    c = {
        "id": id_,
        "source": SOURCES[source]["name"],
        "source_key": source,
        "repo": SOURCES[source]["repo"],
        "commit": SOURCES[source]["commit"],
        "framework": framework,
        "program_path": path,
        "ported_path": ported_path,          # relativo a dataset/; None = usa o original
        "instruction": instruction,
        "label": label,                      # vulnerable | secure
        "target_category": CAT[cat],
        "other_known_issues": [CAT[o] for o in other],
        "split": split,                      # development | evaluation
        "sanitize": {"drop_items": list(drop)},
        "evidence": evidence or {"type": "oracle_pending",
                                 "reference_test": None,
                                 "expected_status": None,
                                 "verified": False},
        "notes": notes,
        "authored_by_student": authored_by_student,
    }
    cases.append(c)


def ssp_ev(test, status):
    return {"type": "mollusk_reference_test",
            "reference_test": test,
            "expected_status": status,
            "verified": True,
            "verified_on": "2026-10-06",
            "log": "docs/coleta_2026-10-06/"}


def oracle(status_hint):
    return {"type": "oracle_pending", "reference_test": None,
            "expected_status": status_hint, "verified": False}


# ---------------------------------------------------------------------------
# DEVELOPMENT: Solana Security Patterns (Anchor) - verificados com Mollusk
# ---------------------------------------------------------------------------
P = "patterns/{}/anchor/src/lib.rs"
T = "patterns/{}/tests/tests/exploit.rs::{}"

d = "01-missing-signer-check"
add("SSP-01-A-V", "ssp", "anchor", P.format(d), "withdraw_vulnerable", "vulnerable", "SIGNER", "development",
    drop=["withdraw_secure", "WithdrawSecure"], evidence=ssp_ev(T.format(d, "exploit_withdraw_without_signer"), "Success"))
add("SSP-01-A-S", "ssp", "anchor", P.format(d), "withdraw_secure", "secure", "SIGNER", "development",
    drop=["withdraw_vulnerable", "WithdrawVulnerable"], evidence=ssp_ev(T.format(d, "secure_rejects_unsigned_withdraw"), "Custom(3010)"))

d = "02-missing-owner-check"
add("SSP-02-A-V", "ssp", "anchor", P.format(d), "process_vulnerable", "vulnerable", "OWNER", "development",
    drop=["process_secure", "ProcessSecure"], other=["COSPLAY"],
    evidence=ssp_ev(T.format(d, "exploit_fake_account_accepted"), "Success"),
    notes="Le bytes de AccountInfo sem verificar owner nem discriminator.")
add("SSP-02-A-S", "ssp", "anchor", P.format(d), "process_secure", "secure", "OWNER", "development",
    drop=["process_vulnerable", "ProcessVulnerable"], evidence=ssp_ev(T.format(d, "secure_rejects_fake_account"), "Custom(3007)"))

d = "03-integer-overflow"
add("SSP-03-A-V1", "ssp", "anchor", P.format(d), "mint_vulnerable", "vulnerable", "MATH", "development",
    drop=["burn_vulnerable", "mint_secure", "burn_secure"], evidence=ssp_ev(T.format(d, "exploit_overflow_supply_wraps_to_zero"), "Success"))
add("SSP-03-A-V2", "ssp", "anchor", P.format(d), "burn_vulnerable", "vulnerable", "MATH", "development",
    drop=["mint_vulnerable", "mint_secure", "burn_secure"], evidence=ssp_ev(T.format(d, "exploit_underflow_balance_wraps_to_max"), "Success"))
add("SSP-03-A-S1", "ssp", "anchor", P.format(d), "mint_secure", "secure", "MATH", "development",
    drop=["mint_vulnerable", "burn_vulnerable", "burn_secure"], evidence=ssp_ev(T.format(d, "secure_blocks_overflow"), "Custom(6000)"))
add("SSP-03-A-S2", "ssp", "anchor", P.format(d), "burn_secure", "secure", "MATH", "development",
    drop=["mint_vulnerable", "burn_vulnerable", "mint_secure"], evidence=ssp_ev(T.format(d, "secure_blocks_underflow"), "Custom(6001)"))

d = "04-reinitialization-attack"
add("SSP-04-A-V", "ssp", "anchor", P.format(d), "init_vulnerable", "vulnerable", "REINIT", "development",
    drop=["init_secure", "InitSecure", "init_anchor_native", "InitAnchorNative"],
    evidence=ssp_ev(T.format(d, "exploit_reinit_overwrites_authority"), "Success"))
add("SSP-04-A-S", "ssp", "anchor", P.format(d), "init_secure", "secure", "REINIT", "development",
    drop=["init_vulnerable", "InitVulnerable", "init_anchor_native", "InitAnchorNative"],
    evidence=ssp_ev(T.format(d, "secure_blocks_reinit"), "Custom(6000)"))
add("SSP-04-A-S2", "ssp", "anchor", P.format(d), "init_anchor_native", "secure", "REINIT", "development",
    drop=["init_vulnerable", "InitVulnerable", "init_secure", "InitSecure"],
    evidence={"type": "static_only", "reference_test": None, "expected_status": None, "verified": False},
    notes="Constraint init do Anchor; sem teste Mollusk na fonte.")

d = "05-pda-bump-canonicalization"
add("SSP-05-A-V", "ssp", "anchor", P.format(d), "set_value_vulnerable", "vulnerable", "PDA", "development",
    drop=["set_value_secure", "SetValueSecure"], evidence=ssp_ev(T.format(d, "exploit_non_canonical_bump_accepted"), "Success"))
add("SSP-05-A-S", "ssp", "anchor", P.format(d), "set_value_secure", "secure", "PDA", "development",
    drop=["set_value_vulnerable", "SetValueVulnerable"], evidence=ssp_ev(T.format(d, "secure_rejects_non_canonical_bump"), "Custom(6001)"))

d = "06-type-cosplay"
add("SSP-06-A-V", "ssp", "anchor", P.format(d), "update_fee_vulnerable", "vulnerable", "COSPLAY", "development",
    drop=["update_fee_secure", "UpdateFeeSecure"], other=["OWNER"],
    evidence=ssp_ev(T.format(d, "exploit_type_cosplay_accepted"), "Success"),
    notes="UncheckedAccount sem verificacao de owner (escrita mitigada pelo runtime).")
add("SSP-06-A-S", "ssp", "anchor", P.format(d), "update_fee_secure", "secure", "COSPLAY", "development",
    drop=["update_fee_vulnerable", "UpdateFeeVulnerable"], evidence=ssp_ev(T.format(d, "secure_rejects_wrong_discriminator"), "Custom(3002)"))

# ---------------------------------------------------------------------------
# EVALUATION: Sealevel Attacks (Anchor 0.20/0.25 -> portar)
# ---------------------------------------------------------------------------
S = "programs/{}/{}/src/lib.rs"
PORT = "Requer port para Anchor atual (docs/ports/)."


def sl(id_, prog, variant, ins, label, cat, hint, other=(), notes=""):
    add(id_, "sealevel", "anchor", S.format(prog, variant), ins, label, cat, "evaluation",
        other=other, evidence=oracle(hint), notes=(notes + " " + PORT).strip(),
        ported_path=f"programs/sealevel/{id_.lower().replace('-', '_')}/src/lib.rs")


sl("SL-00-INS", "0-signer-authorization", "insecure", "log_message", "vulnerable", "SIGNER", "Success")
sl("SL-00-SEC", "0-signer-authorization", "secure", "log_message", "secure", "SIGNER", "Failure: MissingRequiredSignature")
sl("SL-00-REC", "0-signer-authorization", "recommended", "log_message", "secure", "SIGNER", "Failure: AccountNotSigner")
sl("SL-02-INS", "2-owner-checks", "insecure", "log_message", "vulnerable", "OWNER", "Success")
sl("SL-02-SEC", "2-owner-checks", "secure", "log_message", "secure", "OWNER", "Failure: InvalidAccountData")
sl("SL-02-REC", "2-owner-checks", "recommended", "log_message", "secure", "OWNER", "Failure: AccountOwnedByWrongProgram")
sl("SL-03-INS", "3-type-cosplay", "insecure", "update_user", "vulnerable", "COSPLAY", "Success",
   notes="Verifica owner mas nao o tipo: separa Cosplay de Owner.")
sl("SL-03-SEC", "3-type-cosplay", "secure", "update_user", "secure", "COSPLAY", "Failure: InvalidAccountData")
sl("SL-03-REC", "3-type-cosplay", "recommended", "update_user", "secure", "COSPLAY", "Failure: AccountDiscriminatorMismatch")
sl("SL-04-INS", "4-initialization", "insecure", "initialize", "vulnerable", "REINIT", "Success")
sl("SL-04-SEC", "4-initialization", "secure", "initialize", "vulnerable", "REINIT", "Success (reinit aceito)",
   notes="DIVERGE DA FONTE: pasta 'secure', mas a condicao '!user.discriminator' esta invertida; "
         "bloqueia a 1a inicializacao e permite reinicializar. Commit 4bd537c dizia corrigir, HEAD ainda invertido.")
sl("SL-04-REC", "4-initialization", "recommended", "init", "secure", "REINIT", "Failure: account already in use")
sl("SL-05-INS", "5-arbitrary-cpi", "insecure", "cpi", "secure", "CPI", "Failure: IncorrectProgramId",
   notes="DIVERGE DA FONTE: pasta 'insecure', mas spl_token::instruction::transfer valida o program id "
         "(check_program_account) e o CPI arbitrario e rejeitado antes de acontecer. Mitigado pela biblioteca.")
add("SL-05-RAW", "sealevel", "anchor", S.format("5-arbitrary-cpi", "insecure"), "cpi", "vulnerable", "CPI",
    "evaluation", evidence=oracle("Success (programa arbitrario invocado)"),
    ported_path="programs/sealevel/sl_05_raw/src/lib.rs", authored_by_student=True,
    notes="Construido pelo autor a partir de SL-05-INS: instrucao montada manualmente, sem o construtor "
          "da biblioteca. Unico caso vulneravel de Arbitrary CPI com execucao confirmada.")
sl("SL-05-SEC", "5-arbitrary-cpi", "secure", "cpi_secure", "secure", "CPI", "Failure: IncorrectProgramId")
sl("SL-05-REC", "5-arbitrary-cpi", "recommended", "cpi", "secure", "CPI", "Failure: InvalidProgramId")
sl("SL-07-INS", "7-bump-seed-canonicalization", "insecure", "set_value", "vulnerable", "PDA", "Success",
   other=["SIGNER"], notes="Sem controle de acesso em nenhuma variante.")
sl("SL-07-SEC", "7-bump-seed-canonicalization", "secure", "set_value_secure", "secure", "PDA", "Failure: InvalidArgument",
   other=["SIGNER"], notes="Sem controle de acesso em nenhuma variante.")
sl("SL-07-REC", "7-bump-seed-canonicalization", "recommended", "set_value", "secure", "PDA", "Failure: ConstraintSeeds",
   other=["SIGNER"], notes="Sem controle de acesso em nenhuma variante.")
sl("SL-10-INS", "10-sysvar-address-checking", "insecure", "check_sysvar_address", "vulnerable", "SYSVAR", "Success")
sl("SL-10-SEC", "10-sysvar-address-checking", "secure", "check_sysvar_address", "secure", "SYSVAR", "Failure: RequireEqViolated")
sl("SL-10-REC", "10-sysvar-address-checking", "recommended", "check_sysvar_address", "secure", "SYSVAR", "Failure: AccountSysvarMismatch")

# ---------------------------------------------------------------------------
# EVALUATION: Solana Security Patterns (Pinocchio) - compilar a partir de copia
# ---------------------------------------------------------------------------
Q = "patterns/{}/pinocchio/src/lib.rs"


def pq(id_, d, ins, label, cat, drop, hint, other=()):
    add(id_, "ssp", "pinocchio", Q.format(d), ins, label, cat, "evaluation",
        drop=drop, other=other, evidence=oracle(hint),
        notes="Sem teste na fonte; oraculo a escrever. Compilar a partir de copia em dataset/programs/.")


pq("SSP-01-P-V", "01-missing-signer-check", "withdraw_vulnerable", "vulnerable", "SIGNER",
   ["withdraw_secure"], "Success")
pq("SSP-01-P-S", "01-missing-signer-check", "withdraw_secure", "secure", "SIGNER",
   ["withdraw_vulnerable"], "Failure: Custom(1001)")
pq("SSP-02-P-V", "02-missing-owner-check", "process_vulnerable", "vulnerable", "OWNER",
   ["process_secure"], "Success", other=["COSPLAY"])
pq("SSP-02-P-S", "02-missing-owner-check", "process_secure", "secure", "OWNER",
   ["process_vulnerable"], "Failure: Custom(2001)")
pq("SSP-03-P-V1", "03-integer-overflow", "mint_vulnerable", "vulnerable", "MATH",
   ["burn_vulnerable", "mint_secure", "burn_secure"], "Success", other=["SIGNER"])
pq("SSP-03-P-V2", "03-integer-overflow", "burn_vulnerable", "vulnerable", "MATH",
   ["mint_vulnerable", "mint_secure", "burn_secure"], "Success", other=["SIGNER"])
pq("SSP-03-P-S1", "03-integer-overflow", "mint_secure", "secure", "MATH",
   ["mint_vulnerable", "burn_vulnerable", "burn_secure"], "Failure: Custom(3001)", other=["SIGNER"])
pq("SSP-03-P-S2", "03-integer-overflow", "burn_secure", "secure", "MATH",
   ["mint_vulnerable", "burn_vulnerable", "mint_secure"], "Failure: Custom(3002)", other=["SIGNER"])
pq("SSP-04-P-V", "04-reinitialization-attack", "init_vulnerable", "vulnerable", "REINIT",
   ["init_secure"], "Success", other=["SIGNER"])
pq("SSP-04-P-S", "04-reinitialization-attack", "init_secure", "secure", "REINIT",
   ["init_vulnerable"], "Failure: Custom(4001)", other=["SIGNER"])
pq("SSP-05-P-V", "05-pda-bump-canonicalization", "set_value_vulnerable", "vulnerable", "PDA",
   ["set_value_secure"], "Success", other=["SIGNER"])
pq("SSP-05-P-S", "05-pda-bump-canonicalization", "set_value_secure", "secure", "PDA",
   ["set_value_vulnerable"], "Failure: Custom(5002)", other=["SIGNER"])
pq("SSP-06-P-V", "06-type-cosplay", "update_fee_vulnerable", "vulnerable", "COSPLAY",
   ["update_fee_secure"], "Success")
pq("SSP-06-P-S", "06-type-cosplay", "update_fee_secure", "secure", "COSPLAY",
   ["update_fee_vulnerable"], "Failure: Custom(6002)")

# ---------------------------------------------------------------------------
# EVALUATION: Solana Hacks
# ---------------------------------------------------------------------------
add("HK-REINIT-V", "hacks", "native", "reinitialization/reinit-attack/src/lib.rs", "initialize",
    "vulnerable", "REINIT", "evaluation", other=["SIGNER"], evidence=oracle("Success"),
    notes="PoC original usa validator local; oraculo Mollusk a escrever. Port solana-program 1.15 -> 2.1.",
    ported_path="programs/hacks/hk_reinit/src/lib.rs")

# ---------------------------------------------------------------------------
excluded = [
    {"source": "Solana Hacks", "path": "bump-seed-canonicalization",
     "reason": "Nao ha parametro bump; o PoC demonstra ausencia de controle de acesso em modify_acc, "
               "nao canonicalizacao. Mantido apenas para analise qualitativa."},
    {"source": "Solana Hacks", "path": "cosplay",
     "reason": "Confusao entre enums sem discriminator; o PoC desserializa conta zerada e nao demonstra "
               "a confusao de tipos. Mantido apenas para analise qualitativa."},
    {"source": "Solana Hacks", "path": "account-data-match",
     "reason": "Duplicate Mutable Accounts; fora das 8 categorias."},
    {"source": "Sealevel Attacks", "path": "programs/8-pda-sharing",
     "reason": "PDA Sharing (seeds pouco especificas) nao e canonicalizacao nem validacao de PDA de entrada; "
               "codigo incompleto por design."},
    {"source": "Sealevel Attacks", "path": "programs/1,6,9",
     "reason": "account-data-matching, duplicate-mutable-accounts, closing-accounts: fora das 8 categorias."},
]

# resultados dos testes-oraculo (gerados por apply_oracles.py), se existirem
_orc = Path(__file__).resolve().parent / "oracle_results.json"
if _orc.exists():
    _res = json.loads(_orc.read_text(encoding="utf-8"))
    for c in cases:
        r = _res.get(c["id"])
        if r:
            c["evidence"] = {"type": "mollusk_oracle_test",
                             "reference_test": r["reference_test"],
                             "sanity_tests": r["sanity_tests"],
                             "expected_status": r["expected_status"],
                             "verified": r["verified"],
                             "verified_on": r["date"],
                             "log": r["log"]}

doc = {
    "version": "1.3",
    "created": "2026-10-06",
    "unit_of_analysis": "instruction",
    "categories": list(CAT.values()),
    "scoring_rules": {
        "target_only": "Cada caso e avaliado somente na target_category.",
        "vulnerable_case": "TP se o sistema reporta a target_category; FN caso contrario.",
        "secure_case": "FP se o sistema reporta a target_category; TN caso contrario.",
        "other_known_issues": "Predicao de uma categoria listada em other_known_issues e ignorada (nem TP nem FP).",
        "other_wrong_category": "Predicao de categoria fora de target e de other_known_issues conta como FP.",
        "frozen_after": "2026-10-26",
    },
    "sources": SOURCES,
    "cases": cases,
    "excluded": excluded,
}

out = Path(__file__).resolve().parent / "ground_truth.json"
out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# resumo
from collections import Counter
cnt = Counter((c["split"], c["label"]) for c in cases)
print(f"{len(cases)} casos -> {out}")
for k in sorted(cnt):
    print(f"  {k[0]:12s} {k[1]:10s} {cnt[k]}")
cov = {}
for c in cases:
    cov.setdefault(c["split"], set()).add(c["target_category"])
for s, cats in cov.items():
    print(f"  cobertura {s}: {len(cats)}/8")
ver = sum(1 for c in cases if c["evidence"].get("verified"))
print(f"  rotulos verificados por execucao: {ver}/{len(cases)}")
ids = [c["id"] for c in cases]
assert len(ids) == len(set(ids)), "IDs duplicados"
