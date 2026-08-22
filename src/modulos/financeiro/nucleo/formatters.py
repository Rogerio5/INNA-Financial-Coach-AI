"""
Formatadores financeiros da INNA Financial Coach AI.

Responsabilidades:
- formatar moedas;
- formatar percentuais;
- formatar variações;
- formatar datas;
- calcular valores semanais;
- adaptar apresentação por moeda e idioma.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any


SIMBOLOS_MOEDA = {
    "BRL": "R$",
    "USD": "US$",
    "EUR": "€",
    "GBP": "£",
}


def _para_decimal(valor: Any) -> Decimal | None:
    if valor is None:
        return None

    if isinstance(valor, Decimal):
        return valor

    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _separadores_por_idioma(idioma: str) -> tuple[str, str]:
    idioma = str(idioma or "pt").lower()

    if idioma.startswith(("pt", "es", "de", "it", "fr")):
        return ".", ","

    return ",", "."


def formatar_numero(
    valor: Any,
    *,
    casas_decimais: int = 2,
    idioma: str = "pt",
    valor_padrao: str = "-",
) -> str:
    numero = _para_decimal(valor)

    if numero is None:
        return valor_padrao

    casas_decimais = max(0, int(casas_decimais))

    texto = f"{numero:,.{casas_decimais}f}"

    separador_milhar, separador_decimal = _separadores_por_idioma(
        idioma
    )

    if separador_milhar == "," and separador_decimal == ".":
        return texto

    texto = (
        texto
        .replace(",", "__MILHAR__")
        .replace(".", separador_decimal)
        .replace("__MILHAR__", separador_milhar)
    )

    return texto


def formatar_moeda(
    valor: Any,
    moeda: str = "BRL",
    *,
    idioma: str = "pt",
    valor_padrao: str = "-",
) -> str:
    numero = _para_decimal(valor)

    if numero is None:
        return valor_padrao

    moeda = str(moeda or "BRL").upper()
    simbolo = SIMBOLOS_MOEDA.get(moeda, moeda)

    numero_formatado = formatar_numero(
        numero,
        casas_decimais=2,
        idioma=idioma,
        valor_padrao=valor_padrao,
    )

    if moeda in {"BRL", "EUR", "GBP"}:
        return f"{simbolo} {numero_formatado}"

    if moeda == "USD":
        return f"{simbolo} {numero_formatado}"

    return f"{simbolo} {numero_formatado}"


def formatar_percentual(
    valor: Any,
    *,
    casas_decimais: int = 1,
    idioma: str = "pt",
    incluir_sinal: bool = False,
    valor_padrao: str = "-",
) -> str:
    numero = _para_decimal(valor)

    if numero is None:
        return valor_padrao

    prefixo = ""

    if incluir_sinal and numero > 0:
        prefixo = "+"

    numero_formatado = formatar_numero(
        numero,
        casas_decimais=casas_decimais,
        idioma=idioma,
        valor_padrao=valor_padrao,
    )

    return f"{prefixo}{numero_formatado}%"


def formatar_variacao_monetaria(
    valor: Any,
    moeda: str = "BRL",
    *,
    idioma: str = "pt",
    mostrar_seta: bool = True,
    valor_padrao: str = "-",
) -> str:
    numero = _para_decimal(valor)

    if numero is None:
        return valor_padrao

    if numero > 0:
        seta = "▲ " if mostrar_seta else ""
        sinal = "+"
    elif numero < 0:
        seta = "▼ " if mostrar_seta else ""
        sinal = "-"
    else:
        seta = "• " if mostrar_seta else ""
        sinal = ""

    valor_formatado = formatar_moeda(
        abs(numero),
        moeda,
        idioma=idioma,
        valor_padrao=valor_padrao,
    )

    return f"{seta}{sinal}{valor_formatado}"


def formatar_data(
    valor: Any,
    *,
    idioma: str = "pt",
    incluir_hora: bool = True,
    valor_padrao: str = "-",
) -> str:
    if valor is None:
        return valor_padrao

    if isinstance(valor, str):
        try:
            valor = datetime.fromisoformat(
                valor.replace("Z", "+00:00")
            )
        except ValueError:
            return valor

    if isinstance(valor, datetime):
        if str(idioma).lower().startswith("en"):
            formato = (
                "%Y-%m-%d %H:%M"
                if incluir_hora
                else "%Y-%m-%d"
            )
        else:
            formato = (
                "%d/%m/%Y %H:%M"
                if incluir_hora
                else "%d/%m/%Y"
            )

        return valor.strftime(formato)

    if isinstance(valor, date):
        if str(idioma).lower().startswith("en"):
            return valor.strftime("%Y-%m-%d")

        return valor.strftime("%d/%m/%Y")

    return str(valor)


def semanas_no_mes() -> Decimal:
    """
    Aproximação usada pela INNA para cálculos simples.
    """
    return Decimal("4")


def calcular_valor_semanal(valor_mensal: Any) -> float | None:
    numero = _para_decimal(valor_mensal)

    if numero is None:
        return None

    return float(numero / semanas_no_mes())


def calcular_percentual_variacao(
    valor_anterior: Any,
    valor_atual: Any,
) -> float | None:
    anterior = _para_decimal(valor_anterior)
    atual = _para_decimal(valor_atual)

    if anterior is None or atual is None:
        return None

    if anterior == 0:
        return None

    return float(((atual - anterior) / anterior) * Decimal("100"))


def formatar_comparacao_monetaria(
    valor_anterior: Any,
    valor_atual: Any,
    moeda: str = "BRL",
    *,
    idioma: str = "pt",
) -> str:
    anterior = _para_decimal(valor_anterior)
    atual = _para_decimal(valor_atual)

    if anterior is None or atual is None:
        return "-"

    diferenca = atual - anterior

    percentual = calcular_percentual_variacao(
        anterior,
        atual,
    )

    anterior_fmt = formatar_moeda(
        anterior,
        moeda,
        idioma=idioma,
    )

    atual_fmt = formatar_moeda(
        atual,
        moeda,
        idioma=idioma,
    )

    variacao_fmt = formatar_variacao_monetaria(
        diferenca,
        moeda,
        idioma=idioma,
    )

    if percentual is None:
        return (
            f"{anterior_fmt} → {atual_fmt} "
            f"({variacao_fmt})"
        )

    percentual_fmt = formatar_percentual(
        percentual,
        casas_decimais=2,
        idioma=idioma,
        incluir_sinal=True,
    )

    return (
        f"{anterior_fmt} → {atual_fmt} "
        f"({variacao_fmt}; {percentual_fmt})"
    )


__all__ = [
    "formatar_numero",
    "formatar_moeda",
    "formatar_percentual",
    "formatar_variacao_monetaria",
    "formatar_data",
    "semanas_no_mes",
    "calcular_valor_semanal",
    "calcular_percentual_variacao",
    "formatar_comparacao_monetaria",
]
