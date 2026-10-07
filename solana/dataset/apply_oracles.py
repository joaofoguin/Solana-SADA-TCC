#!/usr/bin/env python3
"""Le a saida do `cargo test` dos oraculos, confronta com o rotulo de cada caso
e grava dataset/oracle_results.json; depois regenera o ground_truth.json.

Uso: python3 apply_oracles.py <arquivo .out do cargo test>
"""
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent

# caso -> (teste de ataque, resultado esperado do ataque, testes de sanidade)
# O teste de ataque decide o rotulo: aceito => vulneravel; rejeitado => seguro.
S, P, H = "sealevel.rs", "pinocchio.rs", "hacks.rs"
MAP = {
    "SL-00-INS": (S, "sl_00_ins_attack", "Success", []),
    "SL-00-SEC": (S, "sl_00_sec_attack", "Err(MissingRequiredSignature)", ["sl_00_sec_sanity"]),
    "SL-00-REC": (S, "sl_00_rec_attack", "Err(Custom(3010) AccountNotSigner)", ["sl_00_rec_sanity"]),
    "SL-02-INS": (S, "sl_02_ins_attack", "Success", []),
    "SL-02-SEC": (S, "sl_02_sec_attack", "Err(InvalidAccountData)", ["sl_02_sec_sanity"]),
    "SL-02-REC": (S, "sl_02_rec_attack", "Err(Custom(3007) AccountOwnedByWrongProgram)", ["sl_02_rec_sanity"]),
    "SL-03-INS": (S, "sl_03_ins_attack", "Success", []),
    "SL-03-SEC": (S, "sl_03_sec_attack", "Err(InvalidAccountData)", ["sl_03_sec_sanity"]),
    "SL-03-REC": (S, "sl_03_rec_attack", "Err(Custom(3002) AccountDiscriminatorMismatch)", ["sl_03_rec_sanity"]),
    "SL-04-INS": (S, "sl_04_ins_attack", "Success", []),
    "SL-04-SEC": (S, "sl_04_sec_attack", "Success (reinicializacao aceita)", ["sl_04_sec_first_init_blocked"]),
    "SL-04-REC": (S, "sl_04_rec_attack", "Err(qualquer)", ["sl_04_rec_sanity"]),
    "SL-05-INS": (S, "sl_05_ins_attack", "Err(IncorrectProgramId) no construtor spl_token antes do CPI", []),
    "SL-05-RAW": (S, "sl_05_raw_attack", "Success (programa arbitrario invocado)", []),
    "SL-05-SEC": (S, "sl_05_sec_attack", "Err(IncorrectProgramId)", []),
    "SL-05-REC": (S, "sl_05_rec_attack", "Err(Custom(3008) InvalidProgramId)", []),
    "SL-07-INS": (S, "sl_07_ins_attack", "Success", []),
    "SL-07-SEC": (S, "sl_07_sec_attack", "Err(InvalidArgument)", ["sl_07_sec_sanity"]),
    "SL-07-REC": (S, "sl_07_rec_attack", "Err(Custom(2006) ConstraintSeeds)", ["sl_07_rec_sanity"]),
    "SL-10-INS": (S, "sl_10_ins_attack", "Success", []),
    "SL-10-SEC": (S, "sl_10_sec_attack", "Err(Custom(2501) RequireEqViolated)", ["sl_10_sec_sanity"]),
    "SL-10-REC": (S, "sl_10_rec_attack", "Err(Custom(3015) AccountSysvarMismatch)", ["sl_10_rec_sanity"]),
    "SSP-01-P-V": (P, "ssp_01_p_v_attack", "Success", []),
    "SSP-01-P-S": (P, "ssp_01_p_s_attack", "Err(Custom(1001))", ["ssp_01_p_s_sanity"]),
    "SSP-02-P-V": (P, "ssp_02_p_v_attack", "Success", []),
    "SSP-02-P-S": (P, "ssp_02_p_s_attack", "Err(Custom(2001))", ["ssp_02_p_s_sanity"]),
    "SSP-03-P-V1": (P, "ssp_03_p_v1_attack", "Success", []),
    "SSP-03-P-V2": (P, "ssp_03_p_v2_attack", "Success", []),
    "SSP-03-P-S1": (P, "ssp_03_p_s1_attack", "Err(Custom(3001))", ["ssp_03_p_s1_sanity"]),
    "SSP-03-P-S2": (P, "ssp_03_p_s2_attack", "Err(Custom(3002))", ["ssp_03_p_s2_sanity"]),
    "SSP-04-P-V": (P, "ssp_04_p_v_attack", "Success", []),
    "SSP-04-P-S": (P, "ssp_04_p_s_attack", "Err(Custom(4001))", ["ssp_04_p_s_sanity"]),
    "SSP-05-P-V": (P, "ssp_05_p_v_attack", "Success", []),
    "SSP-05-P-S": (P, "ssp_05_p_s_attack", "Err(Custom(5002))", ["ssp_05_p_s_sanity"]),
    "SSP-06-P-V": (P, "ssp_06_p_v_attack", "Success", []),
    "SSP-06-P-S": (P, "ssp_06_p_s_attack", "Err(Custom(6002))", ["ssp_06_p_s_sanity"]),
    "HK-REINIT-V": (H, "hk_reinit_attack", "Success", []),
}


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1]).resolve()
    status = {}
    for m in re.finditer(r"^test (\S+) \.\.\. (ok|FAILED|ignored)", out.read_text(errors="replace"), re.M):
        status[m.group(1)] = m.group(2)

    gt = json.loads((HERE / "ground_truth.json").read_text(encoding="utf-8"))
    labels = {c["id"]: c["label"] for c in gt["cases"]}
    try:
        log_rel = str(out.relative_to(HERE.parent))
    except ValueError:
        log_rel = str(out)

    results, problems = {}, 0
    print(f"\n{'caso':13s} {'rotulo':10s} {'ataque':8s} {'sanidade':9s} veredito")
    for cid, (fname, attack, expected, sanity) in MAP.items():
        a = status.get(attack, "AUSENTE")
        s_all = [status.get(t, "AUSENTE") for t in sanity]
        s_ok = all(x == "ok" for x in s_all)
        verified = a == "ok" and s_ok
        if verified:
            verdict = "CONFIRMADO"
        elif a == "AUSENTE":
            verdict = "TESTE NAO EXECUTADO"
        elif a != "ok":
            verdict = "DIVERGENCIA: o ataque nao teve o efeito esperado; revisar rotulo ou teste"
        else:
            verdict = "SANIDADE FALHOU: rejeicao pode ser por motivo errado"
        if not verified:
            problems += 1
        s_txt = "-" if not sanity else ("ok" if s_ok else "/".join(s_all))
        print(f"{cid:13s} {labels.get(cid, '?'):10s} {a:8s} {s_txt:9s} {verdict}")
        results[cid] = {
            "reference_test": f"oracle_tests/tests/{fname}::{attack}",
            "sanity_tests": [f"oracle_tests/tests/{fname}::{t}" for t in sanity],
            "expected_status": expected,
            "verified": verified,
            "date": date.today().isoformat(),
            "log": log_rel,
        }

    (HERE / "oracle_results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"\n{len(MAP) - problems}/{len(MAP)} casos confirmados; {problems} para revisar.")
    subprocess.run([sys.executable, str(HERE / "gen_ground_truth.py")], check=True)


if __name__ == "__main__":
    main()
