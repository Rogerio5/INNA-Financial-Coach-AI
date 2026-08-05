"""
Ferramenta educativa para organização de informações sobre dívidas.

A ferramenta não recomenda uma decisão.
Ela identifica dados presentes, dados ausentes e critérios de análise.
"""

from __future__ import annotations

from typing import Any


def _valor_opcional_nao_negativo(
    valor: Any,
    nome: str,
) -> float | None:
    if valor in (None, ""):
        return None

    try:
        numero = float(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{nome} deve ser numérico.") from exc

    if numero < 0:
        raise ValueError(f"{nome} não pode ser negativo.")

    return numero


def analisar_divida_educativamente(
    *,
    valor_total: float | None = None,
    parcela_mensal: float | None = None,
    taxa_juros_mensal: float | None = None,
    esta_atrasada: bool | None = None,
    quantidade_parcelas: int | None = None,
    tipo_divida: str | None = None,
) -> dict:
    """
    Organiza os dados disponíveis para reflexão educativa.
    """
    total = _valor_opcional_nao_negativo(
        valor_total,
        "valor_total",
    )

    parcela = _valor_opcional_nao_negativo(
        parcela_mensal,
        "parcela_mensal",
    )

    juros = _valor_opcional_nao_negativo(
        taxa_juros_mensal,
        "taxa_juros_mensal",
    )

    if quantidade_parcelas is not None:
        quantidade_parcelas = int(quantidade_parcelas)

        if quantidade_parcelas < 0:
            raise ValueError("quantidade_parcelas não pode ser negativa.")

    dados_ausentes = []

    if total is None:
        dados_ausentes.append("valor_total")

    if parcela is None:
        dados_ausentes.append("parcela_mensal")

    if juros is None:
        dados_ausentes.append("taxa_juros_mensal")

    if esta_atrasada is None:
        dados_ausentes.append("esta_atrasada")

    if quantidade_parcelas is None:
        dados_ausentes.append("quantidade_parcelas")

    criterios = [
        "verificar o valor total",
        "verificar o valor da parcela",
        "verificar a taxa de juros",
        "verificar se existem atrasos",
        "verificar o prazo restante",
        "comparar o impacto no orçamento",
    ]

    sinais_atencao = []

    if esta_atrasada is True:
        sinais_atencao.append("divida_atrasada")

    if juros is not None and juros > 0:
        sinais_atencao.append("possui_juros_informados")

    if parcela is not None and parcela > 0:
        sinais_atencao.append("parcela_compromete_orcamento")

    return {
        "tipo_divida": (str(tipo_divida).strip() if tipo_divida else None),
        "valor_total": total,
        "parcela_mensal": parcela,
        "taxa_juros_mensal": juros,
        "esta_atrasada": esta_atrasada,
        "quantidade_parcelas": quantidade_parcelas,
        "dados_ausentes": dados_ausentes,
        "tem_dados_suficientes": (len(dados_ausentes) == 0),
        "criterios_para_avaliar": criterios,
        "sinais_de_atencao": sinais_atencao,
        "mensagem_educativa": (
            "Os dados foram organizados para análise. "
            "A decisão depende da realidade financeira, "
            "dos juros, dos prazos e das necessidades do orçamento."
        ),
    }


__all__ = [
    "analisar_divida_educativamente",
]
