"""Adapter entre o protocolo A2A e o núcleo agentic INNA."""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from typing import Any

LOGGER = logging.getLogger(__name__)

SAFE_RUNTIME_ERROR = (
    "INNA could not complete the A2A request."
)

RuntimeExecutor = Callable[..., Mapping[str, Any]]


def _default_runtime_executor(
    message: str,
    *,
    usuario_id: str | None,
    idioma: str,
    moeda: str,
) -> Mapping[str, Any]:
    # Import tardio evita acoplar a inicialização
    # do servidor A2A ao grafo completo.
    from src.plataforma.orquestracao.graph import (
        executar_nucleo_inna,
    )

    return executar_nucleo_inna(
        message,
        usuario_id=usuario_id,
        idioma=idioma,
        moeda=moeda,
    )


class InnaNativeA2AAdapter:
    """Converte mensagem A2A em execução INNA."""

    def __init__(
        self,
        runtime_executor: RuntimeExecutor | None = None,
    ) -> None:
        self._runtime_executor = (
            runtime_executor
            or _default_runtime_executor
        )

    def execute(
        self,
        message: str,
    ) -> str:
        normalized = str(
            message or ""
        ).strip()

        if not normalized:
            return SAFE_RUNTIME_ERROR

        try:
            state = self._runtime_executor(
                normalized,
                usuario_id=None,
                idioma="pt",
                moeda="BRL",
            )
        except Exception:
            # Não inclui payload do usuário nem
            # detalhes internos na resposta A2A.
            LOGGER.error(
                "inna_native_a2a_runtime_failed"
            )
            return SAFE_RUNTIME_ERROR

        if not isinstance(
            state,
            Mapping,
        ):
            return SAFE_RUNTIME_ERROR

        response = str(
            state.get(
                "response",
                "",
            )
            or ""
        ).strip()

        if not response:
            return SAFE_RUNTIME_ERROR

        return response


__all__ = [
    "InnaNativeA2AAdapter",
    "RuntimeExecutor",
    "SAFE_RUNTIME_ERROR",
]
