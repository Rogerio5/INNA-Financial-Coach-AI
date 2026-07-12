"""
Roteador determinístico de ferramentas financeiras da INNA.

Responsabilidades:
- identificar a intenção principal da mensagem;
- escolher uma ferramenta registrada;
- montar argumentos usando contexto estruturado;
- informar quais dados ainda estão faltando;
- executar a ferramenta quando houver dados suficientes.

O roteador não utiliza Gemini.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from src.tools.registry import executar_tool


def normalizar_texto(texto: str | None) -> str:
    """
    Normaliza texto para classificação por regras.
    """
    texto = str(texto or "").strip().lower()

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    ).encode(
        "ascii",
        "ignore",
    ).decode("ascii")

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto


def _tem_algum_termo(
    texto: str,
    termos: list[str],
) -> bool:
    return any(
        termo in texto
        for termo in termos
    )


def identificar_intencao_tool(
    mensagem: str,
) -> dict:
    """
    Identifica a ferramenta mais adequada para a mensagem.
    """
    texto = normalizar_texto(mensagem)

    if not texto:
        return {
            "ok": False,
            "intencao": "indefinida",
            "tool": None,
            "confianca": 0.0,
            "motivo": "Mensagem vazia.",
        }

    regras = [
        {
            "intencao": "parcelamento_sem_juros",
            "tool": "simular_parcelamento_sem_juros",
            "termos": [
                "parcelar",
                "parcelamento",
                "quantas parcelas",
                "valor da parcela",
                "sem juros",
            ],
        },
        {
            "intencao": "capacidade_semanal",
            "tool": "calcular_capacidade_semanal",
            "termos": [
                "por semana",
                "semanal",
                "guardar na semana",
                "guardar por semana",
                "quanto por semana",
            ],
        },
        {
            "intencao": "analise_divida",
            "tool": "analisar_divida_educativamente",
            "termos": [
                "divida",
                "dividas",
                "endividado",
                "juros",
                "atrasada",
                "parcela atrasada",
                "negociar",
            ],
        },
        {
            "intencao": "simulacao_reserva",
            "tool": "simular_formacao_reserva",
            "termos": [
                "formar reserva",
                "criar reserva",
                "reserva financeira",
                "quanto tempo para guardar",
                "quanto tempo para juntar",
                "atingir a meta",
            ],
        },
        {
            "intencao": "simulacao_meta",
            "tool": "simular_meta_por_aporte",
            "termos": [
                "aporte",
                "meta financeira",
                "alcancar uma meta",
                "juntar por mes",
                "guardar todo mes",
            ],
        },
        {
            "intencao": "analise_orcamento",
            "tool": "analisar_orcamento",
            "termos": [
                "orcamento",
                "renda",
                "gastos",
                "saldo",
                "despesas",
                "quanto sobra",
                "dinheiro sobrando",
                "comprometimento da renda",
            ],
        },
    ]

    candidatos = []

    for regra in regras:
        correspondencias = [
            termo
            for termo in regra["termos"]
            if termo in texto
        ]

        if correspondencias:
            candidatos.append({
                "intencao": regra["intencao"],
                "tool": regra["tool"],
                "correspondencias": correspondencias,
                "pontuacao": len(correspondencias),
            })

    if not candidatos:
        return {
            "ok": False,
            "intencao": "indefinida",
            "tool": None,
            "confianca": 0.0,
            "motivo": (
                "Nenhuma ferramenta financeira foi "
                "identificada para a mensagem."
            ),
        }

    candidatos.sort(
        key=lambda item: item["pontuacao"],
        reverse=True,
    )

    escolhido = candidatos[0]

    confianca = min(
        0.55 + (
            escolhido["pontuacao"] * 0.15
        ),
        0.95,
    )

    return {
        "ok": True,
        "intencao": escolhido["intencao"],
        "tool": escolhido["tool"],
        "confianca": round(confianca, 2),
        "termos_detectados": escolhido[
            "correspondencias"
        ],
        "candidatos": candidatos,
        "motivo": "Intenção identificada por regras determinísticas.",
    }


def extrair_contexto_basico_mensagem(
    mensagem: str | None,
) -> dict[str, Any]:
    """
    Extrai sinais simples e determinísticos da mensagem.

    Esta função não substitui o extrator financeiro principal.
    Ela complementa o contexto das Tools com informações explícitas.
    """
    texto = normalizar_texto(mensagem)
    contexto: dict[str, Any] = {}

    if not texto:
        return contexto

    termos_atraso = [
        "divida atrasada",
        "parcela atrasada",
        "esta atrasada",
        "estou atrasado",
        "em atraso",
        "vencida",
    ]

    termos_sem_atraso = [
        "nao esta atrasada",
        "nao esta em atraso",
        "esta em dia",
        "parcelas em dia",
    ]

    if _tem_algum_termo(
        texto,
        termos_sem_atraso,
    ):
        contexto["esta_atrasada"] = False

    else:
        possui_termo_divida = _tem_algum_termo(
            texto,
            [
                "divida",
                "parcela",
                "fatura",
                "cartao",
                "emprestimo",
                "financiamento",
                "boleto",
            ],
        )

        possui_termo_atraso = _tem_algum_termo(
            texto,
            [
                "atrasada",
                "atrasado",
                "em atraso",
                "vencida",
                "vencido",
            ],
        )

        if (
            _tem_algum_termo(texto, termos_atraso)
            or (
                possui_termo_divida
                and possui_termo_atraso
            )
        ):
            contexto["esta_atrasada"] = True

    tipos_divida = {
        "cartao": [
            "cartao",
            "fatura",
            "rotativo",
        ],
        "cheque_especial": [
            "cheque especial",
        ],
        "emprestimo": [
            "emprestimo",
        ],
        "financiamento": [
            "financiamento",
        ],
        "boleto": [
            "boleto",
        ],
    }

    for tipo, termos in tipos_divida.items():
        if _tem_algum_termo(texto, termos):
            contexto["tipo_divida"] = tipo
            break

    return contexto


def mesclar_contextos_tool(
    contexto_memoria: dict[str, Any] | None,
    contexto_mensagem: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Combina memória e dados explícitos da mensagem.

    Dados da mensagem têm prioridade por serem mais recentes.
    """
    resultado = dict(
        contexto_memoria or {}
    )

    for chave, valor in (
        contexto_mensagem or {}
    ).items():
        if valor is not None:
            resultado[chave] = valor

    return resultado


