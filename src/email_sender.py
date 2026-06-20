
import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv

load_dotenv()


def send_diagnostico_email(
    to_email: str,
    subject: str,
    body: str,
    pdf_bytes: bytes,
    filename: str = "relatorio-inna.pdf",
) -> None:
    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
    from_name = os.getenv("GMAIL_FROM_NAME", "INNA Financial Coach AI")

    if not gmail_user or not gmail_app_password:
        raise RuntimeError(
            "GMAIL_USER e GMAIL_APP_PASSWORD precisam estar configurados no ambiente."
        )

    msg = EmailMessage()
    msg["From"] = formataddr((from_name, gmail_user))
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.set_content(body)

    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=filename,
    )

    # Gmail SMTP usando STARTTLS na porta 587
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(gmail_user, gmail_app_password)
        smtp.send_message(msg)
