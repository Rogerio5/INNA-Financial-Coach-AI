import os
import requests
from dotenv import load_dotenv


load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def gerar_diagnostico_api(payload: dict) -> dict:
    url = f"{API_BASE_URL}/diagnostico"

    response = requests.post(
        url,
        json=payload,
        timeout=90,
    )

    response.raise_for_status()

    return response.json()


def enviar_feedback_api(payload: dict) -> dict:
    url = f"{API_BASE_URL}/feedback"

    response = requests.post(
        url,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()
