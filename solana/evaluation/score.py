"""
evaluation/score.py (SADA-Solana)

Aplica as regras de pontuacao gravadas em dataset/ground_truth.json:
- caso vulneravel: TP se a categoria-alvo foi prevista; senao FN;
- caso seguro: FP se a categoria-alvo foi prevista; senao TN;
- categoria prevista que esta em other_known_issues: ignorada;
- categoria prevista fora da alvo e de other_known_issues: FP dessa categoria.
Metricas por categoria e globais, sempre com as contagens absolutas.
"""

from collections import defaultdict

KEY_TO_NAME = {
    "SIGNER": "Missing Signer Check",
    "OWNER": "Improper Owner Check",
    "CPI": "Arbitrary CPI",
    "PDA": "Improper PDA Validation / Canonicalization",
    "SYSVAR": "Sysvar Account Check",
    "MATH": "Integer Overflow / Underflow",
    "COSPLAY": "Type Cosplay",
    "REINIT": "Reinitialization Attacks",
}


def _prf(c):
    tp, fp, fn = c["TP"], c["FP"], c["FN"]
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f1 = 2 * p * r / (p + r) if p and r else (0.0 if p is not None and r is not None else None)
    return {**c, "precision": p, "recall": r, "f1": f1}


def score_case(case: dict, predicted_keys: list) -> dict:
    predicted = {KEY_TO_NAME[k] for k in predicted_keys if k in KEY_TO_NAME}
    target = case["target_category"]
    others = set(case["other_known_issues"])
    hit = target in predicted
    outcome = ("TP" if hit else "FN") if case["label"] == "vulnerable" else ("FP" if hit else "TN")
    extra_fp = sorted(predicted - {target} - others)
    ignored = sorted(predicted & others - {target})
    return {"outcome": outcome, "extra_fp": extra_fp, "ignored": ignored}


def aggregate(cases: list, per_case: dict) -> dict:
    by_cat = defaultdict(lambda: {"TP": 0, "FP": 0, "FN": 0, "TN": 0})
    for c in cases:
        r = per_case.get(c["id"])
        if r is None:
            continue
        by_cat[c["target_category"]][r["outcome"]] += 1
        for cat in r["extra_fp"]:
            by_cat[cat]["FP"] += 1
    total = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
    for v in by_cat.values():
        for k in total:
            total[k] += v[k]
    return {
        "global": _prf(total),
        "by_category": {k: _prf(v) for k, v in sorted(by_cat.items())},
        "cases_scored": sum(1 for c in cases if c["id"] in per_case),
    }


def fmt(x):
    return "  -  " if x is None else f"{x:.3f}"


def print_table(metrics: dict):
    print(f"\n{'categoria':45s}  TP  FP  FN  TN  prec   rec    F1")
    rows = list(metrics["by_category"].items()) + [("GLOBAL", metrics["global"])]
    for name, m in rows:
        print(f"{name:45s} {m['TP']:3d} {m['FP']:3d} {m['FN']:3d} {m['TN']:3d}  "
              f"{fmt(m['precision'])}  {fmt(m['recall'])}  {fmt(m['f1'])}")
