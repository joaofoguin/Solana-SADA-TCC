"""
evaluation/metrics.py (v2 - corrigido)

Correções em relação à v1:
1. O keyword matching agora é restrito à seção "## Vulnerabilidades
   Identificadas" do relatório final (onde ficam as vulnerabilidades
   CONFIRMADAS, cada uma com um cabeçalho "### [Nome]"). Isso evita falsos
   positivos vindos de texto genérico de recomendação nas seções de Resumo
   Executivo e Considerações Finais.
2. Suporta retomada: se já existe evaluation/results.json, contratos com
   status "ok" são REPROCESSADOS a partir do relatório salvo em disco (sem
   nova chamada à API) usando a lógica de extração corrigida. Contratos
   pendentes/com erro são tentados novamente (consomem tokens da API).

NOTA METODOLÓGICA (documentar no TCC):
Mesmo restrita à seção de achados confirmados, essa extração automática via
keyword matching é uma aproximação e deve ser complementada por revisão
manual amostral (Fase 7).
"""

import json
import os
import re
import time
import traceback

from web3 import Web3

from orchestrator import run_sada
from source_retriever import get_contract_data

SAMPLE_FILE = "dataset/validation_sample.json"
RESULTS_FILE = "evaluation/results.json"

KEYWORD_MAP = {
    "access-control": ["access control", "controle de acesso", "unprotected", "permissão", "authorization", "autorização"],
    "arithmetic": ["overflow", "underflow", "integer arithmetic", "aritmética", "safemath"],
    "reentrancy": ["reentrancy", "reentrância", "reentrada"],
    "unchecked-calls": ["unchecked", "não verificad", "call return", "retorno da chamada", "external call"],
    "other": [],
}


def extract_confirmed_findings_section(report_text: str) -> str:
    match = re.search(
        r"##\s*Vulnerabilidades Identificadas(.*?)(?=\n##\s|\Z)",
        report_text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return match.group(1) if match else ""


def contains_any(text: str, keywords: list) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


NEGATION_PHRASES = [
    "não há risco", "não representa risco", "não é observado",
    "não foi observado", "não foi identificado", "nenhum risco",
    "não se aplica", "não observado no código", "isso não é observado",
    "não há evidência", "nenhuma vulnerabilidade", "sem risco de exploração",
]


def split_into_subsections(findings_section: str) -> list:
    """Divide a seção de achados em subseções por cabeçalho '### Nome'."""
    parts = re.split(r"\n###\s+", findings_section)
    return [p for p in parts if p.strip()]


def is_negated(subsection_text: str) -> bool:
    text_lower = subsection_text.lower()
    return any(phrase in text_lower for phrase in NEGATION_PHRASES)


def extract_predicted_labels(report_text: str) -> set:
    findings_section = extract_confirmed_findings_section(report_text)
    if not findings_section:
        print("[AVISO] Seção 'Vulnerabilidades Identificadas' não encontrada no relatório.")
        return set()

    predicted = set()
    for subsection in split_into_subsections(findings_section):
        if is_negated(subsection):
            continue  # o próprio texto nega a vulnerabilidade - não conta
        for category, keywords in KEYWORD_MAP.items():
            if not keywords:
                continue
            if contains_any(subsection, keywords):
                predicted.add(category)
    return predicted


def compute_metrics(true_labels: set, predicted_labels: set) -> dict:
    tp = len(true_labels & predicted_labels)
    fp = len(predicted_labels - true_labels)
    fn = len(true_labels - predicted_labels)

    precision = tp / (tp + fp) if (tp + fp) > 0 else (1.0 if fp == 0 and tp == 0 else 0.0)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
    }


def load_previous_results() -> dict:
    if not os.path.exists(RESULTS_FILE):
        return {}
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {r["contract_id"]: r for r in data.get("per_contract", [])}


def run_evaluation():
    with open(SAMPLE_FILE, "r", encoding="utf-8") as f:
        sample = json.load(f)

    previous = load_previous_results()
    results = []

    for item in sample:
        contract_id = item["contract_id"]
        raw_address = item["address"]
        true_labels = set(item["slither_labels"])
        prev = previous.get(contract_id)

        if prev and prev.get("status") == "ok" and prev.get("report_path") and os.path.exists(prev["report_path"]):
            print(f"\n[REPROCESSANDO sem API] {contract_id} - usando relatório salvo em {prev['report_path']}")
            with open(prev["report_path"], "r", encoding="utf-8") as f:
                report_text = f.read()

            predicted_labels = extract_predicted_labels(report_text)
            metrics = compute_metrics(true_labels, predicted_labels)

            print(f"Rótulos reais (Slither): {true_labels or '(seguro)'}")
            print(f"Rótulos previstos (corrigido): {predicted_labels or '(nenhum detectado)'}")
            print(f"Métricas: {metrics}")

            results.append({
                **prev,
                "true_labels": list(true_labels),
                "predicted_labels": list(predicted_labels),
                "metrics": metrics,
            })
            continue

        print(f"\n{'='*60}\n{contract_id} - {raw_address}\n{'='*60}")

        try:
            checksum_address = Web3.to_checksum_address(raw_address)
        except Exception as e:
            print(f"[SKIP] Endereço inválido: {e}")
            results.append({"contract_id": contract_id, "address": raw_address, "status": "invalid_address"})
            continue

        try:
            get_contract_data(checksum_address)
        except Exception as e:
            print(f"[SKIP] Contrato não disponível na Etherscan: {e}")
            results.append({"contract_id": contract_id, "address": checksum_address, "status": "not_on_etherscan"})
            continue

        try:
            report_path = run_sada(checksum_address)
            with open(report_path, "r", encoding="utf-8") as f:
                report_text = f.read()
        except Exception as e:
            print(f"[ERRO] Pipeline SADA falhou: {e}")
            traceback.print_exc()
            results.append({"contract_id": contract_id, "address": checksum_address, "status": "pipeline_error"})
            continue

        predicted_labels = extract_predicted_labels(report_text)
        metrics = compute_metrics(true_labels, predicted_labels)

        print(f"Rótulos reais (Slither): {true_labels or '(seguro)'}")
        print(f"Rótulos previstos: {predicted_labels or '(nenhum detectado)'}")
        print(f"Métricas: {metrics}")

        results.append({
            "contract_id": contract_id,
            "address": checksum_address,
            "status": "ok",
            "true_labels": list(true_labels),
            "predicted_labels": list(predicted_labels),
            "metrics": metrics,
            "report_path": report_path,
        })

        time.sleep(2)

    valid_results = [r for r in results if r["status"] == "ok"]
    total_tp = sum(r["metrics"]["tp"] for r in valid_results)
    total_fp = sum(r["metrics"]["fp"] for r in valid_results)
    total_fn = sum(r["metrics"]["fn"] for r in valid_results)

    overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    overall_f1 = (2 * overall_precision * overall_recall) / (overall_precision + overall_recall) \
        if (overall_precision + overall_recall) > 0 else 0.0

    summary = {
        "contracts_evaluated": len(valid_results),
        "contracts_total": len(sample),
        "overall_precision": round(overall_precision, 3),
        "overall_recall": round(overall_recall, 3),
        "overall_f1": round(overall_f1, 3),
    }

    final_output = {"summary": summary, "per_contract": results}

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    print(f"\n\n{'='*60}\nRESUMO FINAL\n{'='*60}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nResultados detalhados salvos em: {RESULTS_FILE}")


if __name__ == "__main__":
    run_evaluation()
