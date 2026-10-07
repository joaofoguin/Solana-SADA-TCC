"""
agents/llm.py (SADA-Solana)

Cliente LLM compartilhado pelos agentes. Fala com qualquer API compativel com
o formato OpenAI (/chat/completions), o que cobre Groq e a maioria dos
provedores. O provedor e o modelo vem do .env na raiz do repositorio:

  LLM_BASE_URL   (padrao: https://api.groq.com/openai/v1)
  LLM_API_KEY    (padrao: GROQ_API_KEY, a mesma chave da versao EVM)
  LLM_MODEL      (padrao: llama-3.3-70b-versatile)
  LLM_JSON_MODE  (padrao: 1; use 0 se o provedor nao aceitar response_format)
  LLM_EXTRA_BODY (opcional, JSON com parametros proprios do provedor;
                  ex. DeepSeek: {"thinking": {"type": "disabled"}})

Acrescimos em relacao a versao EVM:
1. Saida em JSON, validada pelo chamador.
2. Retentativa com espera em 429 (rate limit) e 5xx, respeitando retry-after.
   Na EVM, um estouro de TPM derrubou o contrato TRACSerums.
3. Cota diaria esgotada interrompe a execucao de forma limpa; o runner retoma
   depois sem refazer os casos concluidos.
"""

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # ~/sada-tcc

try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
JSON_MODE = os.getenv("LLM_JSON_MODE", "1") != "0"
EXTRA_BODY = json.loads(os.getenv("LLM_EXTRA_BODY", "{}") or "{}")
TEMPERATURE = 0.0
MAX_TOKENS = 1500
MAX_ATTEMPTS = 6
TIMEOUT_S = 120


class DailyLimitReached(RuntimeError):
    """Cota diaria esgotada: parar e retomar depois."""


class LLMHTTPError(RuntimeError):
    def __init__(self, status, body, headers=None):
        super().__init__(f"HTTP {status}: {str(body)[:300]}")
        self.status_code, self.body, self.headers = status, body, headers or {}


@dataclass
class LLMResult:
    text: str
    prompt_tokens: int
    completion_tokens: int
    latency_s: float
    attempts: int
    model: str


def describe() -> dict:
    """Identificacao do modelo, registrada em cada execucao (sem a chave)."""
    return {"llm_base_url": BASE_URL, "llm_model": MODEL, "llm_json_mode": JSON_MODE,
            "llm_extra_body": EXTRA_BODY, "temperature": TEMPERATURE}


def _http_post(payload: dict) -> dict:
    import requests

    key = os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY")
    if not key:
        raise EnvironmentError(f"LLM_API_KEY/GROQ_API_KEY nao encontrada em {REPO_ROOT / '.env'}")
    r = requests.post(f"{BASE_URL}/chat/completions", json=payload, timeout=TIMEOUT_S,
                      headers={"Authorization": f"Bearer {key}"})
    if r.status_code != 200:
        raise LLMHTTPError(r.status_code, r.text, dict(r.headers))
    return r.json()


def chat_json(system: str, user: str, client=None, sleep=time.sleep) -> LLMResult:
    """client: funcao payload -> resposta JSON (os testes usam uma falsa)."""
    post = client or _http_post
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }
    if JSON_MODE:
        payload["response_format"] = {"type": "json_object"}
    payload.update(EXTRA_BODY)

    wait = 15.0
    for attempt in range(1, MAX_ATTEMPTS + 1):
        t0 = time.monotonic()
        try:
            resp = post(payload)
            usage = resp.get("usage") or {}
            content = resp["choices"][0]["message"].get("content") or ""
            if not content.strip() and attempt < MAX_ATTEMPTS:
                # alguns provedores (ex.: DeepSeek em modo JSON) devolvem conteudo vazio as vezes
                print(f"      [llm] resposta vazia; repetindo (tentativa {attempt}/{MAX_ATTEMPTS})")
                continue
            return LLMResult(
                text=content,
                prompt_tokens=usage.get("prompt_tokens", 0) or 0,
                completion_tokens=usage.get("completion_tokens", 0) or 0,
                latency_s=round(time.monotonic() - t0, 2),
                attempts=attempt,
                model=resp.get("model", MODEL),
            )
        except LLMHTTPError as e:
            body = str(e.body).lower()
            if e.status_code == 429 and ("per day" in body or "tpd" in body or "rpd" in body or "daily" in body):
                raise DailyLimitReached(str(e)) from e
            if e.status_code not in (429, 500, 502, 503, 504) or attempt == MAX_ATTEMPTS:
                raise
            try:
                delay = float(e.headers.get("retry-after") or e.headers.get("Retry-After") or wait)
            except ValueError:
                delay = wait
        except (ConnectionError, TimeoutError, OSError) as e:
            if attempt == MAX_ATTEMPTS:
                raise
            delay = wait
            e = e  # noqa: PLW0127
        print(f"      [llm] aguardando {delay:.0f}s (tentativa {attempt}/{MAX_ATTEMPTS})")
        sleep(delay)
        wait = min(wait * 2, 120.0)
    raise RuntimeError("inalcancavel")


def parse_json(text: str) -> dict:
    """Aceita JSON puro ou envolto em ```json ... ```."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        t = t.rsplit("```", 1)[0]
    return json.loads(t)
