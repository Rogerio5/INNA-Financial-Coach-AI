"""
Health Score global da INNA Financial Coach AI.

Consolida a saúde de:

- Tools;
- RAG;
- memória persistente;
- infraestrutura;
- Timeline;
- performance.

O cálculo é determinístico, auditável e independente de LLM.
"""

from __future__ import annotations

from typing import Any


PESOS_COMPONENTES = {
    "tools": 0.25,
    "rag": 0.20,
    "memoria": 0.15,
    "infraestrutura": 0.15,
    "timeline": 0.10,
    "performance": 0.15,
}


def limitar_score(
    valor: float,
) -> float:
    """
    Mantém o score entre 0 e 100.
    """
    return round(
        max(
            0.0,
            min(
                100.0,
                float(valor),
            ),
        ),
        1,
    )


def classificar_score(
    score: float,
) -> dict[str, str]:
    """
    Classifica um score operacional.
    """
    valor = limitar_score(score)

    if valor >= 95:
        return {
            "classificacao": "Excelente",
            "status": "saudavel",
            "icone": "🟢",
        }

    if valor >= 85:
        return {
            "classificacao": "Boa",
            "status": "atencao_leve",
            "icone": "🟡",
        }

    if valor >= 70:
        return {
            "classificacao": "Atenção",
            "status": "atencao",
            "icone": "🟠",
        }

    return {
        "classificacao": "Crítica",
        "status": "critico",
        "icone": "🔴",
    }


def calcular_score_tools(
    *,
    taxa_sucesso: float,
    confianca_media: float,
    percentual_sem_tool: float,
    total_anomalias: int = 0,
) -> dict[str, Any]:
    """
    Calcula o score das Tools.
    """
    score = 100.0
    penalidades = []

    if taxa_sucesso < 99:
        penalidade = min(
            (99 - taxa_sucesso) * 2,
            35,
        )

        score -= penalidade

        penalidades.append(
            f"Taxa de sucesso: -{penalidade:.1f}"
        )

    if confianca_media < 85:
        penalidade = min(
            (85 - confianca_media) * 1.2,
            20,
        )

        score -= penalidade

        penalidades.append(
            f"Confiança do Router: -{penalidade:.1f}"
        )

    if percentual_sem_tool > 15:
        penalidade = min(
            (percentual_sem_tool - 15) * 0.8,
            20,
        )

        score -= penalidade

        penalidades.append(
            f"Eventos sem Tool: -{penalidade:.1f}"
        )

    if total_anomalias > 0:
        penalidade = min(
            total_anomalias * 3,
            15,
        )

        score -= penalidade

        penalidades.append(
            f"Anomalias: -{penalidade:.1f}"
        )

    score = limitar_score(score)

    return {
        "score": score,
        "penalidades": penalidades,
        **classificar_score(score),
    }


def calcular_score_infraestrutura(
    *,
    total_componentes: int,
    total_operacionais: int,
) -> dict[str, Any]:
    """
    Calcula o score de infraestrutura.
    """
    if total_componentes <= 0:
        score = 0.0
    else:
        score = (
            total_operacionais
            / total_componentes
        ) * 100

    score = limitar_score(score)

    return {
        "score": score,
        "componentes": int(total_componentes),
        "operacionais": int(total_operacionais),
        **classificar_score(score),
    }


def calcular_score_rag(
    *,
    documentos_ativos: int,
    documentos_com_embeddings: int,
    embeddings_ativos: int,
    embeddings_inativos: int,
) -> dict[str, Any]:
    """
    Calcula a saúde básica da camada RAG.
    """
    score = 100.0
    penalidades = []

    if documentos_ativos <= 0:
        score -= 40
        penalidades.append(
            "Nenhum documento ativo: -40"
        )

    if documentos_com_embeddings < documentos_ativos:
        faltantes = (
            documentos_ativos
            - documentos_com_embeddings
        )

        penalidade = min(
            faltantes * 10,
            30,
        )

        score -= penalidade

        penalidades.append(
            f"Documentos sem embeddings: -{penalidade}"
        )

    total_embeddings = (
        embeddings_ativos
        + embeddings_inativos
    )

    if total_embeddings <= 0:
        score -= 30

        penalidades.append(
            "Nenhum embedding disponível: -30"
        )

    elif embeddings_inativos > 0:
        percentual_inativos = (
            embeddings_inativos
            / total_embeddings
        ) * 100

        penalidade = min(
            percentual_inativos * 0.3,
            20,
        )

        score -= penalidade

        penalidades.append(
            f"Embeddings inativos: -{penalidade:.1f}"
        )

    score = limitar_score(score)

    return {
        "score": score,
        "penalidades": penalidades,
        **classificar_score(score),
    }


