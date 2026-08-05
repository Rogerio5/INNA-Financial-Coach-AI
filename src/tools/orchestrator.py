"""
Orquestrador profissional das Tools financeiras da INNA.

Responsabilidades:
- preparar dados confiáveis da memória persistente;
- executar o Tool Router;
- preservar prioridade dos dados mais recentes;
- transformar resultados determinísticos em contexto para o prompt;
- impedir que o modelo altere cálculos feitos pelas Tools;
- informar dados ausentes sem inventar valores.
"""

from __future__ import annotations

import json
from time import perf_counter
from typing import Any

from .registry import TOOL_LABELS
from .router import rotear_tool


CAMPOS_MEMORIA_PERMITIDOS = {
    "usuario_id",
    "nome",
    "idioma",
    "moeda",
    "renda_mensal",
    "gastos_mensais",
    "gastos_incluem_dividas",
    "valor_reserva",
    "dividas_mensais",
    "parcelas_mensais",
    "possui_dividas",
    "uso_cartao_credito",
    "perfil_financeiro",
    "objetivo_principal",
    "ultima_meta",
    "meta_total",
    "meta_financeira",
    "aporte_mensal",
    "valor_inicial",
    "saldo_inicial",
    "valor_total",
    "valor_divida",
    "parcela_mensal",
    "taxa_juros_mensal",
    "esta_atrasada",
    "quantidade_parcelas",
    "parcelas_restantes",
    "tipo_divida",
}


ALIASES_MEMORIA_JSON = {
    "renda": "renda_mensal",
    "gastos": "gastos_mensais",
    "pode_guardar": "valor_reserva",
    "capacidade_mensal": "valor_reserva",
    "meta": "meta_total",
    "aporte": "aporte_mensal",
    "divida_total": "valor_divida",
}


MOTIVOS_TOOLS = {
    "analisar_orcamento": (
        "A pergunta envolve renda, gastos, despesas ou saldo mensal."
    ),
    "calcular_capacidade_semanal": (
        "A pergunta solicita uma referência semanal a partir "
        "da capacidade mensal informada."
    ),
    "simular_formacao_reserva": (
        "A pergunta envolve uma meta de reserva e o tempo estimado para alcançá-la."
    ),
    "analisar_divida_educativamente": (
        "A mensagem contém informações sobre dívida, atraso, parcelas ou juros."
    ),
    "simular_parcelamento_sem_juros": (
        "A pergunta envolve divisão de um valor em parcelas sem juros."
    ),
    "simular_meta_por_aporte": (
        "A pergunta envolve uma meta financeira e aportes mensais."
    ),
}


def obter_motivo_tool(
    nome_tool: str | None,
) -> str | None:
    """
    Explica de forma amigável por que a Tool foi escolhida.
    """
    if not nome_tool:
        return None

    return MOTIVOS_TOOLS.get(
        nome_tool,
        "A ferramenta corresponde à intenção financeira identificada.",
    )


