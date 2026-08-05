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

# OPERATIONAL_NARRATIVE_I18N_CATALOG
#
# Catálogo determinístico usado pela narrativa operacional.
# Os nomes técnicos das Tools não são traduzidos.

NARRATIVE_LANGUAGE_ALIASES = {
    "pt": "pt",
    "pt_br": "pt",
    "en": "en_us",
    "en_us": "en_us",
    "en_gb": "en_gb",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "ch": "ch",
    "it": "it",
    "ro": "ro",
    "ua": "ua",
    "uk": "ua",
    "ru": "ru",
    "sa": "sa",
    "ar": "sa",
}


NARRATIVE_TEXTS = {
    "pt": {
        "health_excellent": "Excelente",
        "health_good": "Boa",
        "health_attention": "Atenção",
        "health_critical": "Crítica",
        "no_data_title": ("Ainda não existem dados suficientes."),
        "no_data_summary": (
            "Execute algumas Tools financeiras para "
            "alimentar o painel de observabilidade."
        ),
        "no_data_classification": "Sem dados",
        "automatic_summary_title": ("Resumo operacional automático"),
        "markdown_no_data": ("Sem dados disponíveis."),
        "markdown_highlights": "### Destaques",
        "markdown_alerts": "### Alertas",
        "markdown_recommendations": ("### Recomendações"),
    },
    "en_us": {
        "health_excellent": "Excellent",
        "health_good": "Good",
        "health_attention": "Attention",
        "health_critical": "Critical",
        "no_data_title": ("There is not enough data yet."),
        "no_data_summary": (
            "Run some financial Tools to populate the observability dashboard."
        ),
        "no_data_classification": "No data",
        "automatic_summary_title": ("Automatic operational summary"),
        "markdown_no_data": ("No data is available."),
        "markdown_highlights": "### Highlights",
        "markdown_alerts": "### Alerts",
        "markdown_recommendations": ("### Recommendations"),
    },
    "en_gb": {
        "health_excellent": "Excellent",
        "health_good": "Good",
        "health_attention": "Attention",
        "health_critical": "Critical",
        "no_data_title": ("There is not enough data yet."),
        "no_data_summary": (
            "Run some financial Tools to populate the observability dashboard."
        ),
        "no_data_classification": "No data",
        "automatic_summary_title": ("Automatic operational summary"),
        "markdown_no_data": ("No data is available."),
        "markdown_highlights": "### Highlights",
        "markdown_alerts": "### Alerts",
        "markdown_recommendations": ("### Recommendations"),
    },
    "ru": {
        "health_excellent": "Отличное",
        "health_good": "Хорошее",
        "health_attention": "Требует внимания",
        "health_critical": "Критическое",
        "no_data_title": ("Данных пока недостаточно."),
        "no_data_summary": (
            "Выполните несколько финансовых Tools, "
            "чтобы заполнить панель наблюдаемости."
        ),
        "no_data_classification": "Нет данных",
        "automatic_summary_title": ("Автоматическая операционная сводка"),
        "markdown_no_data": ("Данные недоступны."),
        "markdown_highlights": ("### Сильные стороны"),
        "markdown_alerts": ("### Предупреждения"),
        "markdown_recommendations": ("### Рекомендации"),
    },
}


def normalizar_idioma_narrativa(
    idioma: str | None,
) -> str:
    """
    Normaliza o idioma solicitado pela interface.

    Idiomas ainda sem catálogo próprio usam inglês
    até receberem o pacote nativo completo.
    """
    codigo = (
        str(idioma or "pt")
        .strip()
        .lower()
        .replace(
            "-",
            "_",
        )
    )

    normalizado = NARRATIVE_LANGUAGE_ALIASES.get(
        codigo,
        codigo,
    )

    if normalizado in NARRATIVE_TEXTS:
        return normalizado

    return "en_us"


