"""
Narrativa inteligente e insights operacionais da INNA.

Este módulo transforma métricas de observabilidade em:
- resumo executivo;
- destaques positivos;
- alertas;
- gargalos;
- recomendações técnicas.

A análise principal é determinística e não depende de LLM,
garantindo previsibilidade, testabilidade e segurança.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .analytics import (
    calcular_execucoes_sem_tool,
    calcular_ranking_tools,
    comparar_periodos,
    preparar_eventos_analytics,
)


def _formatar_percentual(
    valor: float,
) -> str:
    return f"{float(valor):.2f}%"


def _formatar_duracao(
    valor_ms: float,
) -> str:
    valor = float(valor_ms or 0)

    if valor >= 1000:
        return f"{valor / 1000:.2f} s"

    return f"{valor:.3f} ms"


def classificar_saude_operacional(
    *,
    taxa_sucesso: float,
    confianca_media: float,
    percentual_sem_tool: float,
    p95_ms: float,
) -> dict[str, Any]:
    """
    Classifica a saúde operacional da camada de Tools.

    Score máximo: 100 pontos.
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
            f"Taxa de sucesso abaixo de 99%: "
            f"-{penalidade:.1f} pontos."
        )

    if confianca_media < 85:
        penalidade = min(
            (85 - confianca_media) * 1.2,
            20,
        )
        score -= penalidade
        penalidades.append(
            f"Confiança média abaixo de 85%: "
            f"-{penalidade:.1f} pontos."
        )

    if percentual_sem_tool > 15:
        penalidade = min(
            (percentual_sem_tool - 15) * 0.8,
            20,
        )
        score -= penalidade
        penalidades.append(
            f"Muitas execuções sem Tool: "
            f"-{penalidade:.1f} pontos."
        )

    if p95_ms > 5000:
        penalidade = min(
            ((p95_ms - 5000) / 1000) * 2,
            25,
        )
        score -= penalidade
        penalidades.append(
            f"P95 elevado: -{penalidade:.1f} pontos."
        )

    score = round(
        max(0.0, min(100.0, score)),
        1,
    )

    if score >= 95:
        classificacao = "Excelente"
        status = "saudavel"

    elif score >= 85:
        classificacao = "Boa"
        status = "atencao_leve"

    elif score >= 70:
        classificacao = "Atenção"
        status = "atencao"

    else:
        classificacao = "Crítica"
        status = "critico"

    return {
        "score": score,
        "classificacao": classificacao,
        "status": status,
        "penalidades": penalidades,
    }


