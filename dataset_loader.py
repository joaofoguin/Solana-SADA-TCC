"""
dataset_loader.py

Baixa o dataset "Slither Audited Smart Contracts" (Hugging Face) usado no
artigo original (Seção 5.1) e seleciona uma amostra de contratos para
validação, similar aos 11 contratos usados no artigo (Seção 6.2).

Usamos a configuração 'big-multilabel', que contém exatamente 9 classes de
vulnerabilidade (mais a classe "safe"), batendo com a descrição do artigo:
"38 distinct vulnerability classes... consolidated into nine primary
categories, with label 4 reserved for safe contracts."

Carregamos os arquivos parquet diretamente (em vez de usar o nome do dataset
+ config no load_dataset), pois a versão mais recente da lib 'datasets' não
suporta mais os scripts de carregamento customizados que esse dataset usa.
"""

import json
import random
from datasets import load_dataset

SAMPLE_SIZE = 11
OUTPUT_FILE = "dataset/validation_sample.json"
RANDOM_SEED = 42

VALIDATION_PARQUET_URL = (
    "hf://datasets/mwritescode/slither-audited-smart-contracts"
    "@refs/convert/parquet/big-multilabel/validation/0000.parquet"
)


def load_validation_sample():
    print("Carregando dataset (usando cache local se já baixado)...")
    ds = load_dataset("parquet", data_files={"validation": VALIDATION_PARQUET_URL})
    validation_split = ds["validation"]

    print(f"Split de validação total: {len(validation_split)} contratos")

    label_feature = validation_split.features["slither"].feature
    label_names = label_feature.names
    print(f"Classes de vulnerabilidade disponíveis ({len(label_names)}): {label_names}")

    safe_index = label_names.index("safe")

    with_vulns = [
        row for row in validation_split
        if row["source_code"].strip() != "" and safe_index not in row["slither"]
    ]
    safe_contracts = [
        row for row in validation_split
        if row["source_code"].strip() != "" and row["slither"] == [safe_index]
    ]

    print(f"Contratos com vulnerabilidades e código disponível: {len(with_vulns)}")
    print(f"Contratos seguros (safe) e código disponível: {len(safe_contracts)}")

    random.seed(RANDOM_SEED)

    n_vuln = min(9, len(with_vulns))
    n_safe = min(2, len(safe_contracts))

    sample = random.sample(with_vulns, n_vuln) + random.sample(safe_contracts, n_safe)
    random.shuffle(sample)

    output = []
    for i, row in enumerate(sample, start=1):
        vuln_names = [label_names[label_id] for label_id in row["slither"] if label_id != safe_index]
        output.append({
            "contract_id": f"Contract {i}",
            "address": row["address"],
            "source_code": row["source_code"],
            "slither_labels": vuln_names,
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{len(output)} contratos salvos em {OUTPUT_FILE}")
    for item in output:
        labels = item["slither_labels"] if item["slither_labels"] else ["(seguro - sem vulnerabilidades)"]
        print(f"  {item['contract_id']}: {item['address']} -> {labels}")


if __name__ == "__main__":
    load_validation_sample()
