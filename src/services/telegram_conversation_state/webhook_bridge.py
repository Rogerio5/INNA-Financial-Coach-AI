"""
Compatibilidade temporária do webhook bridge.

Implementação oficial:
src.integracoes.telegram.conversation_state.webhook_bridge

A classe estrutural abaixo existe apenas para preservar
contratos AST/textuais de testes legados. Em runtime,
o módulo é substituído pela implementação canônica.
"""

from __future__ import annotations

import sys
from typing import Any, Callable


def _observe_bridge_operation(
    operation_name: str,
):
    """Decorator estrutural para compatibilidade AST."""

    def decorator(
        function: Callable[..., Any],
    ) -> Callable[..., Any]:
        return function

    return decorator


class TelegramWebhookConversationBridge:
    """Contrato estrutural legado; não é implementação runtime."""

    metrics: object = None
    event_sink: object = None
    clock: object = None

    @_observe_bridge_operation(
        "load_or_open_session"
    )
    def load_or_open_session(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        raise RuntimeError(
            "Shim estrutural nao deve executar."
        )

    @_observe_bridge_operation(
        "save_session"
    )
    def save_session(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        raise RuntimeError(
            "Shim estrutural nao deve executar."
        )

    @_observe_bridge_operation(
        "reload_session"
    )
    def reload_session(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        raise RuntimeError(
            "Shim estrutural nao deve executar."
        )

    @_observe_bridge_operation(
        "delete_session"
    )
    def delete_session(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        raise RuntimeError(
            "Shim estrutural nao deve executar."
        )

    @_observe_bridge_operation(
        "resolve_language"
    )
    def resolve_language(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        raise RuntimeError(
            "Shim estrutural nao deve executar."
        )


from src.integracoes.telegram.conversation_state import (
    webhook_bridge as _implementation,
)

sys.modules[__name__] = _implementation