def _primeiro_valor(
    contexto: dict[str, Any],
    chaves: list[str],
    padrao: Any = None,
) -> Any:
    for chave in chaves:
        valor = contexto.get(chave)

        if valor not in (None, ""):
            return valor

    return padrao


def montar_argumentos_tool(
    nome_tool: str,
    contexto: dict[str, Any] | None = None,
) -> dict:
    """
    Monta os argumentos de uma ferramenta a partir do contexto.
    """
    contexto = contexto or {}

    if nome_tool == "analisar_orcamento":
        argumentos = {
            "renda_mensal": _primeiro_valor(
                contexto,
                ["renda_mensal", "renda"],
            ),
            "gastos_mensais": _primeiro_valor(
                contexto,
                ["gastos_mensais", "gastos"],
            ),
            "dividas_mensais": _primeiro_valor(
                contexto,
                [
                    "dividas_mensais",
                    "parcelas_mensais",
                ],
                0.0,
            ),
        }

        obrigatorios = [
            "renda_mensal",
            "gastos_mensais",
        ]

    elif nome_tool == "calcular_capacidade_semanal":
        argumentos = {
            "valor_mensal": _primeiro_valor(
                contexto,
                [
                    "valor_mensal",
                    "valor_reserva",
                    "capacidade_mensal",
                ],
            ),
            "semanas_por_mes": _primeiro_valor(
                contexto,
                ["semanas_por_mes"],
                4.0,
            ),
        }

        obrigatorios = [
            "valor_mensal",
        ]

    elif nome_tool == "simular_formacao_reserva":
        argumentos = {
            "valor_mensal": _primeiro_valor(
                contexto,
                [
                    "valor_mensal",
                    "aporte_mensal",
                    "valor_reserva",
                ],
            ),
            "meta_total": _primeiro_valor(
                contexto,
                [
                    "meta_total",
                    "meta_financeira",
                ],
            ),
            "valor_inicial": _primeiro_valor(
                contexto,
                [
                    "valor_inicial",
                    "saldo_inicial",
                ],
                0.0,
            ),
        }

        obrigatorios = [
            "valor_mensal",
            "meta_total",
        ]

    elif nome_tool == "analisar_divida_educativamente":
        argumentos = {
            "valor_total": _primeiro_valor(
                contexto,
                ["valor_total", "valor_divida"],
            ),
            "parcela_mensal": _primeiro_valor(
                contexto,
                [
                    "parcela_mensal",
                    "valor_parcela",
                ],
            ),
            "taxa_juros_mensal": _primeiro_valor(
                contexto,
                [
                    "taxa_juros_mensal",
                    "juros_mensais",
                ],
            ),
            "esta_atrasada": _primeiro_valor(
                contexto,
                [
                    "esta_atrasada",
                    "divida_atrasada",
                ],
            ),
            "quantidade_parcelas": _primeiro_valor(
                contexto,
                [
                    "quantidade_parcelas",
                    "parcelas_restantes",
                ],
            ),
            "tipo_divida": _primeiro_valor(
                contexto,
                ["tipo_divida"],
            ),
        }

        obrigatorios = []

    elif nome_tool == "simular_parcelamento_sem_juros":
        argumentos = {
            "valor_total": _primeiro_valor(
                contexto,
                ["valor_total", "valor_compra"],
            ),
            "quantidade_parcelas": _primeiro_valor(
                contexto,
                [
                    "quantidade_parcelas",
                    "parcelas",
                ],
            ),
        }

        obrigatorios = [
            "valor_total",
            "quantidade_parcelas",
        ]

    elif nome_tool == "simular_meta_por_aporte":
        argumentos = {
            "meta_total": _primeiro_valor(
                contexto,
                [
                    "meta_total",
                    "meta_financeira",
                ],
            ),
            "aporte_mensal": _primeiro_valor(
                contexto,
                [
                    "aporte_mensal",
                    "valor_mensal",
                    "valor_reserva",
                ],
            ),
            "saldo_inicial": _primeiro_valor(
                contexto,
                [
                    "saldo_inicial",
                    "valor_inicial",
                ],
                0.0,
            ),
        }

        obrigatorios = [
            "meta_total",
            "aporte_mensal",
        ]

    else:
        return {
            "ok": False,
            "tool": nome_tool,
            "argumentos": {},
            "dados_ausentes": [],
            "message": "Ferramenta não suportada pelo roteador.",
        }

    dados_ausentes = [
        campo
        for campo in obrigatorios
        if argumentos.get(campo) in (None, "")
    ]

    argumentos_limpos = {
        chave: valor
        for chave, valor in argumentos.items()
        if valor is not None
    }

    return {
        "ok": len(dados_ausentes) == 0,
        "tool": nome_tool,
        "argumentos": argumentos_limpos,
        "dados_ausentes": dados_ausentes,
        "message": (
            "Argumentos preparados."
            if not dados_ausentes
            else "Ainda faltam dados para executar a ferramenta."
        ),
    }