def calcular_score_memoria(
    *,
    tabela_disponivel: bool,
    total_usuarios_com_memoria: int,
    erros_memoria: int = 0,
) -> dict[str, Any]:
    """
    Calcula a saúde da memória persistente.
    """
    score = 100.0
    penalidades = []

    if not tabela_disponivel:
        score = 0.0
        penalidades.append(
            "Tabela de memória indisponível: -100"
        )

    else:
        if total_usuarios_com_memoria <= 0:
            score -= 15

            penalidades.append(
                "Nenhuma memória registrada: -15"
            )

        if erros_memoria > 0:
            penalidade = min(
                erros_memoria * 5,
                30,
            )

            score -= penalidade

            penalidades.append(
                f"Erros de memória: -{penalidade}"
            )

    score = limitar_score(score)

    return {
        "score": score,
        "penalidades": penalidades,
        **classificar_score(score),
    }


def calcular_score_timeline(
    *,
    traces_analisados: int,
    traces_com_falha: int,
    percentual_cold_start: float,
) -> dict[str, Any]:
    """
    Calcula a saúde dos traces da Timeline.
    """
    score = 100.0
    penalidades = []

    if traces_analisados <= 0:
        score -= 20

        penalidades.append(
            "Nenhum trace analisado: -20"
        )

    if traces_com_falha > 0:
        percentual_falhas = (
            traces_com_falha
            / max(traces_analisados, 1)
        ) * 100

        penalidade = min(
            percentual_falhas * 0.5,
            35,
        )

        score -= penalidade

        penalidades.append(
            f"Traces com falha: -{penalidade:.1f}"
        )

    if percentual_cold_start > 10:
        penalidade = min(
            (percentual_cold_start - 10) * 0.4,
            25,
        )

        score -= penalidade

        penalidades.append(
            f"Cold starts: -{penalidade:.1f}"
        )

    score = limitar_score(score)

    return {
        "score": score,
        "penalidades": penalidades,
        **classificar_score(score),
    }


def calcular_score_performance(
    *,
    p95_tools_ms: float,
    p95_trace_ms: float,
) -> dict[str, Any]:
    """
    Calcula a saúde geral de performance.
    """
    score = 100.0
    penalidades = []

    if p95_tools_ms > 1000:
        penalidade = min(
            (
                p95_tools_ms
                - 1000
            )
            / 200,
            25,
        )

        score -= penalidade

        penalidades.append(
            f"P95 Tools elevado: -{penalidade:.1f}"
        )

    if p95_trace_ms > 10000:
        penalidade = min(
            (
                p95_trace_ms
                - 10000
            )
            / 1000,
            35,
        )

        score -= penalidade

        penalidades.append(
            f"P95 dos traces elevado: -{penalidade:.1f}"
        )

    score = limitar_score(score)

    return {
        "score": score,
        "penalidades": penalidades,
        **classificar_score(score),
    }


def calcular_health_score_global(
    componentes: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Consolida os scores dos componentes.

    Componentes ausentes recebem score zero.
    """
    contribuicoes = {}
    score_global = 0.0

    for nome, peso in PESOS_COMPONENTES.items():
        componente = componentes.get(
            nome,
            {},
        )

        score = limitar_score(
            componente.get(
                "score",
                0,
            )
        )

        contribuicao = score * peso

        contribuicoes[nome] = {
            "score": score,
            "peso": peso,
            "contribuicao": round(
                contribuicao,
                2,
            ),
            "classificacao": componente.get(
                "classificacao",
                classificar_score(score)[
                    "classificacao"
                ],
            ),
            "status": componente.get(
                "status",
                classificar_score(score)[
                    "status"
                ],
            ),
            "icone": componente.get(
                "icone",
                classificar_score(score)[
                    "icone"
                ],
            ),
            "penalidades": componente.get(
                "penalidades",
                [],
            ),
        }

        score_global += contribuicao

    score_global = limitar_score(
        score_global
    )

    classificacao = classificar_score(
        score_global
    )

    componente_mais_fraco = min(
        contribuicoes,
        key=lambda item: (
            contribuicoes[item]["score"]
        ),
    )

    componente_mais_forte = max(
        contribuicoes,
        key=lambda item: (
            contribuicoes[item]["score"]
        ),
    )

    recomendacoes = []

    for nome, item in contribuicoes.items():
        if item["score"] < 85:
            recomendacoes.append(
                f"Priorizar melhorias no componente "
                f"{nome}, atualmente com score "
                f"{item['score']}/100."
            )

    if not recomendacoes:
        recomendacoes.append(
            "Todos os componentes estão em nível saudável. "
            "Continue monitorando P95, falhas e cold starts."
        )

    return {
        "score_global": score_global,
        **classificacao,
        "componentes": contribuicoes,
        "componente_mais_fraco": (
            componente_mais_fraco
        ),
        "componente_mais_forte": (
            componente_mais_forte
        ),
        "recomendacoes": recomendacoes,
    }


__all__ = [
    "PESOS_COMPONENTES",
    "limitar_score",
    "classificar_score",
    "calcular_score_tools",
    "calcular_score_infraestrutura",
    "calcular_score_rag",
    "calcular_score_memoria",
    "calcular_score_timeline",
    "calcular_score_performance",
    "calcular_health_score_global",
]
