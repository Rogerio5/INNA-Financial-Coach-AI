"""
Adaptador de compatibilidade dos formatadores da INNA.

A implementação real está em:

src/services/formatters/financial.py
"""

try:
    from services.formatters.financial import (
        formatar_numero,
        formatar_moeda,
        formatar_percentual,
        formatar_variacao_monetaria,
        formatar_data,
        semanas_no_mes,
        calcular_valor_semanal,
        calcular_percentual_variacao,
        formatar_comparacao_monetaria,
    )
except ImportError:
    from src.modulos.financeiro.nucleo.formatters import (
        formatar_numero,
        formatar_moeda,
        formatar_percentual,
        formatar_variacao_monetaria,
        formatar_data,
        semanas_no_mes,
        calcular_valor_semanal,
        calcular_percentual_variacao,
        formatar_comparacao_monetaria,
    )


def formatar_variacao(valor):
    """
    Compatibilidade com a função antiga.
    """
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return "-"

    sinal = "+" if numero >= 0 else "-"

    texto = formatar_numero(
        abs(numero),
        casas_decimais=2,
        idioma="pt",
    )

    return f"{sinal}{texto}"


def valor_semanal(valor_mensal):
    """
    Compatibilidade com a função antiga.
    """
    return calcular_valor_semanal(valor_mensal)


__all__ = [
    "formatar_numero",
    "formatar_moeda",
    "formatar_percentual",
    "formatar_variacao",
    "formatar_variacao_monetaria",
    "formatar_data",
    "semanas_no_mes",
    "valor_semanal",
    "calcular_valor_semanal",
    "calcular_percentual_variacao",
    "formatar_comparacao_monetaria",
]
