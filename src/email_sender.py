import base64
import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


RESEND_ENDPOINT = "https://api.resend.com/emails"


def _get_email_config() -> tuple[str, str]:
    """
    Carrega as credenciais de envio configuradas no ambiente.
    """
    resend_api_key = os.getenv("RESEND_API_KEY")
    email_from = os.getenv(
        "EMAIL_FROM",
        "INNA Financial Coach AI <onboarding@resend.dev>",
    )

    if not resend_api_key:
        raise RuntimeError("RESEND_API_KEY precisa estar configurada no ambiente.")

    return resend_api_key, email_from


def _send_resend_payload(
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Envia um payload para a API do Resend.

    Retorna o identificador fornecido pelo provedor quando disponível.
    """
    resend_api_key, _ = _get_email_config()

    response = requests.post(
        RESEND_ENDPOINT,
        headers={
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"Erro Resend: {response.status_code} - {response.text}")

    try:
        data = response.json()
    except ValueError:
        data = {}

    return {
        "ok": True,
        "provider": "resend",
        "message_id": data.get("id"),
        "status_code": response.status_code,
    }


def send_text_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: str | None = None,
) -> dict[str, Any]:
    """
    Envia um e-mail sem anexo.

    Utilizado para alertas administrativos e notificações técnicas.
    """
    _, email_from = _get_email_config()

    payload: dict[str, Any] = {
        "from": email_from,
        "to": [to_email],
        "subject": subject,
        "text": body,
    }

    if html_body:
        payload["html"] = html_body

    return _send_resend_payload(payload)


def send_diagnostico_email(
    to_email: str,
    subject: str,
    body: str,
    pdf_bytes: bytes,
    filename: str = "relatorio-inna.pdf",
) -> dict[str, Any]:
    """
    Envia o diagnóstico financeiro com o relatório em PDF.
    """
    _, email_from = _get_email_config()

    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    payload = {
        "from": email_from,
        "to": [to_email],
        "subject": subject,
        "text": body,
        "attachments": [
            {
                "filename": filename,
                "content": pdf_base64,
            }
        ],
    }

    return _send_resend_payload(payload)


__all__ = [
    "send_text_email",
    "send_diagnostico_email",
]