def narrative_t(
    key: str,
    *,
    idioma: str | None = "pt",
    default: str | None = None,
) -> str:
    """
    Obtém um texto localizado da narrativa operacional.
    """
    language = normalizar_idioma_narrativa(idioma)

    texts = NARRATIVE_TEXTS.get(
        language,
        NARRATIVE_TEXTS["en_us"],
    )

    value = texts.get(key)

    if value is not None:
        return value

    portuguese_value = NARRATIVE_TEXTS["pt"].get(key)

    if portuguese_value is not None:
        return portuguese_value

    if default is not None:
        return default

    return key


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
    idioma: str = "pt",
) -> dict[str, Any]:
    """
    Classifica a saúde operacional da camada de Tools.

    Score máximo: 100 pontos.
    """
    idioma = normalizar_idioma_narrativa(idioma)

    score = 100.0
    penalidades = []

    if taxa_sucesso < 99:
        penalidade = min(
            (99 - taxa_sucesso) * 2,
            35,
        )
        score -= penalidade
        penalidades.append(f"Taxa de sucesso abaixo de 99%: -{penalidade:.1f} pontos.")

    if confianca_media < 85:
        penalidade = min(
            (85 - confianca_media) * 1.2,
            20,
        )
        score -= penalidade
        penalidades.append(f"Confiança média abaixo de 85%: -{penalidade:.1f} pontos.")

    if percentual_sem_tool > 15:
        penalidade = min(
            (percentual_sem_tool - 15) * 0.8,
            20,
        )
        score -= penalidade
        penalidades.append(f"Muitas execuções sem Tool: -{penalidade:.1f} pontos.")

    if p95_ms > 5000:
        penalidade = min(
            ((p95_ms - 5000) / 1000) * 2,
            25,
        )
        score -= penalidade
        penalidades.append(f"P95 elevado: -{penalidade:.1f} pontos.")

    score = round(
        max(0.0, min(100.0, score)),
        1,
    )

    if score >= 95:
        classificacao = narrative_t(
            "health_excellent",
            idioma=idioma,
        )
        status = "saudavel"

    elif score >= 85:
        classificacao = narrative_t(
            "health_good",
            idioma=idioma,
        )
        status = "atencao_leve"

    elif score >= 70:
        classificacao = narrative_t(
            "health_attention",
            idioma=idioma,
        )
        status = "atencao"

    else:
        classificacao = narrative_t(
            "health_critical",
            idioma=idioma,
        )
        status = "critico"

    return {
        "score": score,
        "classificacao": classificacao,
        "status": status,
        "penalidades": penalidades,
    }


# OPERATIONAL_NARRATIVE_RUSSIAN_DYNAMIC_MESSAGES


