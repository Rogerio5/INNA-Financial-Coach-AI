"""
Métricas executivas da observabilidade da INNA.

Este módulo transforma eventos operacionais em indicadores
consolidados para o Operations Center.

Não acessa diretamente o banco de dados. Ele recebe um
DataFrame, permitindo testes unitários rápidos e isolados.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd


def _dataframe_seguro(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Retorna uma cópia segura do DataFrame.
    """
    if df is None:
        return pd.DataFrame()

    return df.copy()


def _preparar_datas(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normaliza a coluna criado_em como datetime UTC.
    """
    if df.empty:
        return df

    resultado = df.copy()

    if "criado_em" not in resultado.columns:
        resultado["criado_em"] = pd.NaT
        return resultado

    resultado["criado_em"] = pd.to_datetime(
        resultado["criado_em"],
        errors="coerce",
        utc=True,
        format="mixed",
    )

    return resultado


def calcular_percentil_95(
    valores,
) -> float:
    """
    Calcula o percentil 95 de valores numéricos.
    """
    serie = pd.to_numeric(
        pd.Series(valores),
        errors="coerce",
    ).dropna()

    if serie.empty:
        return 0.0

    return round(
        float(serie.quantile(0.95)),
        3,
    )


def calcular_taxa_sucesso(
    total_sucesso: int,
    total_execucoes: int,
) -> float:
    """
    Calcula a taxa percentual de sucesso.
    """
    if total_execucoes <= 0:
        return 0.0

    return round(
        (int(total_sucesso) / int(total_execucoes)) * 100,
        2,
    )


def identificar_tool_mais_utilizada(
    df: pd.DataFrame,
) -> dict:
    """
    Identifica a Tool com maior quantidade de eventos.
    """
    if df.empty:
        return {
            "nome": None,
            "total": 0,
        }

    if "tool_label" not in df.columns and "tool_nome" not in df.columns:
        return {
            "nome": None,
            "total": 0,
        }

    if "tool_label" in df.columns:
        labels = df["tool_label"].copy()
    else:
        labels = pd.Series(
            None,
            index=df.index,
            dtype="object",
        )

    if "tool_nome" in df.columns:
        labels = labels.fillna(df["tool_nome"])

    labels = labels.dropna()

    if labels.empty:
        return {
            "nome": None,
            "total": 0,
        }

    contagem = labels.value_counts()

    return {
        "nome": str(contagem.index[0]),
        "total": int(contagem.iloc[0]),
    }


def calcular_metricas_executivas(
    df: pd.DataFrame | None,
    *,
    agora: datetime | None = None,
) -> dict:
    """
    Calcula os KPIs executivos do Operations Center.

    O parâmetro agora permite testes determinísticos.
    """
    base = _dataframe_seguro(df)
    base = _preparar_datas(base)

    agora_utc = agora or datetime.now(timezone.utc)

    if agora_utc.tzinfo is None:
        agora_utc = agora_utc.replace(tzinfo=timezone.utc)
    else:
        agora_utc = agora_utc.astimezone(timezone.utc)

    total_eventos = len(base)

    if "executada" in base.columns:
        executadas = base[base["executada"].fillna(False) == True]
    else:
        executadas = base

    total_execucoes = len(executadas)

    if "sucesso" in executadas.columns:
        total_sucesso = int(executadas["sucesso"].fillna(False).astype(bool).sum())
    else:
        total_sucesso = 0

    total_falhas = max(
        total_execucoes - total_sucesso,
        0,
    )

    taxa_sucesso = calcular_taxa_sucesso(
        total_sucesso,
        total_execucoes,
    )

    if "usuario_id" in base.columns:
        usuarios_ativos = int(base["usuario_id"].dropna().nunique())
    else:
        usuarios_ativos = 0

    if "confianca" in executadas.columns:
        confiancas = pd.to_numeric(
            executadas["confianca"],
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
    else:
        confianca_media = 0.0

    if "duracao_ms" in executadas.columns:
        duracoes = pd.to_numeric(
            executadas["duracao_ms"],
            errors="coerce",
        ).dropna()
    else:
        duracoes = pd.Series(dtype=float)

    duracao_media_ms = round(float(duracoes.mean()), 3) if not duracoes.empty else 0.0

    duracao_minima_ms = round(float(duracoes.min()), 3) if not duracoes.empty else 0.0

    duracao_maxima_ms = round(float(duracoes.max()), 3) if not duracoes.empty else 0.0

    duracao_p95_ms = calcular_percentil_95(duracoes)

    hoje_inicio = agora_utc.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    ultimas_24h_inicio = agora_utc - pd.Timedelta(hours=24)

    if "criado_em" in base.columns:
        datas_validas = base["criado_em"].notna()

        execucoes_hoje = int(
            (
                datas_validas
                & (base["criado_em"] >= hoje_inicio)
                & (base["criado_em"] <= agora_utc)
            ).sum()
        )

        execucoes_24h = int(
            (
                datas_validas
                & (base["criado_em"] >= ultimas_24h_inicio)
                & (base["criado_em"] <= agora_utc)
            ).sum()
        )

        ultima_data = base["criado_em"].max()

        ultima_execucao = ultima_data.isoformat() if pd.notna(ultima_data) else None
    else:
        execucoes_hoje = 0
        execucoes_24h = 0
        ultima_execucao = None

    tool_mais_utilizada = identificar_tool_mais_utilizada(executadas)

    return {
        "total_eventos": total_eventos,
        "total_execucoes": total_execucoes,
        "total_sucesso": total_sucesso,
        "total_falhas": total_falhas,
        "taxa_sucesso_percentual": (taxa_sucesso),
        "usuarios_ativos": usuarios_ativos,
        "execucoes_hoje": execucoes_hoje,
        "execucoes_ultimas_24h": (execucoes_24h),
        "confianca_media_percentual": (confianca_media),
        "duracao_media_ms": (duracao_media_ms),
        "duracao_minima_ms": (duracao_minima_ms),
        "duracao_maxima_ms": (duracao_maxima_ms),
        "duracao_p95_ms": duracao_p95_ms,
        "tool_mais_utilizada": (tool_mais_utilizada),
        "ultima_execucao": ultima_execucao,
    }


__all__ = [
    "calcular_percentil_95",
    "calcular_taxa_sucesso",
    "identificar_tool_mais_utilizada",
    "calcular_metricas_executivas",
]