def preparar_contexto_memoria_tools(
    memoria: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Seleciona somente informações úteis para as Tools.

    Campos principais da memória têm prioridade sobre memoria_json.
    """
    memoria = memoria or {}

    contexto = {
        chave: valor
        for chave, valor in memoria.items()
        if chave in CAMPOS_MEMORIA_PERMITIDOS and valor not in (None, "")
    }

    memoria_json = memoria.get("memoria_json")

    if isinstance(memoria_json, dict):
        for chave_origem, chave_destino in ALIASES_MEMORIA_JSON.items():
            valor = memoria_json.get(chave_origem)

            if valor not in (None, "") and chave_destino not in contexto:
                contexto[chave_destino] = valor

    return contexto


def executar_tools_para_pergunta(
    pergunta: str,
    memoria: dict[str, Any] | None = None,
    *,
    executar: bool = True,
) -> dict:
    """
    Executa o roteamento com apoio da memória persistente.
    """
    contexto = preparar_contexto_memoria_tools(memoria)

    resultado_router = rotear_tool(
        mensagem=pergunta,
        contexto=contexto,
        executar=executar,
    )

    classificacao = resultado_router.get("classificacao") or {}

    preparacao = resultado_router.get("preparacao") or {}

    execucao = resultado_router.get("execucao") or {}

    return {
        "ok": resultado_router.get("ok", False),
        "tool_identificada": classificacao.get("tool"),
        "tool_label": TOOL_LABELS.get(
            classificacao.get("tool"),
            classificacao.get("tool"),
        )
        if classificacao.get("tool")
        else None,
        "motivo_tool": obter_motivo_tool(classificacao.get("tool")),
        "intencao": classificacao.get("intencao"),
        "confianca": classificacao.get(
            "confianca",
            0.0,
        ),
        "termos_detectados": classificacao.get(
            "termos_detectados",
            [],
        ),
        "executada": resultado_router.get(
            "executada",
            False,
        ),
        "dados_ausentes": preparacao.get(
            "dados_ausentes",
            [],
        ),
        "argumentos": preparacao.get(
            "argumentos",
            {},
        ),
        "resultado": execucao.get("resultado"),
        "message": (
            execucao.get("message")
            or preparacao.get("message")
            or classificacao.get("motivo")
        ),
        "contexto_utilizado": contexto,
        "router": resultado_router,
    }


def montar_bloco_tools_prompt(
    resultado_tools: dict | None,
) -> str:
    """
    Gera um bloco seguro e estruturado para o Prompt Builder.
    """
    resultado_tools = resultado_tools or {}

    tool = resultado_tools.get("tool_identificada")

    if not tool:
        return "[TOOLS FINANCEIRAS]\nNenhuma ferramenta determinística foi acionada."

    dados_ausentes = resultado_tools.get(
        "dados_ausentes",
        [],
    )

    if dados_ausentes:
        ausentes = ", ".join(dados_ausentes)

        return f"""
[TOOLS FINANCEIRAS]
Ferramenta identificada: {tool}
Status: dados insuficientes
Dados ausentes: {ausentes}

Regras obrigatórias:
- explique quais informações ainda faltam;
- não invente valores;
- não assuma taxas, parcelas ou prazos;
- não execute cálculos incompletos;
- faça perguntas objetivas quando necessário;
- mantenha linguagem educativa.
""".strip()

    if not resultado_tools.get("executada"):
        return f"""
[TOOLS FINANCEIRAS]
Ferramenta identificada: {tool}
Status: identificada, mas não executada.
""".strip()

    resultado_json = json.dumps(
        resultado_tools.get("resultado"),
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    argumentos_json = json.dumps(
        resultado_tools.get("argumentos"),
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    return f"""
[TOOL FINANCEIRA EXECUTADA]
Ferramenta interna: {tool}
Nome amigável: {resultado_tools.get("tool_label") or tool}
Motivo da escolha: {resultado_tools.get("motivo_tool")}
Intenção: {resultado_tools.get("intencao")}
Confiança do roteamento: {resultado_tools.get("confianca")}

Argumentos utilizados:
{argumentos_json}

Resultado determinístico:
{resultado_json}

Regras obrigatórias:
- considere os números acima como calculados pelo sistema;
- não altere, arredonde novamente ou recalcule esses valores;
- não invente informações ausentes;
- explique o resultado em linguagem simples;
- diferencie cálculo, estimativa e orientação;
- não transforme o resultado em recomendação obrigatória;
- apresente possibilidades e critérios para reflexão;
- quando houver dívidas, considere essa informação na explicação;
- não afirme que uma estratégia é a melhor para o usuário;
- não determine uma divisão exata entre dívidas e reserva;
- não diga que o usuário deve separar determinado valor;
- use preferencialmente expressões como:
  "vale avaliar como esse valor se relaciona com as dívidas";
  "uma possibilidade de organização é comparar os compromissos";
  "considere verificar juros, atrasos e necessidades do mês";
- deixe claro que a decisão depende da realidade do usuário.
""".strip()


def processar_pergunta_com_tools(
    pergunta: str,
    memoria: dict[str, Any] | None = None,
    *,
    usuario_id: str | None = None,
    origem: str = "interno",
    registrar_observabilidade: bool = False,
) -> dict:
    """
    Fluxo completo para preparar Tools antes do Gemini.
    """
    inicio = perf_counter()

    resultado = executar_tools_para_pergunta(
        pergunta=pergunta,
        memoria=memoria,
        executar=True,
    )

    duracao_ms = round(
        (perf_counter() - inicio) * 1000,
        3,
    )

    bloco_prompt = montar_bloco_tools_prompt(resultado)

    resultado_final = {
        **resultado,
        "bloco_prompt": bloco_prompt,
        "duracao_ms": duracao_ms,
        "observabilidade": {
            "ok": False,
            "message": "Registro não solicitado.",
        },
    }

    if registrar_observabilidade:
        try:
            from .observability import registrar_evento_tool

            evento = registrar_evento_tool(
                usuario_id=(usuario_id or (memoria or {}).get("usuario_id")),
                pergunta=pergunta,
                resultado_tools=resultado_final,
                duracao_ms=duracao_ms,
                origem=origem,
            )

            resultado_final["observabilidade"] = evento

        except Exception as exc:
            resultado_final["observabilidade"] = {
                "ok": False,
                "message": (f"Falha não bloqueante na observabilidade: {exc}"),
            }

    return resultado_final


__all__ = [
    "CAMPOS_MEMORIA_PERMITIDOS",
    "ALIASES_MEMORIA_JSON",
    "MOTIVOS_TOOLS",
    "obter_motivo_tool",
    "preparar_contexto_memoria_tools",
    "executar_tools_para_pergunta",
    "montar_bloco_tools_prompt",
    "processar_pergunta_com_tools",
]
