#!/usr/bin/env python3
"""
run_pipeline.py (SADA-Solana)

Orquestrador: Static Agent -> Dynamic Agent -> Synthesis Agent, com os mesmos
identificadores de execucao, para a execucao unica no Evaluation Set.

Uso:
  python run_pipeline.py --split evaluation --final
  python run_pipeline.py --split evaluation --final --stamp <AAAAMMDD_HHMM>   # retoma
  python run_pipeline.py --split development --static-run <id>   # ensaio no Development

Com --final, os tres prompts precisam ter exatamente os hashes congelados em
FROZEN (qualquer alteracao de prompt, harness ou KB impede a execucao).
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_dynamic  # noqa: E402
import run_static  # noqa: E402
import run_synthesis  # noqa: E402
from agents.dynamic_agent import prompt_fingerprint as dynamic_fp  # noqa: E402
from agents.static_agent import prompt_fingerprint as static_fp  # noqa: E402
from agents.synthesis_agent import prompt_fingerprint as synthesis_fp  # noqa: E402

RUNS = HERE / "evaluation" / "runs"

# Versoes congeladas para o Evaluation (atualizar so por decisao registrada).
FROZEN = {
    "prompt_sha256": "29c3d0e4c72954d7",            # static-v1
    "dynamic_prompt_sha256": None,      # preencher ao congelar o Dynamic (candidato: dynamic-v4)
    "synthesis_prompt_sha256": None,    # preencher ao congelar o Synthesis (candidato: synthesis-v1)
}


def current_hashes() -> dict:
    return {"prompt_sha256": static_fp()["prompt_sha256"],
            "dynamic_prompt_sha256": dynamic_fp()["dynamic_prompt_sha256"],
            "synthesis_prompt_sha256": synthesis_fp()["synthesis_prompt_sha256"]}


def main(argv=None, client=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["development", "evaluation"], required=True)
    ap.add_argument("--stamp", help="prefixo dos run_id (para retomar)")
    ap.add_argument("--static-run", help="reaproveitar uma execucao do Static (so no Development)")
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args(argv)

    final = ["--final"] if a.final else []
    if a.split == "evaluation":
        if not a.final:
            sys.exit("Evaluation Set so roda com --final.")
        if a.static_run:
            sys.exit("No Evaluation, o Static roda dentro do pipeline (sem --static-run).")
        unset = [k for k, v in FROZEN.items() if v is None]
        if unset:
            sys.exit(f"Versoes ainda nao congeladas em FROZEN: {unset}")
        cur = current_hashes()
        diff = {k: (cur[k], v) for k, v in FROZEN.items() if cur[k] != v}
        if diff:
            sys.exit(f"Prompts diferentes dos congelados (atual, congelado): {diff}")

    stamp = a.stamp or f"{datetime.now():%Y%m%d_%H%M}"
    static_id = a.static_run or f"{stamp}_static_{a.split}"
    dynamic_id = f"{stamp}_dynamic_static_{a.split}"
    synthesis_id = f"{stamp}_synthesis_{a.split}"

    if not a.static_run:
        print("\n######## 1/3 Static Agent")
        run_static.main(["--split", a.split, "--run-id", static_id] + final, client=client)
    gt = json.loads((HERE / "dataset" / "ground_truth.json").read_text(encoding="utf-8"))
    ids = [c["id"] for c in gt["cases"] if c["split"] == a.split]
    missing = [i for i in ids if not (RUNS / static_id / "static" / f"{i}.json").exists()]
    if missing:
        sys.exit(f"Static incompleto ({len(missing)} casos). Retome com --stamp {stamp}")

    print("\n######## 2/3 Dynamic Agent")
    run_dynamic.main(["--split", a.split, "--static-run", static_id, "--run-id", dynamic_id] + final, client=client)
    pending = []
    for i in ids:
        srec = json.loads((RUNS / static_id / "static" / f"{i}.json").read_text())
        for f in run_synthesis.unique_findings(srec):
            if not (RUNS / dynamic_id / "dynamic" / f"{i}__{f['category']}.json").exists():
                pending.append(f"{i}/{f['category']}")
    if pending:
        sys.exit(f"Dynamic incompleto ({len(pending)} achados). Retome com --stamp {stamp}")

    print("\n######## 3/3 Synthesis Agent")
    metrics = run_synthesis.main(["--split", a.split, "--static-run", static_id, "--dynamic-run", dynamic_id,
                                  "--run-id", synthesis_id] + final, client=client)
    (RUNS / synthesis_id / "pipeline_meta.json").write_text(json.dumps(
        {"stamp": stamp, "static_run": static_id, "dynamic_run": dynamic_id, "synthesis_run": synthesis_id,
         "hashes": current_hashes(), "frozen_checked": a.split == "evaluation",
         "finished": datetime.now().isoformat()}, indent=2))
    return metrics


if __name__ == "__main__":
    main()
