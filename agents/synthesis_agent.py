"""
agents/synthesis_agent.py

Replica o Agente de Síntese do SADA (Seção 5.4 do artigo).

No artigo, esse agente usa uma instância "fresh" do GPT (sem o fine-tuning
usado pelos outros dois agentes) para combinar os relatórios estático e
dinâmico em um relatório único e coeso. Aqui replicamos isso usando uma
chamada ao Llama 3.3 70B via Groq SEM o system prompt de conhecimento de
domínio (OWASP/SWC) usado nos outros agentes — apenas instruções de
formatação e consolidação, equivalente à ideia de "instância limpa".
"""

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Você é o agente de SÍNTESE de um sistema multi-agente de análise de segurança de smart contracts (SADA).

Você recebe dois relatórios independentes:
1. Um relatório de ANÁLISE ESTÁTICA (vulnerabilidades identificadas no código-fonte, sem execução).
2. Um relatório de ANÁLISE DINÂMICA (observações de uma simulação real de execução do contrato).

Sua tarefa é combinar esses dois relatórios em um ÚNICO relatório final, consolidado, evitando duplicação de vulnerabilidades já cobertas em ambos. Para cada vulnerabilidade no relatório final, você deve:
- Indicar a origem (Estática, Dinâmica ou Ambas)
- Atribuir uma severidade final (Crítica | Alta | Média | Baixa | Informativa)
- Descrever o risco de exploração de forma clara
- Fornecer uma recomendação de mitigação específica e acionável

O relatório final deve seguir esta estrutura em Markdown:

# Relatório de Segurança Consolidado — [Nome do Contrato]

## Resumo Executivo
(2-3 frases resumindo a postura geral de segurança do contrato)

## Vulnerabilidades Identificadas

### [Nome da Vulnerabilidade]
- **Origem**: (Análise Estática | Análise Dinâmica | Ambas)
- **Severidade**: (Crítica | Alta | Média | Baixa | Informativa)
- **Descrição**: ...
- **Risco de Exploração**: ...
- **Recomendação**: ...

## Considerações Finais
(observações gerais e próximos passos recomendados para os desenvolvedores)

Regras:
- Não invente vulnerabilidades que não estejam presentes em nenhum dos dois relatórios de entrada.
- Se um dos relatórios não identificou nenhuma vulnerabilidade, isso deve ser refletido no resumo executivo.
"""


def synthesize_reports(contract_name: str, static_report: str, dynamic_report: str) -> str:
    """
    Combina os relatórios estático e dinâmico em um relatório final consolidado.
    """
    user_prompt = f"""Contrato analisado: {contract_name}

--- RELATÓRIO DE ANÁLISE ESTÁTICA ---
{static_report}

--- RELATÓRIO DE ANÁLISE DINÂMICA ---
{dynamic_report}

Gere o relatório final consolidado seguindo estritamente o formato definido.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    from source_retriever import get_contract_data
    from agents.static_agent import run_static_analysis
    from agents.dynamic_agent import run_dynamic_analysis

    test_address = "0x0D8775F648430679A709E98d2b0Cb6250d2887EF"
    contract = get_contract_data(test_address)

    print("Rodando análise estática...")
    static_report = run_static_analysis(contract["contract_name"], contract["source_code"])

    print("Rodando análise dinâmica...")
    dynamic_report = run_dynamic_analysis(contract["contract_name"], contract["address"], contract["abi"])

    print("Sintetizando relatório final...\n")
    final_report = synthesize_reports(contract["contract_name"], static_report, dynamic_report)
    print(final_report)
