from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


class TelegramUpdateContextError(
    ValueError
):
    """
    O update Telegram não possui identificadores
    confiáveis no formato esperado.
    """


def normalizar_update_id_telegram(
    value: Any,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
    ):
        raise TelegramUpdateContextError(
            "update_id Telegram inválido."
        )

    return value


def _normalizar_chat_id(
    value: Any,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value == 0
    ):
        raise TelegramUpdateContextError(
            "chat_id Telegram inválido."
        )

    return value


def _normalizar_message_id(
    value: Any,
) -> int | None:
    if value is None:
        return None

    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        raise TelegramUpdateContextError(
            "message_id Telegram inválido."
        )

    return value


@dataclass(
    frozen=True,
    slots=True,
)
class TrustedTelegramUpdateContext:
    update_id: int
    chat_id: int
    message_id: int | None = None

    @property
    def usuario_id(
        self,
    ) -> str:
        return (
            f"telegram:{self.chat_id}"
        )

    @property
    def request_id(
        self,
    ) -> str:
        return (
            f"telegram-update:"
            f"{self.update_id}"
        )

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "channel": "telegram",
            "identity_available": True,
            "request_available": True,
            "message_id_available": (
                self.message_id is not None
            ),
        }


def extrair_contexto_confiavel_telegram(
    update: Mapping[str, Any],
) -> TrustedTelegramUpdateContext:
    if not isinstance(
        update,
        Mapping,
    ):
        raise TelegramUpdateContextError(
            "Update Telegram inválido."
        )

    update_id = normalizar_update_id_telegram(
        update.get(
            "update_id"
        )
    )

    message = update.get(
        "message"
    )

    if not isinstance(
        message,
        Mapping,
    ):
        raise TelegramUpdateContextError(
            "Mensagem Telegram inválida."
        )

    chat = message.get(
        "chat"
    )

    if not isinstance(
        chat,
        Mapping,
    ):
        raise TelegramUpdateContextError(
            "Chat Telegram inválido."
        )

    chat_id = _normalizar_chat_id(
        chat.get(
            "id"
        )
    )

    message_id = _normalizar_message_id(
        message.get(
            "message_id"
        )
    )

    return TrustedTelegramUpdateContext(
        update_id=update_id,
        chat_id=chat_id,
        message_id=message_id,
    )


__all__ = [
    "TelegramUpdateContextError",
    "TrustedTelegramUpdateContext",
    "extrair_contexto_confiavel_telegram",
    "normalizar_update_id_telegram",
]
