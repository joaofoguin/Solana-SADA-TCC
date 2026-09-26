"""
agents/dynamic_agent.py

Replica o Agente de Análise Dinâmica do SADA (Seção 5.3 do artigo).

Etapas (idênticas à descrição do artigo):
1) Conecta ao contrato via Web3 usando a ABI obtida na Etherscan.
2) Testa funções ERC20 comuns (name, symbol, decimals, totalSupply, balanceOf, allowance).
3) Testa dinamicamente todas as funções 'view'/'pure' definidas na ABI, usando
   parâmetros simulados (mock) baseados no tipo esperado.
4) Gera um relatório bruto dos resultados/erros de cada chamada.
5) Envia esse relatório bruto para o LLM (mesmo modelo do agente estático)
   para uma análise de segurança mais aprofundada.
"""

import json
from groq import Groq
from web3 import Web3
from config import GROQ_API_KEY, GROQ_MODEL, WEB3_PROVIDER_URL

client = Groq(api_key=GROQ_API_KEY)

# Funções ERC20 padrão testadas explicitamente (Seção 5.3 do artigo)
ERC20_STANDARD_FUNCTIONS = ["name", "symbol", "decimals", "totalSupply", "balanceOf", "allowance"]

# Endereço "mock" genérico usado para parâmetros de teste (endereço zero é seguro para chamadas de leitura)
MOCK_ADDRESS = Web3.to_checksum_address("0x000000000000000000000000000000000000dEaD")


def get_mock_value(abi_type: str):
    """Gera um valor simulado (mock) baseado no tipo esperado pela função da ABI."""
    if abi_type.startswith("uint") or abi_type.startswith("int"):
        return 1
    if abi_type == "address":
        return MOCK_ADDRESS
    if abi_type == "bool":
        return True
    if abi_type == "string":
        return "test"
    if abi_type == "bytes" or abi_type.startswith("bytes"):
        return b"\x00" * 32
    if abi_type.endswith("[]"):
        return []
    return None  # tipo não tratado, deixamos como None e registramos o erro se falhar


def simulate_contract_execution(address: str, abi: str) -> dict:
    """
    Simula a execução de funções de leitura (view/pure) do contrato.
    Retorna um dicionário com resultados e erros de cada chamada testada.
    """
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
    parsed_abi = json.loads(abi)
    contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=parsed_abi)

    results = {"function_tests": [], "errors": []}

    # 1) Testa funções ERC20 padrão
    for func_name in ERC20_STANDARD_FUNCTIONS:
        if not hasattr(contract.functions, func_name):
            continue
        try:
            func = getattr(contract.functions, func_name)
            # balanceOf e allowance exigem argumentos (endereços)
            if func_name == "balanceOf":
                value = func(MOCK_ADDRESS).call()
            elif func_name == "allowance":
                value = func(MOCK_ADDRESS, MOCK_ADDRESS).call()
            else:
                value = func().call()
            results["function_tests"].append({"function": func_name, "result": str(value), "status": "success"})
        except Exception as e:
            results["errors"].append({"function": func_name, "error": str(e)})

    # 2) Testa dinamicamente todas as funções view/pure adicionais da ABI
    tested_names = set(ERC20_STANDARD_FUNCTIONS)
    for item in parsed_abi:
        if item.get("type") != "function":
            continue
        name = item.get("name")
        state_mutability = item.get("stateMutability", "")
        if name in tested_names or state_mutability not in ("view", "pure"):
            continue
        tested_names.add(name)

        try:
            inputs = item.get("inputs", [])
            mock_args = [get_mock_value(inp["type"]) for inp in inputs]
            func = getattr(contract.functions, name)
            value = func(*mock_args).call()
            results["function_tests"].append({"function": name, "result": str(value), "status": "success"})
        except Exception as e:
            results["errors"].append({"function": name, "error": str(e)})

    return results


def run_dynamic_analysis(contract_name: str, address: str, abi: str) -> str:
    """
    Executa a simulação de execução e envia os resultados brutos ao LLM
    para gerar um relatório de segurança de análise dinâmica.
    """
    raw_results = simulate_contract_execution(address, abi)

    system_prompt = """Você é um agente especialista em segurança de smart contracts Solidity, atuando como o componente de ANÁLISE DINÂMICA de um sistema multi-agente (SADA).

Você recebe os resultados de uma simulação de execução real de funções do contrato (chamadas bem-sucedidas e erros). Sua tarefa é analisar esses resultados para identificar:
- Comportamentos inesperados em tempo de execução
- Riscos de front-running, slippage ou manipulação de preço
- Falhas de controle de acesso reveladas pelos testes
- Erros que sugerem vulnerabilidades (ex: reverts inesperados, funções que deveriam falhar mas não falharam)

Formate o relatório em Markdown, usando a mesma estrutura do agente de análise estática:

## [Nome da Vulnerabilidade ou Observação]
- **Severidade**: (Crítica | Alta | Média | Baixa | Informativa)
- **Evidência**: qual chamada de função ou resultado motivou essa observação
- **Descrição**: explicação do problema
- **Recomendação**: sugestão de mitigação

Se os resultados não indicarem nenhum problema, declare isso explicitamente. Não invente resultados que não estejam nos dados fornecidos.
"""

    user_prompt = f"""Resultados da simulação de execução do contrato '{contract_name}':

```json
{json.dumps(raw_results, indent=2)}
```

Analise esses resultados e gere o relatório de análise dinâmica.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    from source_retriever import get_contract_data

    test_address = "0x0D8775F648430679A709E98d2b0Cb6250d2887EF"
    contract = get_contract_data(test_address)

    print(f"Rodando análise dinâmica em: {contract['contract_name']}...\n")
    report = run_dynamic_analysis(contract["contract_name"], contract["address"], contract["abi"])
    print(report)
