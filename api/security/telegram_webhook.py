from __future__ import annotations

import hmac
import os
import re
from dataclasses import dataclass
from typing import Annotated

from fastapi import (
    Header,
    HTTPException,
    status,
)


TELEGRAM_SECRET_HEADER = (
    "X-Telegram-Bot-Api-Secret-Token"
)

TELEGRAM_SECRET_PATTERN = re.compile(
    r"^[A-Za-z0-9_-]{32,256}$"
)


class TelegramWebhookSecurityError(
    RuntimeError
):
    """
    O webhook Telegram não foi autenticado.
    """


class TelegramWebhookConfigurationError(
    RuntimeError
):
    """
    A configuração do segredo está ausente
    ou inválida.
    """


@dataclass(
    frozen=True,
    slots=True,
)
class TrustedTelegramWebhookContext:
    authenticated: bool = True
    authentication_method: str = (
        "telegram_secret_token"
    )

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "authenticated": (
                self.authenticated
            ),
            "authentication_method": (
                self.authentication_method
            ),
        }


def obter_segredo_webhook_telegram(
    explicit_secret: str | None = None,
) -> str:
    raw_secret = (
        explicit_secret
        if explicit_secret is not None
        else os.getenv(
            "TELEGRAM_WEBHOOK_SECRET",
            "",
        )
    )

    if not isinstance(
        raw_secret,
        str,
    ):
        raise (
            TelegramWebhookConfigurationError(
                "Configuração do webhook "
                "Telegram inválida."
            )
        )

    secret = raw_secret.strip()

    if not TELEGRAM_SECRET_PATTERN.fullmatch(
        secret
    ):
        raise (
            TelegramWebhookConfigurationError(
                "Configuração do webhook "
                "Telegram inválida."
            )
        )

    return secret


def verificar_segredo_webhook_telegram(
    received_secret: str | None,
    *,
    expected_secret: str | None = None,
) -> TrustedTelegramWebhookContext:
    configured_secret = (
        obter_segredo_webhook_telegram(
            expected_secret
        )
    )

    if not isinstance(
        received_secret,
        str,
    ):
        raise TelegramWebhookSecurityError(
            "Webhook Telegram não autenticado."
        )

    received = received_secret.strip()

    if not TELEGRAM_SECRET_PATTERN.fullmatch(
        received
    ):
        raise TelegramWebhookSecurityError(
            "Webhook Telegram não autenticado."
        )

    if not hmac.compare_digest(
        received,
        configured_secret,
    ):
        raise TelegramWebhookSecurityError(
            "Webhook Telegram não autenticado."
        )

    return TrustedTelegramWebhookContext()


async def require_trusted_telegram_webhook(
    secret_token: Annotated[
        str | None,
        Header(
            alias=TELEGRAM_SECRET_HEADER,
        ),
    ] = None,
) -> TrustedTelegramWebhookContext:
    try:
        return (
            verificar_segredo_webhook_telegram(
                secret_token
            )
        )

    except TelegramWebhookConfigurationError:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "Autenticação do webhook "
                "Telegram indisponível."
            ),
        ) from None

    except TelegramWebhookSecurityError:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Webhook Telegram "
                "não autenticado."
            ),
        ) from None


__all__ = [
    "TELEGRAM_SECRET_HEADER",
    "TelegramWebhookConfigurationError",
    "TelegramWebhookSecurityError",
    "TrustedTelegramWebhookContext",
    "obter_segredo_webhook_telegram",
    "require_trusted_telegram_webhook",
    "verificar_segredo_webhook_telegram",
]
