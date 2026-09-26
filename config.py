"""
config.py
Carrega as chaves de API e configurações do arquivo .env.
Todos os outros módulos do projeto importam suas variáveis a partir daqui.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env na raiz do projeto

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL")

# Modelo usado via Groq (equivalente ao GPT-4o do artigo original)
GROQ_MODEL = "llama-3.3-70b-versatile"

# Validação simples: avisa se alguma chave não foi carregada
def validate_config():
    missing = []
    if not ETHERSCAN_API_KEY:
        missing.append("ETHERSCAN_API_KEY")
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not WEB3_PROVIDER_URL:
        missing.append("WEB3_PROVIDER_URL")

    if missing:
        raise EnvironmentError(
            f"As seguintes variáveis não foram encontradas no .env: {', '.join(missing)}"
        )
    print("[config] Todas as variáveis de ambiente foram carregadas com sucesso.")


if __name__ == "__main__":
    validate_config()