def gerar_insights_operacionais(
    df: pd.DataFrame | None,
    *,
    horas_comparacao: int = 24,
) -> dict[str, Any]:
    """
    Gera narrativa e insights a partir dos eventos das Tools.
    """
    base = preparar_eventos_analytics(
        df
    )

    if base.empty:
        return {
            "ok": True,
            "tem_dados": False,
            "titulo": "Ainda não existem dados suficientes.",
            "resumo_executivo": (
                "Execute algumas Tools financeiras para "
                "alimentar o painel de observabilidade."
            ),
            "destaques": [],
            "alertas": [],
            "recomendacoes": [],
            "metricas": {},
            "saude": {
                "score": 0.0,
                "classificacao": "Sem dados",
                "status": "sem_dados",
                "penalidades": [],
            },
        }

    total_eventos = len(base)

    total_sucessos = int(
        base["sucesso"].sum()
        if "sucesso" in base.columns
        else 0
    )

    total_falhas = max(
        total_eventos - total_sucessos,
        0,
    )

    taxa_sucesso = round(
        (
            total_sucessos
            / total_eventos
        )
        * 100,
        2,
    )

    confianca_media = (
        round(
            float(
                base["confianca"]
                .dropna()
                .mean()
            )
            * 100,
            2,
        )
        if (
            "confianca" in base.columns
            and base["confianca"].notna().any()
        )
        else 0.0
    )

    ranking = calcular_ranking_tools(
        base
    )

    sem_tool = calcular_execucoes_sem_tool(
        base
    )

    comparacao = comparar_periodos(
        base,
        horas=int(horas_comparacao),
    )

    tool_mais_usada = None
    tool_mais_lenta = None
    p95_global = 0.0

    if not ranking.empty:
        item_mais_usado = ranking.iloc[0]

        tool_mais_usada = {
            "nome": item_mais_usado["ferramenta"],
            "execucoes": int(
                item_mais_usado["execucoes"]
            ),
            "taxa_sucesso": float(
                item_mais_usado[
                    "taxa_sucesso_percentual"
                ]
            ),
        }

        indice_lenta = ranking[
            "p95_ms"
        ].idxmax()

        item_lento = ranking.loc[
            indice_lenta
        ]

        tool_mais_lenta = {
            "nome": item_lento["ferramenta"],
            "p95_ms": float(
                item_lento["p95_ms"]
            ),
            "media_ms": float(
                item_lento[
                    "duracao_media_ms"
                ]
            ),
        }

        p95_global = float(
            ranking["p95_ms"].max()
        )

    saude = classificar_saude_operacional(
        taxa_sucesso=taxa_sucesso,
        confianca_media=confianca_media,
        percentual_sem_tool=float(
            sem_tool["percentual"]
        ),
        p95_ms=p95_global,
    )

    destaques = []
    alertas = []
    recomendacoes = []

    if taxa_sucesso >= 99:
        destaques.append(
            f"A taxa de sucesso está excelente: "
            f"{_formatar_percentual(taxa_sucesso)}."
        )

    elif taxa_sucesso >= 95:
        destaques.append(
            f"A taxa de sucesso está saudável: "
            f"{_formatar_percentual(taxa_sucesso)}."
        )

    else:
        alertas.append(
            f"A taxa de sucesso está em "
            f"{_formatar_percentual(taxa_sucesso)}, "
            "abaixo do nível recomendado de 95%."
        )

        recomendacoes.append(
            "Investigar as Tools com falhas e analisar "
            "mensagens de erro, dados ausentes e intenção."
        )

    if tool_mais_usada:
        destaques.append(
            f"A Tool mais utilizada foi "
            f"“{tool_mais_usada['nome']}”, com "
            f"{tool_mais_usada['execucoes']} execução(ões)."
        )

    if confianca_media >= 90:
        destaques.append(
            f"O Router apresentou confiança média alta: "
            f"{_formatar_percentual(confianca_media)}."
        )

    elif confianca_media >= 85:
        alertas.append(
            f"A confiança média está no limite recomendado "
            f"de {_formatar_percentual(confianca_media)}. "
            "Vale acompanhar novas execuções para confirmar "
            "a estabilidade do Router."
        )

        recomendacoes.append(
            "Acompanhar a confiança do Router conforme novas "
            "perguntas e intenções forem registradas."
        )

    elif confianca_media >= 75:
        alertas.append(
            f"A confiança média do Router está em uma faixa "
            f"de atenção: {_formatar_percentual(confianca_media)}."
        )

        recomendacoes.append(
            "Revisar as intenções com menor confiança e "
            "adicionar exemplos de classificação."
        )

    else:
        alertas.append(
            f"A confiança média do Router está baixa: "
            f"{_formatar_percentual(confianca_media)}."
        )

        recomendacoes.append(
            "Revisar termos, regras de classificação e "
            "exemplos de intenção do Router."
        )

    if sem_tool["percentual"] > 20:
        alertas.append(
            f"{sem_tool['percentual']:.2f}% das execuções "
            "não identificaram uma Tool."
        )

        recomendacoes.append(
            "Analisar perguntas sem Tool para descobrir "
            "novas intenções ou lacunas no roteamento."
        )

    elif sem_tool["total"] == 0:
        destaques.append(
            "Todas as execuções analisadas identificaram "
            "uma Tool quando necessário."
        )

    if tool_mais_lenta:
        if tool_mais_lenta["p95_ms"] >= 5000:
            alertas.append(
                f"A Tool “{tool_mais_lenta['nome']}” possui "
                f"P95 elevado: "
                f"{_formatar_duracao(tool_mais_lenta['p95_ms'])}."
            )

            recomendacoes.append(
                f"Investigar conexões externas, consultas "
                f"ao banco e processamento da Tool "
                f"“{tool_mais_lenta['nome']}”."
            )

        else:
            destaques.append(
                f"O maior P95 entre as Tools foi "
                f"{_formatar_duracao(tool_mais_lenta['p95_ms'])}, "
                "dentro de uma faixa aceitável."
            )

    variacao_execucoes = float(
        comparacao.get(
            "variacao_execucoes_percentual",
            0,
        )
    )

    variacao_falhas = float(
        comparacao.get(
            "variacao_falhas_percentual",
            0,
        )
    )

    variacao_duracao = float(
        comparacao.get(
            "variacao_duracao_percentual",
            0,
        )
    )

    if variacao_execucoes > 25:
        destaques.append(
            f"O volume de execuções aumentou "
            f"{variacao_execucoes:.2f}% em relação "
            "ao período anterior."
        )

    elif variacao_execucoes < -25:
        alertas.append(
            f"O volume de execuções caiu "
            f"{abs(variacao_execucoes):.2f}% em relação "
            "ao período anterior."
        )

    if variacao_falhas > 20:
        alertas.append(
            f"As falhas aumentaram "
            f"{variacao_falhas:.2f}% no período atual."
        )

        recomendacoes.append(
            "Priorizar a análise dos erros mais recentes "
            "e verificar se houve mudança no Router ou Tools."
        )

    if variacao_duracao > 30:
        alertas.append(
            f"A duração média aumentou "
            f"{variacao_duracao:.2f}%."
        )

        recomendacoes.append(
            "Comparar traces recentes e identificar "
            "qual etapa apresentou degradação."
        )

    if not alertas:
        destaques.append(
            "Nenhuma anomalia operacional crítica foi "
            "detectada nos eventos analisados."
        )

    if not recomendacoes:
        recomendacoes.append(
            "Continuar monitorando volume, confiança, "
            "P95 e taxa de sucesso."
        )

    resumo_executivo = (
        f"Foram analisadas {total_eventos} execução(ões), "
        f"com taxa de sucesso de "
        f"{_formatar_percentual(taxa_sucesso)} e confiança "
        f"média do Router de "
        f"{_formatar_percentual(confianca_media)}. "
    )

    if tool_mais_usada:
        resumo_executivo += (
            f"A Tool predominante foi "
            f"“{tool_mais_usada['nome']}”. "
        )

    resumo_executivo += (
        f"A saúde operacional foi classificada como "
        f"{saude['classificacao']}, com score "
        f"{saude['score']}/100."
    )

    return {
        "ok": True,
        "tem_dados": True,
        "titulo": "Resumo operacional automático",
        "resumo_executivo": resumo_executivo,
        "destaques": destaques,
        "alertas": alertas,
        "recomendacoes": recomendacoes,
        "metricas": {
            "total_eventos": total_eventos,
            "total_sucessos": total_sucessos,
            "total_falhas": total_falhas,
            "taxa_sucesso_percentual": taxa_sucesso,
            "confianca_media_percentual": confianca_media,
            "execucoes_sem_tool": sem_tool,
            "tool_mais_usada": tool_mais_usada,
            "tool_mais_lenta": tool_mais_lenta,
            "comparacao_periodos": comparacao,
        },
        "saude": saude,
    }


def gerar_texto_narrativa(
    insights: dict[str, Any],
) -> str:
    """
    Converte os insights estruturados em Markdown.
    """
    if not insights.get("tem_dados"):
        return insights.get(
            "resumo_executivo",
            "Sem dados disponíveis.",
        )

    linhas = [
        f"## {insights.get('titulo')}",
        "",
        insights.get(
            "resumo_executivo",
            "",
        ),
        "",
        "### Destaques",
    ]

    for item in insights.get(
        "destaques",
        [],
    ):
        linhas.append(
            f"- {item}"
        )

    alertas = insights.get(
        "alertas",
        [],
    )

    if alertas:
        linhas.extend([
            "",
            "### Alertas",
        ])

        for item in alertas:
            linhas.append(
                f"- {item}"
            )

    linhas.extend([
        "",
        "### Recomendações",
    ])

    for item in insights.get(
        "recomendacoes",
        [],
    ):
        linhas.append(
            f"- {item}"
        )

    return "\n".join(linhas).strip()


__all__ = [
    "classificar_saude_operacional",
    "gerar_insights_operacionais",
    "gerar_texto_narrativa",
]
