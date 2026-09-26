"""
agents/static_agent.py

Replica o Agente de Análise Estática do SADA (Seção 5.2 do artigo).

DIFERENÇA METODOLÓGICA EM RELAÇÃO AO ARTIGO ORIGINAL:
O artigo usa um GPT-4o fine-tunado com 11 contratos + relatórios de exemplo.
Aqui, por restrição de orçamento (fine-tuning pago indisponível), usamos
Llama 3.3 70B via Groq (gratuito) com prompt engineering: o mesmo
conhecimento de domínio (OWASP Top 10 + SWC Registry, Seções 3.2 e 3.3
do artigo) é injetado diretamente no system prompt, funcionando como uma
base de conhecimento estática equivalente à usada no fine-tuning.
"""

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

# Base de conhecimento de domínio (equivalente ao conteúdo usado no fine-tuning do artigo)
# Fonte: Seção 3.2 (OWASP Top 10) e Seção 3.3 / Tabela 1 (SWC Registry) do artigo original.
DOMAIN_KNOWLEDGE = """
OWASP TOP 10 PARA SMART CONTRACTS (2023):
1. Reentrancy Attacks - chamada externa antes de atualizar o estado; mitigar com padrão Checks-Effects-Interactions e reentrancy guards.
2. Integer Overflow and Underflow - operações aritméticas fora dos limites da variável; mitigar com SafeMath ou Solidity >= 0.8.0.
3. Timestamp Dependence - uso de block.timestamp para lógica crítica, manipulável por mineradores; usar block.number ou buffers de tempo.
4. Access Control Vulnerabilities - falta de restrição adequada a funções sensíveis; usar modifiers e RBAC.
5. Front-Running Attacks - exploração de transações pendentes; mitigar com commit-reveal ou mempools privados.
6. Denial of Service (DoS) - exaustão de recursos; evitar loops de tamanho ilimitado, usar pull payments.
7. Logic Errors - falhas sutis na lógica do contrato; revisão de código e testes unitários.
8. Insecure Randomness - geração de números aleatórios previsíveis; usar Chainlink VRF.
9. Gas Limit Vulnerabilities - funções que excedem limites de gas; otimizar loops e algoritmos.
10. Unchecked External Calls - falha em verificar retorno de chamadas externas; sempre checar valores de retorno.

SWC REGISTRY (vulnerabilidades mais relevantes):
- SWC-101: Integer Overflow and Underflow
- SWC-104: Unchecked Call Return Value
- SWC-105: Unprotected Ether Withdrawal
- SWC-106: Unprotected SELFDESTRUCT Instruction
- SWC-107: Reentrancy
- SWC-109: Uninitialized Storage Pointer
- SWC-112: Delegatecall to Untrusted Callee
- SWC-113: DoS with Failed Call
- SWC-116: Block values as a proxy for time (Timestamp Dependence)
- SWC-120: Weak Sources of Randomness from Chain Attributes
"""

SYSTEM_PROMPT = f"""Você é um agente especialista em segurança de smart contracts Solidity, atuando como o componente de ANÁLISE ESTÁTICA de um sistema multi-agente (SADA).

Sua tarefa é examinar o código-fonte de um smart contract SEM executá-lo, identificando vulnerabilidades, padrões de risco e desvios de boas práticas, com base no seguinte conhecimento de domínio:

{DOMAIN_KNOWLEDGE}

Para cada vulnerabilidade encontrada, seu relatório DEVE seguir exatamente este formato estruturado em Markdown:

## [Nome da Vulnerabilidade]
- **Severidade**: (Crítica | Alta | Média | Baixa)
- **Localização**: (nome da função ou trecho de código)
- **Descrição**: explicação clara do problema
- **Risco/Exploração**: como um atacante poderia explorar essa falha
- **Recomendação**: sugestão específica e acionável de correção, incluindo um trecho de código corrigido quando possível

Regras importantes:
- Seja específico ao trecho de código analisado, evite recomendações genéricas.
- Se nenhuma vulnerabilidade for encontrada, declare isso explicitamente.
- Não invente funções ou comportamentos que não estejam no código fornecido.
- Priorize precisão: é melhor omitir uma suspeita fraca do que gerar um falso positivo.
"""


def run_static_analysis(contract_name: str, source_code: str) -> str:
    """
    Executa a análise estática do código-fonte do contrato usando o Groq.
    Retorna o relatório em formato Markdown (string).
    """
    user_prompt = f"""Analise o smart contract abaixo, chamado '{contract_name}', e gere o relatório de vulnerabilidades seguindo estritamente o formato definido.

CÓDIGO-FONTE:
```solidity
{source_code}
```
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,  # baixa, para minimizar alucinação (mesma lógica da Seção 5.2 do artigo)
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # Teste rápido e isolado deste agente
    from source_retriever import get_contract_data

    test_address = "0x0D8775F648430679A709E98d2b0Cb6250d2887EF"
    contract = get_contract_data(test_address)

    print(f"Rodando análise estática em: {contract['contract_name']}...\n")
    report = run_static_analysis(contract["contract_name"], contract["source_code"])
    print(report)
