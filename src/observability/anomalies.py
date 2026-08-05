"""
Detecção estatística de anomalias operacionais da INNA.

Utiliza:
- comparação entre período atual e linha de base;
- variações percentuais e em pontos percentuais;
- mediana e MAD para outliers robustos;
- classificação de severidade;
- recomendações técnicas determinísticas.

O módulo não acessa diretamente o banco e não depende de LLM.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from .analytics import preparar_eventos_analytics


SEVERIDADE_ORDEM = {
    "informativa": 1,
    "baixa": 2,
    "media": 3,
    "alta": 4,
    "critica": 5,
}


def calcular_mad(
    valores,
) -> float:
    """
    Calcula o Median Absolute Deviation.
    """
    serie = pd.to_numeric(
        pd.Series(valores),
        errors="coerce",
    ).dropna()

    if serie.empty:
        return 0.0

    mediana = float(serie.median())

    mad = float((serie - mediana).abs().median())

    return round(mad, 6)


def detectar_outliers_mad(
    valores,
    *,
    limite_score: float = 3.5,
) -> pd.DataFrame:
    """
    Detecta outliers usando Modified Z-Score com MAD.

    Retorna posição, valor e score robusto.
    """
    serie = pd.to_numeric(
        pd.Series(valores),
        errors="coerce",
    )

    validos = serie.dropna()

    if len(validos) < 3:
        return pd.DataFrame(
            columns=[
                "indice",
                "valor",
                "score_robusto",
            ]
        )

    mediana = float(validos.median())
    mad = calcular_mad(validos)

    if mad == 0:
        return pd.DataFrame(
            columns=[
                "indice",
                "valor",
                "score_robusto",
            ]
        )

    scores = 0.6745 * (validos - mediana) / mad

    mascara = scores.abs() > float(limite_score)

    resultado = pd.DataFrame(
        {
            "indice": validos[mascara].index,
            "valor": validos[mascara].values,
            "score_robusto": (scores[mascara].round(3).values),
        }
    )

    return resultado.reset_index(drop=True)


def _resumir_periodo(
    df: pd.DataFrame,
) -> dict[str, float]:
    """
    Calcula métricas comparáveis de um período.
    """
    if df.empty:
        return {
            "eventos": 0,
            "sucessos": 0,
            "falhas": 0,
            "taxa_falhas_percentual": 0.0,
            "confianca_media_percentual": 0.0,
            "duracao_media_ms": 0.0,
            "duracao_p95_ms": 0.0,
            "sem_tool_percentual": 0.0,
        }

    total = len(df)

    sucessos = int(df["sucesso"].sum() if "sucesso" in df.columns else 0)

    falhas = max(total - sucessos, 0)

    confiancas = pd.to_numeric(
        df.get(
            "confianca",
            pd.Series(dtype=float),
        ),
        errors="coerce",
    ).dropna()

    duracoes = pd.to_numeric(
        df.get(
            "duracao_ms",
            pd.Series(dtype=float),
        ),
        errors="coerce",
    ).dropna()

    sem_tool = int(
        (
            df.get(
                "tool_exibicao",
                pd.Series(dtype=str),
            )
            == "Sem Tool"
        ).sum()
    )

    return {
        "eventos": total,
        "sucessos": sucessos,
        "falhas": falhas,
        "taxa_falhas_percentual": round(
            (falhas / total) * 100,
            2,
        ),
        "confianca_media_percentual": (
            round(
                float(confiancas.mean()) * 100,
                2,
            )
            if not confiancas.empty
            else 0.0
        ),
        "duracao_media_ms": (
            round(float(duracoes.mean()), 3) if not duracoes.empty else 0.0
        ),
        "duracao_p95_ms": (
            round(
                float(duracoes.quantile(0.95)),
                3,
            )
            if not duracoes.empty
            else 0.0
        ),
        "sem_tool_percentual": round(
            (sem_tool / total) * 100,
            2,
        ),
    }


def _criar_anomalia(
    *,
    codigo: str,
    titulo: str,
    descricao: str,
    severidade: str,
    metrica: str,
    valor_atual: float,
    valor_referencia: float,
    recomendacao: str,
) -> dict[str, Any]:
    """
    Padroniza a estrutura de uma anomalia.
    """
    return {
        "codigo": codigo,
        "titulo": titulo,
        "descricao": descricao,
        "severidade": severidade,
        "ordem_severidade": SEVERIDADE_ORDEM[severidade],
        "metrica": metrica,
        "valor_atual": round(
            float(valor_atual),
            3,
        ),
        "valor_referencia": round(
            float(valor_referencia),
            3,
        ),
        "recomendacao": recomendacao,
    }


def detectar_anomalias_operacionais(
    df: pd.DataFrame | None,
    *,
    agora: datetime | None = None,
    horas_periodo_atual: int = 24,
    horas_linha_base: int = 168,
) -> dict[str, Any]:
    """
    Compara o período atual com uma linha de base anterior.

    A linha de base termina exatamente quando começa
    o período atual, evitando contaminação entre janelas.
    """
    base = preparar_eventos_analytics(df)

    if base.empty or "criado_em" not in base.columns:
        return {
            "ok": True,
            "tem_dados": False,
            "anomalias": [],
            "total_anomalias": 0,
            "maior_severidade": None,
            "periodo_atual": {},
            "linha_base": {},
            "outliers_duracao": pd.DataFrame(),
        }

    agora_utc = agora or datetime.now(timezone.utc)

    if agora_utc.tzinfo is None:
        agora_utc = agora_utc.replace(tzinfo=timezone.utc)
    else:
        agora_utc = agora_utc.astimezone(timezone.utc)

    inicio_atual = agora_utc - pd.Timedelta(hours=int(horas_periodo_atual))

    inicio_base = inicio_atual - pd.Timedelta(hours=int(horas_linha_base))

    atual = base[
        (base["criado_em"] >= inicio_atual) & (base["criado_em"] <= agora_utc)
    ].copy()

    historico = base[
        (base["criado_em"] >= inicio_base) & (base["criado_em"] < inicio_atual)
    ].copy()

    resumo_atual = _resumir_periodo(atual)
    resumo_base = _resumir_periodo(historico)

    anomalias: list[dict[str, Any]] = []

    # Falhas
    delta_falhas = (
        resumo_atual["taxa_falhas_percentual"] - resumo_base["taxa_falhas_percentual"]
    )

    if resumo_atual["falhas"] > 0 and delta_falhas >= 10:
        severidade = (
            "critica"
            if resumo_atual["taxa_falhas_percentual"] >= 40
            else "alta"
            if delta_falhas >= 25
            else "media"
        )

        anomalias.append(
            _criar_anomalia(
                codigo="aumento_taxa_falhas",
                titulo="Aumento da taxa de falhas",
                descricao=(
                    "A taxa de falhas do período atual "
                    f"aumentou {delta_falhas:.2f} pontos "
                    "percentuais em relação à linha de base."
                ),
                severidade=severidade,
                metrica="taxa_falhas_percentual",
                valor_atual=resumo_atual["taxa_falhas_percentual"],
                valor_referencia=resumo_base["taxa_falhas_percentual"],
                recomendacao=(
                    "Investigar erros recentes, Tool afetada, "
                    "dados ausentes e mudanças no Router."
                ),
            )
        )

    # Confiança
    queda_confianca = (
        resumo_base["confianca_media_percentual"]
        - resumo_atual["confianca_media_percentual"]
    )

    if resumo_base["confianca_media_percentual"] > 0 and queda_confianca >= 8:
        severidade = "alta" if queda_confianca >= 20 else "media"

        anomalias.append(
            _criar_anomalia(
                codigo="queda_confianca_router",
                titulo="Queda de confiança do Router",
                descricao=(
                    f"A confiança média caiu {queda_confianca:.2f} pontos percentuais."
                ),
                severidade=severidade,
                metrica="confianca_media_percentual",
                valor_atual=resumo_atual["confianca_media_percentual"],
                valor_referencia=resumo_base["confianca_media_percentual"],
                recomendacao=(
                    "Revisar perguntas com baixa confiança, "
                    "termos detectados e exemplos de intenção."
                ),
            )
        )

    # P95
    p95_atual = resumo_atual["duracao_p95_ms"]

    p95_base = resumo_base["duracao_p95_ms"]

    if p95_base > 0 and p95_atual > p95_base * 1.5 and p95_atual - p95_base >= 100:
        razao = p95_atual / p95_base

        severidade = "critica" if razao >= 5 else "alta" if razao >= 3 else "media"

        anomalias.append(
            _criar_anomalia(
                codigo="degradacao_p95",
                titulo="Degradação do P95",
                descricao=(
                    f"O P95 aumentou {razao:.2f} vezes em relação à linha de base."
                ),
                severidade=severidade,
                metrica="duracao_p95_ms",
                valor_atual=p95_atual,
                valor_referencia=p95_base,
                recomendacao=(
                    "Comparar traces, verificar cold start, "
                    "Gemini, RAG e conexões com o Neon."
                ),
            )
        )

    # Sem Tool
    delta_sem_tool = (
        resumo_atual["sem_tool_percentual"] - resumo_base["sem_tool_percentual"]
    )

    if resumo_atual["sem_tool_percentual"] >= 20 and delta_sem_tool >= 10:
        anomalias.append(
            _criar_anomalia(
                codigo="aumento_sem_tool",
                titulo="Aumento de execuções sem Tool",
                descricao=(
                    "O percentual de eventos sem Tool aumentou "
                    f"{delta_sem_tool:.2f} pontos percentuais."
                ),
                severidade=(
                    "alta" if resumo_atual["sem_tool_percentual"] >= 50 else "media"
                ),
                metrica="sem_tool_percentual",
                valor_atual=resumo_atual["sem_tool_percentual"],
                valor_referencia=resumo_base["sem_tool_percentual"],
                recomendacao=(
                    "Analisar perguntas não roteadas e avaliar "
                    "a criação de novas intenções ou Tools."
                ),
            )
        )

    # Volume normalizado por hora
    taxa_volume_atual = resumo_atual["eventos"] / max(int(horas_periodo_atual), 1)

    taxa_volume_base = resumo_base["eventos"] / max(int(horas_linha_base), 1)

    if taxa_volume_base > 0:
        variacao_volume = (
            (taxa_volume_atual - taxa_volume_base) / taxa_volume_base
        ) * 100

        if variacao_volume <= -60:
            anomalias.append(
                _criar_anomalia(
                    codigo="queda_volume",
                    titulo="Queda incomum no volume",
                    descricao=(
                        f"A média de eventos por hora caiu {abs(variacao_volume):.2f}%."
                    ),
                    severidade="baixa",
                    metrica="eventos_por_hora",
                    valor_atual=taxa_volume_atual,
                    valor_referencia=taxa_volume_base,
                    recomendacao=(
                        "Verificar disponibilidade da aplicação, "
                        "telemetria e comportamento dos usuários."
                    ),
                )
            )

        elif variacao_volume >= 200:
            anomalias.append(
                _criar_anomalia(
                    codigo="pico_volume",
                    titulo="Pico incomum de volume",
                    descricao=(
                        f"A média de eventos por hora aumentou {variacao_volume:.2f}%."
                    ),
                    severidade="baixa",
                    metrica="eventos_por_hora",
                    valor_atual=taxa_volume_atual,
                    valor_referencia=taxa_volume_base,
                    recomendacao=(
                        "Confirmar se o crescimento é esperado "
                        "e acompanhar recursos e limites da API."
                    ),
                )
            )

    # Outliers individuais
    outliers = detectar_outliers_mad(
        atual.get(
            "duracao_ms",
            pd.Series(dtype=float),
        )
    )

    if not outliers.empty:
        maior_valor = float(outliers["valor"].max())

        anomalias.append(
            _criar_anomalia(
                codigo="outliers_duracao",
                titulo="Execuções com duração fora do padrão",
                descricao=(
                    f"Foram detectadas {len(outliers)} "
                    "execução(ões) com duração atípica."
                ),
                severidade=("alta" if maior_valor >= 30000 else "media"),
                metrica="duracao_ms",
                valor_atual=maior_valor,
                valor_referencia=resumo_atual["duracao_media_ms"],
                recomendacao=(
                    "Abrir os traces correspondentes e verificar "
                    "a etapa responsável pela maior duração."
                ),
            )
        )

    anomalias = sorted(
        anomalias,
        key=lambda item: item["ordem_severidade"],
        reverse=True,
    )

    maior_severidade = anomalias[0]["severidade"] if anomalias else None

    return {
        "ok": True,
        "tem_dados": True,
        "anomalias": anomalias,
        "total_anomalias": len(anomalias),
        "maior_severidade": maior_severidade,
        "periodo_atual": resumo_atual,
        "linha_base": resumo_base,
        "outliers_duracao": outliers,
        "configuracao": {
            "horas_periodo_atual": int(horas_periodo_atual),
            "horas_linha_base": int(horas_linha_base),
        },
    }


__all__ = [
    "SEVERIDADE_ORDEM",
    "calcular_mad",
    "detectar_outliers_mad",
    "detectar_anomalias_operacionais",
]
