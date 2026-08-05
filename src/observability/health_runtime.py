"""
Coleta e consolidação do Health Score real da INNA.

Este módulo consulta as camadas existentes do projeto e converte
os resultados para o motor determinístico definido em health.py.

A coleta é tolerante a falhas: um componente indisponível reduz
seu próprio score, sem impedir a análise dos demais componentes.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd

from .analytics import (
    calcular_execucoes_sem_tool,
    calcular_percentis,
    preparar_eventos_analytics,
)
from .health import (
    calcular_health_score_global,
    calcular_score_infraestrutura,
    calcular_score_memoria,
    calcular_score_performance,
    calcular_score_rag,
    calcular_score_timeline,
    calcular_score_tools,
)


def _carregar_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        try:
            from dotenv import load_dotenv

            load_dotenv(dotenv_path=Path(".env"))

            database_url = os.getenv("DATABASE_URL")
        except Exception:
            database_url = None

    if not database_url:
        raise RuntimeError("DATABASE_URL não encontrada.")

    return database_url


def _consultar_total_memorias() -> dict[str, Any]:
    """
    Consulta quantidade de usuários com memória persistente.
    """
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(
            _carregar_database_url(),
            pool_pre_ping=True,
        )

        query = text("""
            SELECT COUNT(*) AS total
            FROM memoria_usuarios_inna;
        """)

        with engine.connect() as connection:
            resultado = connection.execute(query).scalar()

        engine.dispose()

        return {
            "ok": True,
            "total": int(resultado or 0),
            "message": ("Memórias consultadas com sucesso."),
        }

    except Exception as exc:
        return {
            "ok": False,
            "total": 0,
            "message": (f"Erro ao consultar memórias: {exc}"),
        }


def _extrair_status_componente(
    status_infraestrutura: dict[str, Any],
    chave: str,
) -> bool:
    """
    Extrai o estado booleano de um componente.
    """
    status = status_infraestrutura.get("status", {}).get(chave, {})

    return bool(status.get("ok"))


def _calcular_metricas_tools(
    df: pd.DataFrame | None,
    *,
    total_anomalias: int,
) -> dict[str, Any]:
    """
    Converte eventos das Tools em score e métricas.
    """
    base = preparar_eventos_analytics(df)

    if base.empty:
        score = calcular_score_tools(
            taxa_sucesso=0,
            confianca_media=0,
            percentual_sem_tool=100,
            total_anomalias=total_anomalias,
        )

        return {
            "score": score,
            "metricas": {
                "total_eventos": 0,
                "taxa_sucesso": 0.0,
                "confianca_media": 0.0,
                "percentual_sem_tool": 100.0,
                "p95_tools_ms": 0.0,
            },
        }

    total = len(base)

    sucessos = int(base["sucesso"].sum())

    taxa_sucesso = round(
        (sucessos / total) * 100,
        2,
    )

    confiancas = pd.to_numeric(
        base["confianca"],
        errors="coerce",
    ).dropna()

    confianca_media = (
        round(
            float(confiancas.mean()) * 100,
            2,
        )
        if not confiancas.empty
        else 0.0
    )

    sem_tool = calcular_execucoes_sem_tool(base)

    percentis = calcular_percentis(base["duracao_ms"])

    score = calcular_score_tools(
        taxa_sucesso=taxa_sucesso,
        confianca_media=confianca_media,
        percentual_sem_tool=float(sem_tool["percentual"]),
        total_anomalias=int(total_anomalias),
    )

    return {
        "score": score,
        "metricas": {
            "total_eventos": total,
            "taxa_sucesso": taxa_sucesso,
            "confianca_media": confianca_media,
            "percentual_sem_tool": float(sem_tool["percentual"]),
            "p95_tools_ms": float(percentis["p95"]),
        },
    }


def _calcular_metricas_timeline(
    traces_df: pd.DataFrame | None,
) -> dict[str, Any]:
    """
    Calcula métricas e score da Timeline.
    """
    if traces_df is None or traces_df.empty:
        score = calcular_score_timeline(
            traces_analisados=0,
            traces_com_falha=0,
            percentual_cold_start=0,
        )

        return {
            "score": score,
            "metricas": {
                "traces_analisados": 0,
                "traces_com_falha": 0,
                "percentual_cold_start": 0.0,
                "p95_trace_ms": 0.0,
                "p95_trace_sem_cold_start_ms": 0.0,
            },
        }

    base = traces_df.copy()

    duracoes = pd.to_numeric(
        base["duracao_total_ms"],
        errors="coerce",
    ).fillna(0)

    traces_analisados = len(base)

    traces_com_falha = int(
        (
            pd.to_numeric(
                base["total_falhas"],
                errors="coerce",
            ).fillna(0)
            > 0
        ).sum()
    )

    total_cold_start = int((duracoes >= 30000).sum())

    percentual_cold_start = round(
        (total_cold_start / traces_analisados) * 100,
        2,
    )

    p95_trace_ms = round(
        float(duracoes.quantile(0.95)),
        3,
    )

    duracoes_sem_cold_start = duracoes[duracoes < 30000]

    p95_trace_sem_cold_start_ms = (
        round(
            float(duracoes_sem_cold_start.quantile(0.95)),
            3,
        )
        if not duracoes_sem_cold_start.empty
        else 0.0
    )

    score = calcular_score_timeline(
        traces_analisados=traces_analisados,
        traces_com_falha=traces_com_falha,
        percentual_cold_start=(percentual_cold_start),
    )

    return {
        "score": score,
        "metricas": {
            "traces_analisados": (traces_analisados),
            "traces_com_falha": (traces_com_falha),
            "percentual_cold_start": (percentual_cold_start),
            "p95_trace_ms": p95_trace_ms,
            "p95_trace_sem_cold_start_ms": (p95_trace_sem_cold_start_ms),
        },
    }


def coletar_health_score_real(
    *,
    limite_eventos_tools: int = 1000,
    limite_traces: int = 100,
) -> dict[str, Any]:
    """
    Coleta todas as métricas reais e calcula o Health Score.
    """
    erros_coleta: list[str] = []

    # -----------------------------------------------------
    # Infraestrutura
    # -----------------------------------------------------
    try:
        from src.tools.observability import (
            carregar_eventos_tools,
            carregar_status_infraestrutura,
        )
    except ImportError:
        from tools.observability import (
            carregar_eventos_tools,
            carregar_status_infraestrutura,
        )

    status_infra = carregar_status_infraestrutura()

    if not status_infra.get("ok"):
        erros_coleta.append(
            status_infra.get(
                "message",
                "Falha ao carregar infraestrutura.",
            )
        )

    score_infra = calcular_score_infraestrutura(
        total_componentes=int(
            status_infra.get(
                "total_componentes",
                0,
            )
        ),
        total_operacionais=int(
            status_infra.get(
                "total_operacionais",
                0,
            )
        ),
    )

    # -----------------------------------------------------
    # Eventos das Tools e anomalias
    # -----------------------------------------------------
    eventos_resultado = carregar_eventos_tools(limite=int(limite_eventos_tools))

    eventos_df = eventos_resultado.get("df")

    if not eventos_resultado.get("ok"):
        erros_coleta.append(
            eventos_resultado.get(
                "message",
                "Falha ao carregar eventos das Tools.",
            )
        )

    try:
        from .anomalies import (
            detectar_anomalias_operacionais,
        )

        resultado_anomalias = detectar_anomalias_operacionais(eventos_df)

        total_anomalias = int(
            resultado_anomalias.get(
                "total_anomalias",
                0,
            )
        )

    except Exception as exc:
        resultado_anomalias = {
            "ok": False,
            "total_anomalias": 0,
            "anomalias": [],
        }

        total_anomalias = 0

        erros_coleta.append(f"Erro ao calcular anomalias: {exc}")

    tools_resultado = _calcular_metricas_tools(
        eventos_df,
        total_anomalias=total_anomalias,
    )

    # -----------------------------------------------------
    # RAG / pgvector
    # -----------------------------------------------------
    try:
        try:
            from src.services.rag.vector_store import (
                carregar_resumo_embeddings,
            )
        except ImportError:
            from services.rag.vector_store import (
                carregar_resumo_embeddings,
            )

        resumo_rag = carregar_resumo_embeddings()

        if not resumo_rag.get("ok"):
            erros_coleta.append(
                resumo_rag.get(
                    "message",
                    "Falha ao carregar resumo RAG.",
                )
            )

    except Exception as exc:
        resumo_rag = {
            "ok": False,
        }

        erros_coleta.append(f"Erro ao consultar o RAG: {exc}")

    documentos_ativos = int(
        resumo_rag.get(
            "documentos_ativos_com_embeddings",
            resumo_rag.get(
                "documentos_ativos",
                0,
            ),
        )
    )

    documentos_com_embeddings = int(
        resumo_rag.get(
            "documentos_com_embeddings",
            0,
        )
    )

    embeddings_ativos = int(
        resumo_rag.get(
            "embeddings_ativos",
            0,
        )
    )

    embeddings_inativos = int(
        resumo_rag.get(
            "embeddings_inativos",
            0,
        )
    )

    score_rag = calcular_score_rag(
        documentos_ativos=documentos_ativos,
        documentos_com_embeddings=(documentos_com_embeddings),
        embeddings_ativos=embeddings_ativos,
        embeddings_inativos=(embeddings_inativos),
    )

    # -----------------------------------------------------
    # Memória
    # -----------------------------------------------------
    memorias = _consultar_total_memorias()

    memoria_disponivel = _extrair_status_componente(
        status_infra,
        "memory_table",
    )

    score_memoria = calcular_score_memoria(
        tabela_disponivel=(memoria_disponivel),
        total_usuarios_com_memoria=int(
            memorias.get(
                "total",
                0,
            )
        ),
        erros_memoria=(0 if memorias.get("ok") else 1),
    )

    if not memorias.get("ok"):
        erros_coleta.append(
            memorias.get(
                "message",
                "Falha ao consultar memória.",
            )
        )

    # -----------------------------------------------------
    # Timeline
    # -----------------------------------------------------
    try:
        from .timeline import (
            carregar_traces_recentes,
        )

        traces_resultado = carregar_traces_recentes(limite=int(limite_traces))

        traces_df = traces_resultado.get("df")

        if not traces_resultado.get("ok"):
            erros_coleta.append(
                traces_resultado.get(
                    "message",
                    "Falha ao carregar traces.",
                )
            )

    except Exception as exc:
        traces_df = pd.DataFrame()

        erros_coleta.append(f"Erro ao consultar a Timeline: {exc}")

    timeline_resultado = _calcular_metricas_timeline(traces_df)

    # -----------------------------------------------------
    # Performance
    # -----------------------------------------------------
    score_performance = calcular_score_performance(
        p95_tools_ms=float(tools_resultado["metricas"]["p95_tools_ms"]),
        p95_trace_ms=float(
            timeline_resultado["metricas"]["p95_trace_sem_cold_start_ms"]
        ),
    )

    componentes = {
        "tools": tools_resultado["score"],
        "rag": score_rag,
        "memoria": score_memoria,
        "infraestrutura": score_infra,
        "timeline": timeline_resultado["score"],
        "performance": score_performance,
    }

    health_global = calcular_health_score_global(componentes)

    return {
        "ok": len(erros_coleta) == 0,
        "message": (
            "Health Score calculado com sucesso."
            if not erros_coleta
            else ("Health Score calculado com alertas de coleta.")
        ),
        "health": health_global,
        "componentes_brutos": componentes,
        "metricas": {
            "tools": tools_resultado["metricas"],
            "rag": {
                "documentos_ativos": (documentos_ativos),
                "documentos_com_embeddings": (documentos_com_embeddings),
                "embeddings_ativos": (embeddings_ativos),
                "embeddings_inativos": (embeddings_inativos),
            },
            "memoria": {
                "tabela_disponivel": (memoria_disponivel),
                "usuarios_com_memoria": int(
                    memorias.get(
                        "total",
                        0,
                    )
                ),
            },
            "infraestrutura": {
                "total_componentes": int(
                    status_infra.get(
                        "total_componentes",
                        0,
                    )
                ),
                "total_operacionais": int(
                    status_infra.get(
                        "total_operacionais",
                        0,
                    )
                ),
                "status": status_infra.get(
                    "status",
                    {},
                ),
            },
            "timeline": timeline_resultado["metricas"],
        },
        "anomalias": resultado_anomalias,
        "erros_coleta": erros_coleta,
    }


__all__ = [
    "coletar_health_score_real",
]