def rotear_tool(
    mensagem: str,
    contexto: dict[str, Any] | None = None,
    *,
    executar: bool = True,
) -> dict:
    """
    Identifica, prepara e opcionalmente executa uma Tool.
    """
    classificacao = identificar_intencao_tool(
        mensagem
    )

    if not classificacao.get("ok"):
        return {
            "ok": False,
            "executada": False,
            "classificacao": classificacao,
            "preparacao": None,
            "execucao": None,
        }

    nome_tool = classificacao["tool"]

    contexto_mensagem = (
        extrair_contexto_basico_mensagem(
            mensagem
        )
    )

    contexto_completo = mesclar_contextos_tool(
        contexto_memoria=contexto,
        contexto_mensagem=contexto_mensagem,
    )

    preparacao = montar_argumentos_tool(
        nome_tool,
        contexto_completo,
    )

    if not preparacao.get("ok"):
        return {
            "ok": False,
            "executada": False,
            "classificacao": classificacao,
            "preparacao": preparacao,
            "execucao": None,
        }

    if not executar:
        return {
            "ok": True,
            "executada": False,
            "classificacao": classificacao,
            "preparacao": preparacao,
            "execucao": None,
        }

    execucao = executar_tool(
        nome_tool,
        preparacao["argumentos"],
    )

    return {
        "ok": execucao.get("ok", False),
        "executada": True,
        "classificacao": classificacao,
        "preparacao": preparacao,
        "execucao": execucao,
    }


__all__ = [
    "normalizar_texto",
    "extrair_contexto_basico_mensagem",
    "mesclar_contextos_tool",
    "identificar_intencao_tool",
    "montar_argumentos_tool",
    "rotear_tool",
]
