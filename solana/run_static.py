#!/usr/bin/env python3
"""
run_static.py (SADA-Solana)

Executa o Static Agent sobre os casos sanitizados de um split e calcula as
metricas pelas regras do ground_truth.json.

Uso:
  python run_static.py --split development                  # nova execucao
  python run_static.py --split development --run-id <id>    # retoma uma execucao
  python run_static.py --split development --cases SSP-01-A-V SSP-01-A-S
  python run_static.py --split evaluation --final           # SO na execucao final

Cada caso fica salvo em evaluation/runs/<run_id>/static/<caso>.json assim que
termina; ao retomar, os casos ja salvos nao sao reenviados ao LLM.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent  # ~/sada-tcc/solana
sys.path.insert(0, str(HERE))

from agents.llm import DailyLimitReached, describe  # noqa: E402
from agents.static_agent import prompt_fingerprint, run_static_analysis  # noqa: E402
from evaluation.score import aggregate, print_table, score_case  # noqa: E402

DATASET = HERE / "dataset"
RUNS = HERE / "evaluation" / "runs"


def main(argv=None, client=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["development", "evaluation"], required=True)
    ap.add_argument("--run-id")
    ap.add_argument("--cases", nargs="*")
    ap.add_argument("--final", action="store_true", help="obrigatorio para o Evaluation Set")
    a = ap.parse_args(argv)

    if a.split == "evaluation" and not a.final:
        sys.exit("Evaluation Set so roda com --final (execucao unica, apos congelar o prompt).")

    gt = json.loads((DATASET / "ground_truth.json").read_text(encoding="utf-8"))
    manifest = {m["id"]: m for m in json.loads((DATASET / "sanitized" / "manifest.json").read_text())}
    cases = [c for c in gt["cases"] if c["split"] == a.split and (not a.cases or c["id"] in a.cases)]
    if not cases:
        sys.exit("Nenhum caso selecionado.")

    run_id = a.run_id or f"{datetime.now():%Y%m%d_%H%M}_static_{a.split}"
    out = RUNS / run_id / "static"
    out.mkdir(parents=True, exist_ok=True)
    meta_path = RUNS / run_id / "run_meta.json"
    fp = {**prompt_fingerprint(), **describe()}
    if meta_path.exists():
        old = json.loads(meta_path.read_text())
        for k in ("prompt_sha256", "llm_model", "llm_base_url", "llm_extra_body"):
            if old.get(k) != fp[k]:
                sys.exit(f"{k} mudou desde o inicio da execucao {run_id}; use um novo --run-id.")
    else:
        meta_path.write_text(json.dumps({**fp, "split": a.split, "started": datetime.now().isoformat(),
                                         "ground_truth_version": gt["version"]}, indent=2))

    print(f"Execucao {run_id} | {fp['llm_model']} | {fp['prompt_version']} ({fp['prompt_sha256']}) | {len(cases)} casos")
    per_case, tokens = {}, 0
    for i, c in enumerate(cases, 1):
        f = out / f"{c['id']}.json"
        if f.exists():
            rec = json.loads(f.read_text())
            status = "cache"
        else:
            m = manifest[c["id"]]
            code = (DATASET / m["file"]).read_text(encoding="utf-8")
            try:
                rec = run_static_analysis(m["target_instruction"], code, client=client)
            except DailyLimitReached as e:
                print(f"\nCota diaria esgotada ({e}). Retome depois com:\n"
                      f"  python run_static.py --split {a.split} --run-id {run_id}")
                break
            rec["case_id"] = c["id"]
            f.write_text(json.dumps(rec, indent=2, ensure_ascii=False))
            tokens += rec["llm"]["prompt_tokens"] + rec["llm"]["completion_tokens"]
            status = "novo "
        r = score_case(c, rec["predicted"])
        per_case[c["id"]] = r
        extra = f" extra_FP={r['extra_fp']}" if r["extra_fp"] else ""
        perr = "  [JSON INVALIDO]" if rec.get("parse_error") else ""
        print(f"[{i:2d}/{len(cases)}] {status} {c['id']:12s} {c['label']:10s} -> {r['outcome']}  "
              f"previsto={rec['predicted'] or '-'}{extra}{perr}")

    metrics = aggregate(cases, per_case)
    metrics.update({"run_id": run_id, **fp, "tokens_this_session": tokens})
    (RUNS / run_id / "metrics_static.json").write_text(json.dumps(metrics, indent=2))
    print_table(metrics)
    print(f"\n{metrics['cases_scored']}/{len(cases)} casos pontuados | tokens nesta sessao: {tokens}")
    print(f"Resultados: {RUNS / run_id}")
    return metrics


if __name__ == "__main__":
    main()
