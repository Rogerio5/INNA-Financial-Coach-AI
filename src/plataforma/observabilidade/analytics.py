"""
Analytics avançado das Tools da INNA.

O módulo recebe DataFrames de eventos e produz indicadores
operacionais sem acessar diretamente o banco de dados.

Isso permite:
- testes unitários rápidos;
- reutilização em Streamlit, API ou relatórios;
- separação entre persistência e análise.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd


def _dataframe_seguro(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame()

    return df.copy()


def _serie_numerica(
    valores,
) -> pd.Series:
    return pd.to_numeric(
        pd.Series(valores),
        errors="coerce",
    ).dropna()


def calcular_percentis(
    valores,
) -> dict[str, float]:
    """
    Calcula P50, P95 e P99.
    """
    serie = _serie_numerica(
        valores
    )

    if serie.empty:
        return {
            "p50": 0.0,
            "p95": 0.0,
            "p99": 0.0,
        }

    return {
        "p50": round(
            float(serie.quantile(0.50)),
            3,
        ),
        "p95": round(
            float(serie.quantile(0.95)),
            3,
        ),
        "p99": round(
            float(serie.quantile(0.99)),
            3,
        ),
    }


def preparar_eventos_analytics(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Normaliza os campos usados nas análises.
    """
    base = _dataframe_seguro(df)

    if base.empty:
        return base

    if "criado_em" in base.columns:
        base["criado_em"] = pd.to_datetime(
            base["criado_em"],
            errors="coerce",
            utc=True,
            format="mixed",
        )

    if "duracao_ms" in base.columns:
        base["duracao_ms"] = pd.to_numeric(
            base["duracao_ms"],
            errors="coerce",
        )

    if "confianca" in base.columns:
        base["confianca"] = pd.to_numeric(
            base["confianca"],
            errors="coerce",
        )

    if "sucesso" in base.columns:
        base["sucesso"] = (
            base["sucesso"]
            .fillna(False)
            .astype(bool)
        )

    if "executada" in base.columns:
        base["executada"] = (
            base["executada"]
            .fillna(False)
            .astype(bool)
        )

    if "tool_label" in base.columns:
        labels = base["tool_label"].copy()
    else:
        labels = pd.Series(
            None,
            index=base.index,
            dtype="object",
        )

    if "tool_nome" in base.columns:
        labels = labels.fillna(
            base["tool_nome"]
        )

    base["tool_exibicao"] = labels.fillna(
        "Sem Tool"
    )

    return base


