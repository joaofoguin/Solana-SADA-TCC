#!/usr/bin/env python3
"""
run_synthesis.py (SADA-Solana)

Executa o Synthesis Agent sobre uma execucao do Static e a execucao do Dynamic
feita sobre ela, e calcula as metricas das quatro configuracoes comparadas:

  static_only          achados do Static Agent
  rule_keep_confirmed  Static + Dynamic: so os confirmados pela execucao
  rule_drop_refuted    Static + Dynamic: tudo menos os refutados (not_confirmed)
  pipeline             Static + Dynamic + Synthesis (decisao do Synthesis Agent)

As duas regras fixas servem de referencia para saber o que o Synthesis acrescenta
em relacao a uma decisao mecanica.

Uso:
  python run_synthesis.py --split development --static-run <id> --dynamic-run <id>
  python run_synthesis.py --split evaluation --static-run <id> --dynamic-run <id> --final

Cada caso fica em evaluation/runs/<run_id>/synthesis/<caso>.json (decisao) e
<caso>.md (relatorio consolidado legivel).
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent  # ~/sada-tcc/solana
sys.path.insert(0, str(HERE))

from agents.llm import DailyLimitReached, describe  # noqa: E402
from agents.synthesis_agent import prompt_fingerprint, render_markdown, run_synthesis  # noqa: E402
from evaluation.score import aggregate, print_table, score_case  # noqa: E402

DATASET = HERE / "dataset"
RUNS = HERE / "evaluation" / "runs"
CONFIGS = ("static_only", "rule_keep_confirmed", "rule_drop_refuted", "pipeline")


def unique_findings(srec: dict) -> list:
    seen, out = set(), []
    for f in srec.get("findings", []):
        if f["category"] not in seen:
            seen.add(f["category"])
            out.append(f)
    return out


def main(argv=None, client=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["development", "evaluation"], required=True)
    ap.add_argument("--static-run", required=True)
    ap.add_argument("--dynamic-run", required=True)
    ap.add_argument("--run-id")
    ap.add_argument("--cases", nargs="*")
    ap.add_argument("--final", action="store_true", help="obrigatorio para o Evaluation Set")
    a = ap.parse_args(argv)

    if a.split == "evaluation" and not a.final:
        sys.exit("Evaluation Set so roda com --final (execucao unica, apos congelar os prompts).")
    dmeta = json.loads((RUNS / a.dynamic_run / "run_meta.json").read_text())
    if dmeta.get("mode") != "static" or dmeta.get("static_run") != a.static_run:
        sys.exit(f"A execucao {a.dynamic_run} nao foi feita sobre o Static {a.static_run} (modo {dmeta.get('mode')}).")

    gt = json.loads((DATASET / "ground_truth.json").read_text(encoding="utf-8"))
    manifest = {m["id"]: m for m in json.loads((DATASET / "sanitized" / "manifest.json").read_text())}
    cases = [c for c in gt["cases"] if c["split"] == a.split and (not a.cases or c["id"] in a.cases)]
    if not cases:
        sys.exit("Nenhum caso selecionado.")

    run_id = a.run_id or f"{datetime.now():%Y%m%d_%H%M}_synthesis_{a.split}"
    out = RUNS / run_id / "synthesis"
    out.mkdir(parents=True, exist_ok=True)
    meta_path = RUNS / run_id / "run_meta.json"
    fp = {**prompt_fingerprint(), **describe(), "static_run": a.static_run, "dynamic_run": a.dynamic_run,
          "dynamic_prompt_sha256": dmeta.get("dynamic_prompt_sha256")}
    if meta_path.exists():
        old = json.loads(meta_path.read_text())
        for k in ("synthesis_prompt_sha256", "llm_model", "llm_base_url", "llm_extra_body", "static_run", "dynamic_run"):
            if old.get(k) != fp[k]:
                sys.exit(f"{k} mudou desde o inicio da execucao {run_id}; use um novo --run-id.")
    else:
        meta_path.write_text(json.dumps({**fp, "split": a.split, "started": datetime.now().isoformat(),
                                         "ground_truth_version": gt["version"]}, indent=2, default=str))

    print(f"Execucao {run_id} | {fp['llm_model']} | {fp['synthesis_prompt_version']} "
          f"({fp['synthesis_prompt_sha256']}) | {len(cases)} casos")
    per_case = {k: {} for k in CONFIGS}
    for i, c in enumerate(cases, 1):
        m = manifest[c["id"]]
        srec = json.loads((RUNS / a.static_run / "static" / f"{c['id']}.json").read_text())
        pairs = []
        for f in unique_findings(srec):
            dpath = RUNS / a.dynamic_run / "dynamic" / f"{c['id']}__{f['category']}.json"
            pairs.append((f, json.loads(dpath.read_text()) if dpath.exists() else None))
        missing = [f["category"] for f, d in pairs if d is None]
        if missing:
            print(f"      aviso: {c['id']} sem resultado do Dynamic para {missing}")
        path = out / f"{c['id']}.json"
        ctx = {"instruction": m["target_instruction"], "framework": c["framework"]}
        if path.exists():
            rec, status = json.loads(path.read_text()), "cache"
        else:
            try:
                rec = run_synthesis(ctx, pairs, client=client)
            except DailyLimitReached as e:
                print(f"\nCota diaria esgotada ({e}). Retome com --run-id {run_id}")
                break
            rec["case_id"] = c["id"]
            path.write_text(json.dumps(rec, indent=2, ensure_ascii=False, default=str))
            (out / f"{c['id']}.md").write_text(render_markdown(c["id"], ctx, rec), encoding="utf-8")
            status = "novo "
        verdict = {f["category"]: (d or {}).get("verdict") for f, d in pairs}
        preds = {
            "static_only": srec.get("predicted", []),
            "rule_keep_confirmed": [k for k, v in verdict.items() if v == "confirmed"],
            "rule_drop_refuted": [k for k, v in verdict.items() if v != "not_confirmed"],
            "pipeline": rec["predicted"],
        }
        for k in CONFIGS:
            per_case[k][c["id"]] = score_case(c, preds[k])
        flags = "".join([" [JSON INVALIDO]" if rec.get("parse_error") else "",
                         f" omitidos={rec['omitted']}" if rec.get("omitted") else "",
                         f" extras={len(rec['extra_categories'])}" if rec.get("extra_categories") else ""])
        print(f"[{i:2d}/{len(cases)}] {status} {c['id']:12s} {c['label']:10s} dinamica={verdict or '-'} "
              f"-> final={rec['predicted'] or '-'} ({per_case['pipeline'][c['id']]['outcome']}){flags}")

    metrics = {k: aggregate(cases, per_case[k]) for k in CONFIGS}
    metrics.update({"run_id": run_id, **fp})
    (RUNS / run_id / "metrics_synthesis.json").write_text(json.dumps(metrics, indent=2, default=str))
    for k in CONFIGS:
        print(f"\n== {k}")
        print_table(metrics[k])
    print(f"Resultados: {RUNS / run_id}")
    return metrics


if __name__ == "__main__":
    main()