def _localizar_insights_dinamicos(
    insights: dict[str, Any],
    *,
    idioma: str,
) -> dict[str, Any]:
    """
    Localiza as mensagens dinâmicas geradas pela análise.

    Os identificadores e nomes técnicos das Tools são
    preservados exatamente como foram registrados.
    """
    language = normalizar_idioma_narrativa(idioma)

    if language != "ru" or not insights.get("tem_dados"):
        return insights

    resultado = dict(insights)

    metricas = dict(
        resultado.get(
            "metricas",
            {},
        )
    )

    saude = dict(
        resultado.get(
            "saude",
            {},
        )
    )

    total_eventos = int(
        metricas.get(
            "total_eventos",
            0,
        )
    )

    taxa_sucesso = float(
        metricas.get(
            "taxa_sucesso_percentual",
            0,
        )
    )

    confianca_media = float(
        metricas.get(
            "confianca_media_percentual",
            0,
        )
    )

    sem_tool = dict(
        metricas.get(
            "execucoes_sem_tool",
            {},
        )
        or {}
    )

    tool_mais_usada = metricas.get("tool_mais_usada")

    tool_mais_lenta = metricas.get("tool_mais_lenta")

    comparacao = dict(
        metricas.get(
            "comparacao_periodos",
            {},
        )
        or {}
    )

    destaques: list[str] = []
    alertas: list[str] = []
    recomendacoes: list[str] = []

    if taxa_sucesso >= 99:
        destaques.append(
            "Уровень успешных выполнений отличный: "
            f"{_formatar_percentual(taxa_sucesso)}."
        )

    elif taxa_sucesso >= 95:
        destaques.append(
            "Уровень успешных выполнений находится "
            "в здоровом диапазоне: "
            f"{_formatar_percentual(taxa_sucesso)}."
        )

    else:
        alertas.append(
            "Уровень успешных выполнений составляет "
            f"{_formatar_percentual(taxa_sucesso)}, "
            "что ниже рекомендуемого уровня 95%."
        )

        recomendacoes.append(
            "Проверить Tools с ошибками, сообщения об "
            "ошибках, отсутствующие данные и распознанные "
            "намерения."
        )

    if tool_mais_usada:
        destaques.append(
            "Наиболее используемой Tool была "
            f"«{tool_mais_usada['nome']}»: "
            f"{int(tool_mais_usada['execucoes'])} выполнений."
        )

    if confianca_media >= 90:
        destaques.append(
            "Router показал высокий средний уровень "
            "уверенности: "
            f"{_formatar_percentual(confianca_media)}."
        )

    elif confianca_media >= 85:
        alertas.append(
            "Средняя уверенность находится на "
            "рекомендуемой границе: "
            f"{_formatar_percentual(confianca_media)}. "
            "Следует наблюдать за новыми выполнениями, "
            "чтобы подтвердить стабильность Router."
        )

        recomendacoes.append(
            "Отслеживать уверенность Router по мере "
            "регистрации новых вопросов и намерений."
        )

    elif confianca_media >= 75:
        alertas.append(
            "Средняя уверенность Router находится "
            "в диапазоне, требующем внимания: "
            f"{_formatar_percentual(confianca_media)}."
        )

        recomendacoes.append(
            "Проверить намерения с низкой уверенностью "
            "и добавить примеры классификации."
        )

    else:
        alertas.append(
            "Средняя уверенность Router низкая: "
            f"{_formatar_percentual(confianca_media)}."
        )

        recomendacoes.append(
            "Проверить термины, правила классификации и примеры намерений Router."
        )

    percentual_sem_tool = float(
        sem_tool.get(
            "percentual",
            0,
        )
    )

    total_sem_tool = int(
        sem_tool.get(
            "total",
            0,
        )
    )

    if percentual_sem_tool > 20:
        alertas.append(f"{percentual_sem_tool:.2f}% выполнений не определили Tool.")

        recomendacoes.append(
            "Проанализировать вопросы без Tool, чтобы "
            "выявить новые намерения или пробелы "
            "в маршрутизации."
        )

    elif total_sem_tool == 0:
        destaques.append(
            "Все проанализированные выполнения определили Tool, когда это требовалось."
        )

    if tool_mais_lenta:
        p95_ms = float(
            tool_mais_lenta.get(
                "p95_ms",
                0,
            )
        )

        if p95_ms >= 5000:
            alertas.append(
                f"Tool «{tool_mais_lenta['nome']}» имеет "
                "повышенное значение P95: "
                f"{_formatar_duracao(p95_ms)}."
            )

            recomendacoes.append(
                "Проверить внешние соединения, запросы "
                "к базе данных и обработку Tool "
                f"«{tool_mais_lenta['nome']}»."
            )

        else:
            destaques.append(
                "Наибольшее значение P95 среди Tools "
                f"составило {_formatar_duracao(p95_ms)}, "
                "что находится в допустимом диапазоне."
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
            "Объём выполнений увеличился на "
            f"{variacao_execucoes:.2f}% по сравнению "
            "с предыдущим периодом."
        )

    elif variacao_execucoes < -25:
        alertas.append(
            "Объём выполнений снизился на "
            f"{abs(variacao_execucoes):.2f}% по сравнению "
            "с предыдущим периодом."
        )

    if variacao_falhas > 20:
        alertas.append(
            "Количество ошибок увеличилось на "
            f"{variacao_falhas:.2f}% в текущем периоде."
        )

        recomendacoes.append(
            "Приоритетно проанализировать последние "
            "ошибки и проверить изменения в Router "
            "или Tools."
        )

    if variacao_duracao > 30:
        alertas.append(f"Средняя длительность увеличилась на {variacao_duracao:.2f}%.")

        recomendacoes.append(
            "Сравнить последние traces и определить "
            "этап, на котором возникло ухудшение."
        )

    if not alertas:
        destaques.append(
            "В проанализированных событиях не обнаружено "
            "критических операционных аномалий."
        )

    if not recomendacoes:
        recomendacoes.append(
            "Продолжать отслеживать объём, уверенность, "
            "P95 и уровень успешных выполнений."
        )

    resumo_executivo = (
        f"Проанализировано выполнений: {total_eventos}. "
        "Уровень успешных выполнений: "
        f"{_formatar_percentual(taxa_sucesso)}; "
        "средняя уверенность Router: "
        f"{_formatar_percentual(confianca_media)}. "
    )

    if tool_mais_usada:
        resumo_executivo += f"Преобладающей Tool была «{tool_mais_usada['nome']}». "

    resumo_executivo += (
        "Операционное состояние классифицировано как "
        f"«{saude.get('classificacao', '')}», "
        f"оценка: {saude.get('score', 0)}/100."
    )

    resultado["resumo_executivo"] = resumo_executivo

    resultado["destaques"] = destaques
    resultado["alertas"] = alertas
    resultado["recomendacoes"] = recomendacoes

    return resultado


