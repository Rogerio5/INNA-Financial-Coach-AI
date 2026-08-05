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
from collections.abc import Callable
from typing import Any, TypeVar

from .llm_costs import (
    extrair_tokens_resposta,
    registrar_consumo_llm,
)
from .phoenix_privacy import hash_identifier
from .phoenix_runtime import traced_operation

T = TypeVar("T")


def _phoenix_identifier(
    value: str | None,
) -> str | None:
    """
    Converte identificadores internos em hashes irreversíveis.

    O valor original nunca é enviado ao Phoenix.
    """

    if value is None:
        return None

    normalized = str(value).strip()

    if not normalized:
        return None

    return hash_identifier(normalized)


def _build_phoenix_attributes(
    *,
    modelo: str,
    operacao: str,
    provider: str,
    origem: str | None,
    usuario_id: str | None,
    trace_id: str | None,
    request_id: str | None,
) -> dict[str, Any]:
    """
    Cria somente atributos técnicos permitidos.

    O dicionário livre de metadados não é exportado ao Phoenix,
    evitando vazamento acidental de conteúdo de negócio.
    """

    attributes: dict[str, Any] = {
        # Convenções oficiais OpenInference/Phoenix.
        "openinference.span.kind": "LLM",
        "llm.model_name": modelo,
        "llm.provider": provider,
        # Metadados técnicos próprios da INNA.
        "inna.llm.operation": operacao,
        "inna.llm.origin": origem or "unknown",
        "telemetry.layer": "llm_tracking",
        "privacy.content_exported": False,
    }

    user_hash = _phoenix_identifier(usuario_id)
    trace_hash = _phoenix_identifier(trace_id)
    request_hash = _phoenix_identifier(request_id)

    if user_hash:
        attributes["enduser.id_hash"] = user_hash

    if trace_hash:
        attributes["inna.trace_id_hash"] = trace_hash

    if request_hash:
        attributes["inna.request_id_hash"] = request_hash

    return attributes


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

    phoenix_attributes = _build_phoenix_attributes(
        modelo=modelo,
        operacao=operacao,
        provider=provider,
        origem=origem,
        usuario_id=usuario_id,
        trace_id=trace_id,
        request_id=request_id,
    )

    span_name = f"inna.llm.{provider}.{operacao}"

    with traced_operation(
        span_name,
        attributes=phoenix_attributes,
        instrumentation_name="inna.observability.llm",
    ) as span:
        try:
            resposta = chamada()

            duracao_ms = round(
                (time.perf_counter() - inicio) * 1000,
                3,
            )

            tokens = extrair_tokens_resposta(resposta)

            span.set_attribute(
                "llm.token_count.prompt",
                int(tokens["tokens_entrada"]),
            )
            span.set_attribute(
                "llm.token_count.completion",
                int(tokens["tokens_saida"]),
            )
            span.set_attribute(
                "llm.token_count.total",
                int(tokens["tokens_totais"]),
            )
            span.set_attribute(
                "llm.duration_ms",
                duracao_ms,
            )
            span.set_attribute(
                "llm.success",
                True,
            )

            registrar_consumo_llm(
                modelo=modelo,
                operacao=operacao,
                provider=provider,
                origem=origem,
                usuario_id=usuario_id,
                trace_id=trace_id,
                request_id=request_id,
                tokens_entrada=tokens["tokens_entrada"],
                tokens_saida=tokens["tokens_saida"],
                tokens_totais=tokens["tokens_totais"],
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
                (time.perf_counter() - inicio) * 1000,
                3,
            )

            span.set_attribute(
                "llm.success",
                False,
            )
            span.set_attribute(
                "llm.duration_ms",
                duracao_ms,
            )
            span.set_attribute(
                "llm.error_type",
                type(exc).__name__,
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

    O argumento contents é encaminhado ao Gemini, mas nunca é
    transformado em atributo de telemetria.
    """

    def chamada():
        argumentos = {
            "model": modelo,
            "contents": contents,
        }

        if config is not None:
            argumentos["config"] = config

        return client.models.generate_content(**argumentos)

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
