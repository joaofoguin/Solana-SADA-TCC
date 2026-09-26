"""
orchestrator.py

Replica a Camada de Orquestração do SADA (Seção 5.4 e Figura 2 do artigo).

Fluxo:
1) Recebe o endereço do contrato do usuário.
2) Valida e busca código-fonte + ABI via Etherscan (source_retriever.py).
3) Executa o Agente de Análise Estática.
4) Executa o Agente de Análise Dinâmica.
5) Executa o Agente de Síntese para consolidar os dois relatórios.
6) Salva o relatório final como arquivo Markdown na pasta reports/.
"""

import os
import sys
from datetime import datetime

from source_retriever import get_contract_data
from agents.static_agent import run_static_analysis
from agents.dynamic_agent import run_dynamic_analysis
from agents.synthesis_agent import synthesize_reports

REPORTS_DIR = "reports"


def run_sada(address: str) -> str:
    """
    Executa o pipeline completo do SADA para um endereço de contrato.
    Retorna o caminho do arquivo de relatório gerado.
    """
    print(f"\n{'='*60}")
    print(f"SADA - Static and Dynamic Analyzer")
    print(f"Endereço alvo: {address}")
    print(f"{'='*60}\n")

    print("[1/4] Buscando código-fonte e dados do contrato...")
    contract = get_contract_data(address)
    print(f"      Contrato encontrado: {contract['contract_name']}\n")

    print("[2/4] Executando análise estática...")
    static_report = run_static_analysis(contract["contract_name"], contract["source_code"])
    print("      Concluído.\n")

    print("[3/4] Executando análise dinâmica...")
    dynamic_report = run_dynamic_analysis(contract["contract_name"], contract["address"], contract["abi"])
    print("      Concluído.\n")

    print("[4/4] Sintetizando relatório final...")
    final_report = synthesize_reports(contract["contract_name"], static_report, dynamic_report)
    print("      Concluído.\n")

    # Salva o relatório final como markdown
    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{contract['contract_name']}_{address[:8]}_{timestamp}.md"
    filepath = os.path.join(REPORTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final_report)

    # Também salva os relatórios intermediários (útil para a avaliação quantitativa depois)
    with open(filepath.replace(".md", "_static.md"), "w", encoding="utf-8") as f:
        f.write(static_report)
    with open(filepath.replace(".md", "_dynamic.md"), "w", encoding="utf-8") as f:
        f.write(dynamic_report)

    print(f"Relatório final salvo em: {filepath}")
    return filepath


if __name__ == "__main__":
    if len(sys.argv) > 1:
        contract_address = sys.argv[1]
    else:
        contract_address = input("Digite o endereço do smart contract: ").strip()

    try:
        run_sada(contract_address)
    except Exception as e:
        print(f"\n[ERRO] O pipeline falhou: {e}")