def gerar_insights_operacionais(
    df: pd.DataFrame | None,
    *,
    horas_comparacao: int = 24,
    idioma: str = "pt",
) -> dict[str, Any]:
    """
    Gera narrativa e insights a partir dos eventos das Tools.
    """
    idioma = str(idioma or "pt").strip().lower()

    base = preparar_eventos_analytics(df)

    if base.empty:
        resultado = {
            "ok": True,
            "tem_dados": False,
            "idioma": idioma,
            "titulo": narrative_t(
                "no_data_title",
                idioma=idioma,
            ),
            "resumo_executivo": narrative_t(
                "no_data_summary",
                idioma=idioma,
            ),
            "destaques": [],
            "alertas": [],
            "recomendacoes": [],
            "metricas": {},
            "saude": {
                "score": 0.0,
                "classificacao": narrative_t(
                    "no_data_classification",
                    idioma=idioma,
                ),
                "status": "sem_dados",
                "penalidades": [],
            },
        }

        return _localizar_insights_dinamicos(
            resultado,
            idioma=idioma,
        )

    total_eventos = len(base)

    total_sucessos = int(base["sucesso"].sum() if "sucesso" in base.columns else 0)

    total_falhas = max(
        total_eventos - total_sucessos,
        0,
    )

    taxa_sucesso = round(
        (total_sucessos / total_eventos) * 100,
        2,
    )

    confianca_media = (
        round(
            float(base["confianca"].dropna().mean()) * 100,
            2,
        )
        if ("confianca" in base.columns and base["confianca"].notna().any())
        else 0.0
    )

    ranking = calcular_ranking_tools(base)

    sem_tool = calcular_execucoes_sem_tool(base)

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
            "execucoes": int(item_mais_usado["execucoes"]),
            "taxa_sucesso": float(item_mais_usado["taxa_sucesso_percentual"]),
        }

        indice_lenta = ranking["p95_ms"].idxmax()

        item_lento = ranking.loc[indice_lenta]

        tool_mais_lenta = {
            "nome": item_lento["ferramenta"],
            "p95_ms": float(item_lento["p95_ms"]),
            "media_ms": float(item_lento["duracao_media_ms"]),
        }

        p95_global = float(ranking["p95_ms"].max())

    saude = classificar_saude_operacional(
        taxa_sucesso=taxa_sucesso,
        confianca_media=confianca_media,
        percentual_sem_tool=float(sem_tool["percentual"]),
        p95_ms=p95_global,
        idioma=idioma,
    )

    destaques = []
    alertas = []
    recomendacoes = []

    if taxa_sucesso >= 99:
        destaques.append(
            f"A taxa de sucesso está excelente: {_formatar_percentual(taxa_sucesso)}."
        )

    elif taxa_sucesso >= 95:
        destaques.append(
            f"A taxa de sucesso está saudável: {_formatar_percentual(taxa_sucesso)}."
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
            "Revisar termos, regras de classificação e exemplos de intenção do Router."
        )

    if sem_tool["percentual"] > 20:
        alertas.append(
            f"{sem_tool['percentual']:.2f}% das execuções não identificaram uma Tool."
        )

        recomendacoes.append(
            "Analisar perguntas sem Tool para descobrir "
            "novas intenções ou lacunas no roteamento."
        )

    elif sem_tool["total"] == 0:
        destaques.append(
            "Todas as execuções analisadas identificaram uma Tool quando necessário."
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
        alertas.append(f"As falhas aumentaram {variacao_falhas:.2f}% no período atual.")

        recomendacoes.append(
            "Priorizar a análise dos erros mais recentes "
            "e verificar se houve mudança no Router ou Tools."
        )

    if variacao_duracao > 30:
        alertas.append(f"A duração média aumentou {variacao_duracao:.2f}%.")

        recomendacoes.append(
            "Comparar traces recentes e identificar qual etapa apresentou degradação."
        )

    if not alertas:
        destaques.append(
            "Nenhuma anomalia operacional crítica foi detectada nos eventos analisados."
        )

    if not recomendacoes:
        recomendacoes.append(
            "Continuar monitorando volume, confiança, P95 e taxa de sucesso."
        )

    resumo_executivo = (
        f"Foram analisadas {total_eventos} execução(ões), "
        f"com taxa de sucesso de "
        f"{_formatar_percentual(taxa_sucesso)} e confiança "
        f"média do Router de "
        f"{_formatar_percentual(confianca_media)}. "
    )

    if tool_mais_usada:
        resumo_executivo += f"A Tool predominante foi “{tool_mais_usada['nome']}”. "

    resumo_executivo += (
        f"A saúde operacional foi classificada como "
        f"{saude['classificacao']}, com score "
        f"{saude['score']}/100."
    )

    resultado = {
        "ok": True,
        "tem_dados": True,
        "idioma": idioma,
        "titulo": narrative_t(
            "automatic_summary_title",
            idioma=idioma,
        ),
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

    return _localizar_insights_dinamicos(
        resultado,
        idioma=idioma,
    )


def gerar_texto_narrativa(
    insights: dict[str, Any],
    *,
    idioma: str = "pt",
) -> str:
    """
    Converte os insights estruturados em Markdown.
    """
    if not insights.get("tem_dados"):
        return insights.get(
            "resumo_executivo",
            narrative_t(
                "markdown_no_data",
                idioma=idioma,
            ),
        )

    linhas = [
        f"## {insights.get('titulo')}",
        "",
        insights.get(
            "resumo_executivo",
            "",
        ),
        "",
        narrative_t(
            "markdown_highlights",
            idioma=idioma,
        ),
    ]

    for item in insights.get(
        "destaques",
        [],
    ):
        linhas.append(f"- {item}")

    alertas = insights.get(
        "alertas",
        [],
    )

    if alertas:
        linhas.extend(
            [
                "",
                narrative_t(
                    "markdown_alerts",
                    idioma=idioma,
                ),
            ]
        )

        for item in alertas:
            linhas.append(f"- {item}")

    linhas.extend(
        [
            "",
            narrative_t(
                "markdown_recommendations",
                idioma=idioma,
            ),
        ]
    )

    for item in insights.get(
        "recomendacoes",
        [],
    ):
        linhas.append(f"- {item}")

    return "\n".join(linhas).strip()


__all__ = [
    "classificar_saude_operacional",
    "gerar_insights_operacionais",
    "gerar_texto_narrativa",
]
