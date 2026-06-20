
import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_diagnostico_email(
    to_email: str,
    subject: str,
    body: str,
    pdf_bytes: bytes,
    filename: str = "relatorio-inna.pdf",
) -> None:
    resend_api_key = os.getenv("RESEND_API_KEY")
    email_from = os.getenv(
        "EMAIL_FROM",
        "INNA Financial Coach AI <onboarding@resend.dev>",
    )

    if not resend_api_key:
        raise RuntimeError("RESEND_API_KEY precisa estar configurada no ambiente.")

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

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"Erro Resend: {response.status_code} - {response.text}")
