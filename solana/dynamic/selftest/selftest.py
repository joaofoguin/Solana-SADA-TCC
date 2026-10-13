#!/usr/bin/env python3
"""
dynamic/selftest/selftest.py (SADA-Solana)

Teste de software do harness do Dynamic Agent: executa cenarios escritos pelo
autor para os casos do Development e confere o veredito das regras de decisao.
NAO e resultado experimental e estes cenarios NUNCA entram no prompt do agente;
servem so para provar que o harness, o carregamento dos .so e as regras de
veredito funcionam antes de colocar o LLM no circuito.

Uso (de ~/sada-tcc/solana):  python dynamic/selftest/selftest.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))

from agents.dynamic_agent import execute_scenario, judge  # noqa: E402
from run_dynamic import target_for_case  # noqa: E402

gt = {c["id"]: c for c in json.loads((HERE / "dataset" / "ground_truth.json").read_text())["cases"]}
manifest = {m["id"]: m for m in json.loads((HERE / "dataset" / "sanitized" / "manifest.json").read_text())}
ok = 0
items = json.loads((Path(__file__).parent / "scenarios_dev.json").read_text())
for it in items:
    c, m = gt[it["case"]], manifest[it["case"]]
    code = (HERE / "dataset" / m["file"]).read_text()
    run = execute_scenario(it["scenario"], target_for_case(c, code, m["target_instruction"]))
    verdict, reason = judge(run)
    good = verdict == it["expected_verdict"]
    ok += good
    print(f"{'OK  ' if good else 'FALHA'} {it['case']:12s} esperado={it['expected_verdict']:13s} obtido={verdict}  ({reason[:80]})")
print(f"\n{ok}/{len(items)} cenarios com o veredito esperado")
sys.exit(0 if ok == len(items) else 1)
