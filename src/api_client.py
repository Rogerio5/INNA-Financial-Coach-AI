import os

import requests
from dotenv import load_dotenv


load_dotenv()


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def _request_error_message(error: Exception) -> str:
    return (
        "Não foi possível conectar com a API da INNA. "
        "Verifique se a FastAPI está rodando com o comando: "
        "python -m uvicorn api.main:app --reload --port 8000"
    )


def verificar_api_online() -> bool:
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def gerar_diagnostico_api(payload: dict) -> dict:
    try:
        response = requests.post(
            f"{API_BASE_URL}/diagnostico",
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    except requests.ConnectionError as error:
        raise RuntimeError(_request_error_message(error)) from error

    except requests.Timeout as error:
        raise RuntimeError(
            "A API da INNA demorou muito para responder. Tente novamente em alguns instantes."
        ) from error

    except requests.HTTPError as error:
        raise RuntimeError(
            f"A API da INNA retornou um erro HTTP: {response.status_code}. "
            "Verifique os dados enviados ou consulte o Swagger da API."
        ) from error

    except requests.RequestException as error:
        raise RuntimeError(_request_error_message(error)) from error


def enviar_feedback_api(payload: dict) -> dict:
    try:
        response = requests.post(
            f"{API_BASE_URL}/feedback",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        raise RuntimeError(
            "Não foi possível enviar o feedback para a API da INNA."
        ) from error


def baixar_relatorio_pdf_api(diagnostico_id: int) -> bytes:
    try:
        response = requests.get(
            f"{API_BASE_URL}/diagnosticos/{diagnostico_id}/relatorio",
            timeout=60,
        )
        response.raise_for_status()
        return response.content

    except requests.RequestException as error:
        raise RuntimeError(
            "Não foi possível baixar o relatório PDF pela API da INNA."
        ) from error


def buscar_historico_usuario_api(nome: str, limit: int = 10) -> list[dict]:
    try:
        response = requests.get(
            f"{API_BASE_URL}/diagnosticos/usuario/{nome}",
            params={"limit": limit},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        raise RuntimeError(
            "Não foi possível buscar o histórico do usuário na API da INNA."
        ) from error