def calcular_ranking_tools(
    df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Produz ranking completo por Tool.
    """
    base = preparar_eventos_analytics(
        df
    )

    if base.empty:
        return pd.DataFrame()

    agrupado = (
        base.groupby(
            "tool_exibicao",
            dropna=False,
        )
        .agg(
            execucoes=("id", "count"),
            sucessos=("sucesso", "sum"),
            falhas=(
                "sucesso",
                lambda serie: int(
                    (~serie.astype(bool)).sum()
                ),
            ),
            confianca_media=(
                "confianca",
                "mean",
            ),
            duracao_media_ms=(
                "duracao_ms",
                "mean",
            ),
            duracao_minima_ms=(
                "duracao_ms",
                "min",
            ),
            duracao_maxima_ms=(
                "duracao_ms",
                "max",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "tool_exibicao": "ferramenta",
            }
        )
    )

    agrupado["taxa_sucesso_percentual"] = (
        agrupado.apply(
            lambda row: (
                round(
                    (
                        float(row["sucessos"])
                        / float(row["execucoes"])
                    )
                    * 100,
                    2,
                )
                if row["execucoes"] > 0
                else 0.0
            ),
            axis=1,
        )
    )

    agrupado["confianca_media_percentual"] = (
        agrupado["confianca_media"]
        .fillna(0)
        .mul(100)
        .round(2)
    )

    for coluna in [
        "duracao_media_ms",
        "duracao_minima_ms",
        "duracao_maxima_ms",
    ]:
        agrupado[coluna] = (
            agrupado[coluna]
            .fillna(0)
            .round(3)
        )

    percentis = []

    for ferramenta, grupo in base.groupby(
        "tool_exibicao"
    ):
        valores = calcular_percentis(
            grupo["duracao_ms"]
        )

        percentis.append({
            "ferramenta": ferramenta,
            "p50_ms": valores["p50"],
            "p95_ms": valores["p95"],
            "p99_ms": valores["p99"],
        })

    if percentis:
        agrupado = agrupado.merge(
            pd.DataFrame(percentis),
            on="ferramenta",
            how="left",
        )
    else:
        agrupado["p50_ms"] = 0.0
        agrupado["p95_ms"] = 0.0
        agrupado["p99_ms"] = 0.0

    return agrupado.sort_values(
        by=[
            "execucoes",
            "taxa_sucesso_percentual",
        ],
        ascending=[
            False,
            False,
        ],
    ).reset_index(drop=True)


def calcular_distribuicao_coluna(
    df: pd.DataFrame | None,
    coluna: str,
    *,
    valor_padrao: str = "Não informado",
) -> pd.DataFrame:
    """
    Gera frequência absoluta e percentual.
    """
    base = preparar_eventos_analytics(
        df
    )

    if base.empty or coluna not in base.columns:
        return pd.DataFrame(
            columns=[
                coluna,
                "total",
                "percentual",
            ]
        )

    serie = (
        base[coluna]
        .fillna(valor_padrao)
        .astype(str)
    )

    resultado = (
        serie.value_counts()
        .rename_axis(coluna)
        .reset_index(name="total")
    )

    total_geral = int(
        resultado["total"].sum()
    )

    resultado["percentual"] = (
        resultado["total"]
        .apply(
            lambda valor: (
                round(
                    (
                        int(valor)
                        / total_geral
                    )
                    * 100,
                    2,
                )
                if total_geral > 0
                else 0.0
            )
        )
    )

    return resultado


def calcular_execucoes_sem_tool(
    df: pd.DataFrame | None,
) -> dict[str, Any]:
    """
    Identifica eventos sem Tool reconhecida.
    """
    base = preparar_eventos_analytics(
        df
    )

    if base.empty:
        return {
            "total": 0,
            "percentual": 0.0,
        }

    mascara = (
        base["tool_exibicao"]
        == "Sem Tool"
    )

    total_sem_tool = int(
        mascara.sum()
    )

    return {
        "total": total_sem_tool,
        "percentual": round(
            (
                total_sem_tool
                / len(base)
            )
            * 100,
            2,
        ),
    }


def calcular_serie_temporal_analytics(
    df: pd.DataFrame | None,
    frequencia: str = "D",
) -> pd.DataFrame:
    """
    Consolida execuções ao longo do tempo.

    Frequências úteis:
    - H: hora
    - D: dia
    - W: semana
    - ME: mês
    """
    base = preparar_eventos_analytics(
        df
    )

    if (
        base.empty
        or "criado_em" not in base.columns
    ):
        return pd.DataFrame()

    base = base.dropna(
        subset=["criado_em"]
    )

    if base.empty:
        return pd.DataFrame()

    base = base.set_index(
        "criado_em"
    )

    serie = (
        base.resample(frequencia)
        .agg(
            execucoes=("id", "count"),
            sucessos=("sucesso", "sum"),
            duracao_media_ms=(
                "duracao_ms",
                "mean",
            ),
            confianca_media=(
                "confianca",
                "mean",
            ),
            usuarios_ativos=(
                "usuario_id",
                "nunique",
            ),
        )
        .reset_index()
    )

    serie["falhas"] = (
        serie["execucoes"]
        - serie["sucessos"]
    )

    serie["taxa_sucesso_percentual"] = (
        serie.apply(
            lambda row: (
                round(
                    (
                        row["sucessos"]
                        / row["execucoes"]
                    )
                    * 100,
                    2,
                )
                if row["execucoes"] > 0
                else 0.0
            ),
            axis=1,
        )
    )

    serie["duracao_media_ms"] = (
        serie["duracao_media_ms"]
        .fillna(0)
        .round(3)
    )

    serie["confianca_media_percentual"] = (
        serie["confianca_media"]
        .fillna(0)
        .mul(100)
        .round(2)
    )

    return serie


def comparar_periodos(
    df: pd.DataFrame | None,
    *,
    agora: datetime | None = None,
    horas: int = 24,
) -> dict[str, Any]:
    """
    Compara o período atual com o período anterior.
    """
    base = preparar_eventos_analytics(
        df
    )

    agora_utc = agora or datetime.now(
        timezone.utc
    )

    if agora_utc.tzinfo is None:
        agora_utc = agora_utc.replace(
            tzinfo=timezone.utc
        )
    else:
        agora_utc = agora_utc.astimezone(
            timezone.utc
        )

    if (
        base.empty
        or "criado_em" not in base.columns
    ):
        return {
            "periodo_atual": {},
            "periodo_anterior": {},
            "variacao_execucoes_percentual": 0.0,
            "variacao_falhas_percentual": 0.0,
            "variacao_duracao_percentual": 0.0,
        }

    inicio_atual = agora_utc - pd.Timedelta(
        hours=horas
    )

    inicio_anterior = (
        inicio_atual
        - pd.Timedelta(hours=horas)
    )

    atual = base[
        (base["criado_em"] >= inicio_atual)
        & (base["criado_em"] <= agora_utc)
    ]

    anterior = base[
        (
            base["criado_em"]
            >= inicio_anterior
        )
        & (
            base["criado_em"]
            < inicio_atual
        )
    ]

    def resumir(
        periodo: pd.DataFrame,
    ) -> dict[str, float]:
        if periodo.empty:
            return {
                "execucoes": 0,
                "falhas": 0,
                "duracao_media_ms": 0.0,
            }

        falhas = int(
            (~periodo["sucesso"]).sum()
        )

        duracao_media = (
            round(
                float(
                    periodo[
                        "duracao_ms"
                    ].dropna().mean()
                ),
                3,
            )
            if periodo[
                "duracao_ms"
            ].notna().any()
            else 0.0
        )

        return {
            "execucoes": len(periodo),
            "falhas": falhas,
            "duracao_media_ms": duracao_media,
        }

    resumo_atual = resumir(atual)
    resumo_anterior = resumir(anterior)

    def variacao(
        atual_valor: float,
        anterior_valor: float,
    ) -> float:
        if anterior_valor == 0:
            return (
                100.0
                if atual_valor > 0
                else 0.0
            )

        return round(
            (
                (
                    atual_valor
                    - anterior_valor
                )
                / anterior_valor
            )
            * 100,
            2,
        )

    return {
        "periodo_atual": resumo_atual,
        "periodo_anterior": resumo_anterior,
        "variacao_execucoes_percentual": variacao(
            resumo_atual["execucoes"],
            resumo_anterior["execucoes"],
        ),
        "variacao_falhas_percentual": variacao(
            resumo_atual["falhas"],
            resumo_anterior["falhas"],
        ),
        "variacao_duracao_percentual": variacao(
            resumo_atual["duracao_media_ms"],
            resumo_anterior["duracao_media_ms"],
        ),
    }


__all__ = [
    "calcular_percentis",
    "preparar_eventos_analytics",
    "calcular_ranking_tools",
    "calcular_distribuicao_coluna",
    "calcular_execucoes_sem_tool",
    "calcular_serie_temporal_analytics",
    "comparar_periodos",
]
