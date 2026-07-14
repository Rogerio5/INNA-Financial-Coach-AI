"""
Wrapper de observabilidade para chamadas de LLM.

Registra automaticamente:
- modelo;
- operação;
- duração;
- tokens de entrada e saída;
- sucesso ou falha;
- trace e usuário;
- custo estimado.

Não registra prompt, resposta ou dados financeiros do usuário.
"""

from __future__ import annotations

import time
from typing import Any, Callable, TypeVar

from .llm_costs import (
    extrair_tokens_resposta,
    registrar_consumo_llm,
)


T = TypeVar("T")


def executar_llm_observado(
    chamada: Callable[[], T],
    *,
    modelo: str,
    operacao: str,
    provider: str = "google",
    origem: str | None = None,
    usuario_id: str | None = None,
    trace_id: str | None = None,
    request_id: str | None = None,
    metadados: dict[str, Any] | None = None,
    registrar_falha: bool = True,
) -> T:
    """
    Executa uma chamada de LLM e registra sua telemetria.

    O retorno original da chamada é preservado.
    A exceção original também é propagada.
    """
    inicio = time.perf_counter()

    try:
        resposta = chamada()

        duracao_ms = round(
            (
                time.perf_counter()
                - inicio
            )
            * 1000,
            3,
        )

        tokens = extrair_tokens_resposta(
            resposta
        )

        registrar_consumo_llm(
            modelo=modelo,
            operacao=operacao,
            provider=provider,
            origem=origem,
            usuario_id=usuario_id,
            trace_id=trace_id,
            request_id=request_id,
            tokens_entrada=tokens[
                "tokens_entrada"
            ],
            tokens_saida=tokens[
                "tokens_saida"
            ],
            tokens_totais=tokens[
                "tokens_totais"
            ],
            duracao_ms=duracao_ms,
            sucesso=True,
            metadados={
                **(metadados or {}),
                "telemetria_automatica": True,
                "conteudo_registrado": False,
            },
        )

        return resposta

    except Exception as exc:
        duracao_ms = round(
            (
                time.perf_counter()
                - inicio
            )
            * 1000,
            3,
        )

        if registrar_falha:
            registrar_consumo_llm(
                modelo=modelo,
                operacao=operacao,
                provider=provider,
                origem=origem,
                usuario_id=usuario_id,
                trace_id=trace_id,
                request_id=request_id,
                tokens_entrada=0,
                tokens_saida=0,
                tokens_totais=0,
                duracao_ms=duracao_ms,
                sucesso=False,
                erro_tipo=type(exc).__name__,
                erro_mensagem=str(exc),
                metadados={
                    **(metadados or {}),
                    "telemetria_automatica": True,
                    "conteudo_registrado": False,
                },
            )

        raise


def executar_generate_content_observado(
    client: Any,
    *,
    modelo: str,
    contents: Any,
    config: Any = None,
    operacao: str = "generate_content",
    origem: str | None = None,
    usuario_id: str | None = None,
    trace_id: str | None = None,
    request_id: str | None = None,
    metadados: dict[str, Any] | None = None,
) -> Any:
    """
    Wrapper específico para google-genai:

    client.models.generate_content(...)
    """

    def chamada():
        argumentos = {
            "model": modelo,
            "contents": contents,
        }

        if config is not None:
            argumentos["config"] = config

        return client.models.generate_content(
            **argumentos
        )

    return executar_llm_observado(
        chamada,
        modelo=modelo,
        operacao=operacao,
        provider="google",
        origem=origem,
        usuario_id=usuario_id,
        trace_id=trace_id,
        request_id=request_id,
        metadados=metadados,
    )


__all__ = [
    "executar_llm_observado",
    "executar_generate_content_observado",
]
