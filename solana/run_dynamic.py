#!/usr/bin/env python3
"""
run_dynamic.py (SADA-Solana)

Executa o Dynamic Agent sobre os achados de uma execucao do Static Agent e
calcula as metricas do par Static + Dynamic (achado mantido so se confirmado).

Uso:
  python run_dynamic.py --split development --static-run <run_id_do_static>
  python run_dynamic.py --split development --static-run <id> --run-id <id>   # retoma
  python run_dynamic.py --split development --forced      # diagnostico (so Development):
        testa a categoria-alvo de TODOS os casos, inclusive os seguros, para medir
        se o Dynamic confirma casos seguros (ponto de controle de 21/10)
  python run_dynamic.py --split evaluation --static-run <id> --final   # SO na execucao final

Cada achado fica salvo em evaluation/runs/<run_id>/dynamic/<caso>__<CAT>.json
assim que termina; ao retomar, os ja salvos nao sao refeitos.

Binarios: SSP Anchor em solana-security-pattern/target/deploy; programas
portados em dataset/programs/deploy. Programa do atacante (opcional):
dataset/programs/deploy/evil_noop.so ou DYN_ATTACKER_SO.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent  # ~/sada-tcc/solana
sys.path.insert(0, str(HERE))

from agents.dynamic_agent import prompt_fingerprint, run_dynamic_analysis  # noqa: E402
from agents.llm import DailyLimitReached, describe  # noqa: E402
from evaluation.score import KEY_TO_NAME, aggregate, print_table, score_case  # noqa: E402

DATASET = HERE / "dataset"
RUNS = HERE / "evaluation" / "runs"
SSP = HERE / "solana-security-pattern"
NAME_TO_KEY = {v: k for k, v in KEY_TO_NAME.items()}


def so_for_case(case: dict) -> Path:
    if case.get("ported_path"):  # programs/<fonte>/<dir>/src/lib.rs
        d = Path(case["ported_path"]).parts
        return DATASET / "programs" / "deploy" / f"{d[2]}.so"
    pattern_dir = SSP / Path(case["program_path"]).parent.parent  # patterns/<p>/anchor
    toml = (pattern_dir / "Cargo.toml").read_text()
    lib = re.search(r'^\[lib\]\s*$(?:\n(?!\[).*)*?\nname\s*=\s*"([^"]+)"', toml, re.M)
    if not lib:
        raise ValueError(f"{case['id']}: [lib] name nao encontrado em {pattern_dir / 'Cargo.toml'}")
    name = lib.group(1)
    return SSP / "target" / "deploy" / f"{name}.so"


def target_for_case(case: dict, code: str, sanitized_name: str) -> dict:
    m = re.search(r'declare_id!\(\s*"(\w{32,44})"\s*\)', code)
    if not m:
        raise ValueError(f"{case['id']}: declare_id! nao encontrado no codigo sanitizado")
    disc = None
    if case["framework"] == "anchor":
        disc = hashlib.sha256(f"global:{case['instruction']}".encode()).hexdigest()[:16]
    attacker = os.getenv("DYN_ATTACKER_SO") or DATASET / "programs" / "deploy" / "evil_noop.so"
    so = so_for_case(case)
    if not so.exists():
        raise FileNotFoundError(f"{case['id']}: binario nao encontrado: {so}")
    return {"so_path": so, "program_id": m.group(1), "target_name": sanitized_name, "target_disc": disc,
            "attacker_so": attacker if Path(attacker).exists() else None}


def main(argv=None, client=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["development", "evaluation"], required=True)
    ap.add_argument("--static-run")
    ap.add_argument("--forced", action="store_true")
    ap.add_argument("--run-id")
    ap.add_argument("--cases", nargs="*")
    ap.add_argument("--final", action="store_true", help="obrigatorio para o Evaluation Set")
    a = ap.parse_args(argv)

    if a.split == "evaluation" and not a.final:
        sys.exit("Evaluation Set so roda com --final (execucao unica, apos congelar os prompts).")
    if a.forced and a.split != "development":
        sys.exit("--forced usa o rotulo do Ground Truth e so e permitido no Development.")
    if not a.forced and not a.static_run:
        sys.exit("Informe --static-run <id> (ou --forced no Development).")

    gt = json.loads((DATASET / "ground_truth.json").read_text(encoding="utf-8"))
    manifest = {m["id"]: m for m in json.loads((DATASET / "sanitized" / "manifest.json").read_text())}
    cases = [c for c in gt["cases"] if c["split"] == a.split and (not a.cases or c["id"] in a.cases)]
    if not cases:
        sys.exit("Nenhum caso selecionado.")

    mode = "forced" if a.forced else "static"
    run_id = a.run_id or f"{datetime.now():%Y%m%d_%H%M}_dynamic_{mode}_{a.split}"
    out = RUNS / run_id / "dynamic"
    out.mkdir(parents=True, exist_ok=True)
    meta_path = RUNS / run_id / "run_meta.json"
    fp = {**prompt_fingerprint(), **describe(), "mode": mode, "static_run": a.static_run}
    if meta_path.exists():
        old = json.loads(meta_path.read_text())
        for k in ("dynamic_prompt_sha256", "llm_model", "llm_base_url", "llm_extra_body", "mode", "static_run"):
            if old.get(k) != fp[k]:
                sys.exit(f"{k} mudou desde o inicio da execucao {run_id}; use um novo --run-id.")
    else:
        meta_path.write_text(json.dumps({**fp, "split": a.split, "started": datetime.now().isoformat(),
                                         "ground_truth_version": gt["version"]}, indent=2, default=str))

    print(f"Execucao {run_id} | {fp['llm_model']} | {fp['dynamic_prompt_version']} "
          f"({fp['dynamic_prompt_sha256']}) | modo {mode} | {len(cases)} casos")
    per_case_static, per_case_pipe, verdicts = {}, {}, []
    stopped = False
    for i, c in enumerate(cases, 1):
        m = manifest[c["id"]]
        code = (DATASET / m["file"]).read_text(encoding="utf-8")
        if a.forced:
            key = NAME_TO_KEY[c["target_category"]]
            findings = [{"category": key, "evidence": "", "explanation": "",
                         "attack_hypothesis": f"Verificar por execucao se a instrucao e vulneravel a "
                                              f"{c['target_category']}."}]
            static_pred = [key]
        else:
            srec = json.loads((RUNS / a.static_run / "static" / f"{c['id']}.json").read_text())
            seen, findings = set(), []
            for f in srec.get("findings", []):
                if f["category"] not in seen:
                    seen.add(f["category"])
                    findings.append(f)
            static_pred = srec.get("predicted", [])
        confirmed = []
        for f in findings:
            path = out / f"{c['id']}__{f['category']}.json"
            if path.exists():
                rec, status = json.loads(path.read_text()), "cache"
            else:
                try:
                    target = target_for_case(c, code, m["target_instruction"])
                    rec = run_dynamic_analysis({"instruction": m["target_instruction"],
                                                "framework": c["framework"], "code": code},
                                               f, target, client=client)
                except DailyLimitReached as e:
                    print(f"\nCota diaria esgotada ({e}). Retome com --run-id {run_id}")
                    stopped = True
                    break
                rec.update({"case_id": c["id"], "static_finding": f})
                path.write_text(json.dumps(rec, indent=2, ensure_ascii=False, default=str))
                status = "novo "
            verdicts.append((c, rec))
            if rec["verdict"] == "confirmed":
                confirmed.append(f["category"])
            print(f"[{i:2d}/{len(cases)}] {status} {c['id']:12s} {c['label']:10s} {f['category']:8s} "
                  f"-> {rec['verdict']:13s} ({rec['attempts_used']} tent.) {rec['attack_result'] or ''}")
        if stopped:
            break
        if not findings:
            print(f"[{i:2d}/{len(cases)}] -     {c['id']:12s} {c['label']:10s} (sem achado do Static)")
        per_case_static[c["id"]] = score_case(c, static_pred)
        per_case_pipe[c["id"]] = score_case(c, confirmed)

    # resumo do ponto de controle: o Dynamic confirma vulneraveis e nao confirma seguros?
    def count(label, verdict):
        return sum(1 for c, r in verdicts if c["label"] == label and r["verdict"] == verdict
                   and KEY_TO_NAME[r["category"]] == c["target_category"])
    checkpoint = {lab: {v: count(lab, v) for v in ("confirmed", "not_confirmed", "inconclusive")}
                  for lab in ("vulnerable", "secure")}
    metrics = {
        # no modo forced a "previsao do Static" e a propria categoria-alvo: nao e metrica do Static
        "static_only": None if a.forced else aggregate(cases, per_case_static),
        "static_plus_dynamic": aggregate(cases, per_case_pipe),
        "checkpoint_target_category": checkpoint,
        "run_id": run_id, **fp,
    }
    (RUNS / run_id / "metrics_dynamic.json").write_text(json.dumps(metrics, indent=2, default=str))
    if metrics["static_only"]:
        print("\nStatic isolado:")
        print_table(metrics["static_only"])
    print("\nStatic + Dynamic (achado mantido so se confirmado; antes do Synthesis):")
    print_table(metrics["static_plus_dynamic"])
    print("\nCategoria-alvo por rotulo:", json.dumps(checkpoint))
    print(f"Resultados: {RUNS / run_id}")
    return metrics


if __name__ == "__main__":
    main()
