"""
source_retriever.py

Replica os passos 1 e 2 do SADA (Seção 4.1 do artigo):
1) Input and Validation: garante que o endereço está em formato checksum válido.
2) Source Code Retrieval: busca o código-fonte do contrato via Etherscan API.
"""

import requests
from web3 import Web3
from config import ETHERSCAN_API_KEY, WEB3_PROVIDER_URL, validate_config

ETHERSCAN_BASE_URL = "https://api.etherscan.io/v2/api"


def get_web3_instance() -> Web3:
    """Cria e retorna uma instância conectada do Web3."""
    w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
    if not w3.is_connected():
        raise ConnectionError("Não foi possível conectar ao provedor Web3 (verifique WEB3_PROVIDER_URL).")
    return w3


def validate_and_checksum_address(address: str, w3: Web3) -> str:
    """
    Passo 1: garante que o endereço está em formato checksum válido.
    Se não estiver, converte usando o Web3.
    """
    if not Web3.is_address(address):
        raise ValueError(f"Endereço inválido: {address}")

    if Web3.is_checksum_address(address):
        return address

    checksum_address = Web3.to_checksum_address(address)
    print(f"[source_retriever] Endereço convertido para checksum: {checksum_address}")
    return checksum_address


def is_contract_address(address: str, w3: Web3) -> bool:
    """Confirma que o endereço realmente corresponde a um contrato (tem bytecode)."""
    code = w3.eth.get_code(Web3.to_checksum_address(address))
    return len(code) > 0


def fetch_source_code(address: str) -> dict:
    """
    Passo 2: busca o código-fonte do contrato na Etherscan API.
    Retorna um dicionário com o código-fonte, nome do contrato e ABI.
    """
    params = {
	"chainid": 1,
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": ETHERSCAN_API_KEY,
    }

    response = requests.get(ETHERSCAN_BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != "1":
        raise RuntimeError(f"Etherscan retornou erro: {data.get('message')} - {data.get('result')}")

    result = data["result"][0]

    if result.get("SourceCode", "") == "":
        raise RuntimeError(
            "Contrato não verificado na Etherscan (código-fonte indisponível). "
            "Tente outro endereço de contrato verificado."
        )

    return {
        "contract_name": result.get("ContractName"),
        "source_code": result.get("SourceCode"),
        "abi": result.get("ABI"),
        "compiler_version": result.get("CompilerVersion"),
    }


def get_contract_data(address: str) -> dict:
    """
    Função principal deste módulo: valida o endereço e retorna os dados do contrato.
    """
    w3 = get_web3_instance()
    checksum_address = validate_and_checksum_address(address, w3)

    if not is_contract_address(checksum_address, w3):
        raise ValueError(f"O endereço {checksum_address} não corresponde a um smart contract implantado.")

    contract_data = fetch_source_code(checksum_address)
    contract_data["address"] = checksum_address
    return contract_data


if __name__ == "__main__":
    validate_config()

    # Endereço de teste: contrato do token BAT (Basic Attention Token) - verificado na Etherscan
    test_address = "0x0D8775F648430679A709E98d2b0Cb6250d2887EF"

    try:
        data = get_contract_data(test_address)
        print(f"\nContrato encontrado: {data['contract_name']}")
        print(f"Endereço (checksum): {data['address']}")
        print(f"Versão do compilador: {data['compiler_version']}")
        print(f"Tamanho do código-fonte: {len(data['source_code'])} caracteres")
    except Exception as e:
        print(f"[ERRO] {e}")
