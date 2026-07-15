"""
Webhook do Resend para atualização de entrega dos e-mails.
"""

from __future__ import annotations

import os

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
)
from svix.webhooks import Webhook


try:
    from src.observability.resend_webhook import (
        processar_evento_resend,
    )
except ImportError:
    from observability.resend_webhook import (
        processar_evento_resend,
    )


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post("/resend")
async def receber_webhook_resend(
    request: Request,
):
    secret = os.getenv(
        "RESEND_WEBHOOK_SECRET"
    )

    if not secret:
        raise HTTPException(
            status_code=503,
            detail=(
                "RESEND_WEBHOOK_SECRET "
                "não configurado."
            ),
        )

    corpo = await request.body()

    headers = {
        "svix-id": request.headers.get(
            "svix-id",
            "",
        ),
        "svix-timestamp": request.headers.get(
            "svix-timestamp",
            "",
        ),
        "svix-signature": request.headers.get(
            "svix-signature",
            "",
        ),
    }

    if not all(headers.values()):
        raise HTTPException(
            status_code=400,
            detail=(
                "Cabeçalhos de assinatura "
                "não encontrados."
            ),
        )

    try:
        evento = Webhook(secret).verify(
            corpo,
            headers,
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail=(
                "Assinatura do webhook inválida."
            ),
        )

    resultado = processar_evento_resend(
        svix_id=headers["svix-id"],
        evento=evento,
    )

    if not resultado.get("ok"):
        raise HTTPException(
            status_code=500,
            detail=resultado.get(
                "message",
                "Erro ao processar webhook.",
            ),
        )

    return {
        "received": True,
        **resultado,
    }
