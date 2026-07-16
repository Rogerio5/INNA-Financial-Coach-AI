"""
Ferramentas do agente RAG da INNA.

Este módulo adapta o RAG híbrido já existente para o núcleo
LangGraph, sem criar uma segunda base vetorial.
"""

from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, Field


class RagToolResult(BaseModel):
    ok: bool

    question: str
    language: str

    answer: str = ""
    sources: list[str] = Field(
        default_factory=list
    )

    mode: str = "unknown"
    retrieved_documents: int = 0
    duration_ms: int = 0

    raw_result: dict[str, Any] = Field(
        default_factory=dict
    )

    error_type: str | None = None
    error_message: str | None = None


def _normalizar_fontes(
    fontes: Any,
) -> list[str]:
    """
    Converte diferentes formatos de fontes para list[str].
    """
    if fontes is None:
        return []

    if isinstance(fontes, str):
        return [fontes]

    if not isinstance(fontes, (list, tuple)):
        return [str(fontes)]

    normalizadas: list[str] = []

    for fonte in fontes:
        if isinstance(fonte, str):
            valor = fonte.strip()

        elif isinstance(fonte, dict):
            valor = str(
                fonte.get("titulo")
                or fonte.get("title")
                or fonte.get("source")
                or fonte.get("fonte")
                or fonte.get("arquivo")
                or fonte.get("url")
                or fonte
            ).strip()

        else:
            valor = str(fonte).strip()

        if valor and valor not in normalizadas:
            normalizadas.append(valor)

    return normalizadas


def consultar_rag_inna(
    pergunta: str,
    *,
    idioma: str = "pt",
    top_k: int = 4,
) -> RagToolResult:
    """
    Executa o RAG híbrido existente da INNA.

    A função:
    - valida a pergunta;
    - executa answer_with_rag();
    - normaliza resposta, fontes e modo;
    - registra o log técnico do RAG;
    - nunca expõe stack trace ao usuário.
    """
    pergunta = str(pergunta or "").strip()
    idioma = str(idioma or "pt").strip().lower()

    try:
        top_k = max(
            1,
            min(int(top_k), 10),
        )
    except (TypeError, ValueError):
        top_k = 4

    if len(pergunta) < 3:
        return RagToolResult(
            ok=False,
            question=pergunta,
            language=idioma,
            error_type="ValidationError",
            error_message=(
                "A pergunta precisa possuir "
                "pelo menos 3 caracteres."
            ),
        )

    inicio = time.perf_counter()

    try:
        from src.rag_engine import (
            answer_with_rag,
            save_rag_log,
        )

        resultado = answer_with_rag(
            pergunta=pergunta,
            idioma=idioma,
            top_k=top_k,
        )

        if not isinstance(resultado, dict):
            resultado = {
                "resposta": str(resultado),
            }

        duracao_ms = int(
            (time.perf_counter() - inicio)
            * 1000
        )

        resposta = str(
            resultado.get("resposta")
            or resultado.get("answer")
            or resultado.get("response")
            or ""
        ).strip()

        fontes = _normalizar_fontes(
            resultado.get("fontes")
            or resultado.get("sources")
        )

        modo = str(
            resultado.get("modo")
            or resultado.get("mode")
            or "rag"
        )

        documentos = (
            resultado.get("documentos")
            or resultado.get("results")
            or resultado.get("contextos")
            or []
        )

        if isinstance(documentos, (list, tuple)):
            quantidade_documentos = len(
                documentos
            )

            if quantidade_documentos == 0:
                quantidade_documentos = len(
                    fontes
                )
        else:
            quantidade_documentos = len(
                fontes
            )

        try:
            save_rag_log(
                pergunta=pergunta,
                resultado=resultado,
                tempo_resposta_ms=duracao_ms,
            )
        except Exception:
            # A falha da telemetria não deve impedir
            # que o usuário receba a resposta.
            pass

        if not resposta:
            return RagToolResult(
                ok=False,
                question=pergunta,
                language=idioma,
                sources=fontes,
                mode=modo,
                retrieved_documents=(
                    quantidade_documentos
                ),
                duration_ms=duracao_ms,
                raw_result=resultado,
                error_type="EmptyRagAnswer",
                error_message=(
                    "O RAG não retornou uma "
                    "resposta utilizável."
                ),
            )

        return RagToolResult(
            ok=True,
            question=pergunta,
            language=idioma,
            answer=resposta,
            sources=fontes,
            mode=modo,
            retrieved_documents=(
                quantidade_documentos
            ),
            duration_ms=duracao_ms,
            raw_result=resultado,
        )

    except Exception as exc:
        duracao_ms = int(
            (time.perf_counter() - inicio)
            * 1000
        )

        return RagToolResult(
            ok=False,
            question=pergunta,
            language=idioma,
            duration_ms=duracao_ms,
            error_type=type(exc).__name__,
            error_message=str(exc)[:1000],
        )


__all__ = [
    "RagToolResult",
    "consultar_rag_inna",
]
