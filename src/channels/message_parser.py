import re


def _to_float(value: str) -> float:
    """
    Converte valores como 3000, 3.000, 3.000,50 ou 3000.50 para float.
    """
    value = value.strip()
    value = value.replace("R$", "").replace("r$", "").strip()

    if "," in value:
        value = value.replace(".", "").replace(",", ".")
    else:
        value = value.replace(",", "")

    return float(value)


def _extract_money(text: str, patterns: list[str], default: float = 0.0) -> float:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _to_float(match.group(1))
    return default


def _extract_text(text: str, patterns: list[str], default: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return default


def parse_financial_message(message: str) -> dict:
    """
    Extrai dados financeiros básicos de uma mensagem enviada no Telegram.

    Formato recomendado:

    Nome: Ronaldo Demo
    Renda: 3000
    Gastos fixos: 1400
    Gastos variáveis: 700
    Dívidas: 300
    Reserva: 500
    Objetivo: Organizar minha vida financeira
    """
    text = message.strip()

    nome = _extract_text(
        text,
        [
            r"nome\s*:\s*(.+)",
            r"name\s*:\s*(.+)",
            r"nombre\s*:\s*(.+)",
        ],
        default="Usuário Telegram",
    )

    objetivo = _extract_text(
        text,
        [
            r"objetivo\s*:\s*(.+)",
            r"goal\s*:\s*(.+)",
            r"objetivo financeiro\s*:\s*(.+)",
        ],
        default="Organizar minha vida financeira",
    )

    renda = _extract_money(
        text,
        [
            r"renda\s*:\s*R?\$?\s*([\d\.,]+)",
            r"renda mensal\s*:\s*R?\$?\s*([\d\.,]+)",
            r"sal[aá]rio\s*:\s*R?\$?\s*([\d\.,]+)",
            r"ganhei\s*R?\$?\s*([\d\.,]+)",
            r"income\s*:\s*R?\$?\s*([\d\.,]+)",
            r"ingresos\s*:\s*R?\$?\s*([\d\.,]+)",
        ],
    )

    gastos_fixos = _extract_money(
        text,
        [
            r"gastos?\s*fixos?\s*:\s*R?\$?\s*([\d\.,]+)",
            r"fixos?\s*:\s*R?\$?\s*([\d\.,]+)",
            r"fixed expenses\s*:\s*R?\$?\s*([\d\.,]+)",
            r"gastos fijos\s*:\s*R?\$?\s*([\d\.,]+)",
        ],
    )

    gastos_variaveis = _extract_money(
        text,
        [
            r"gastos?\s*vari[aá]veis\s*:\s*R?\$?\s*([\d\.,]+)",
            r"vari[aá]veis\s*:\s*R?\$?\s*([\d\.,]+)",
            r"variable expenses\s*:\s*R?\$?\s*([\d\.,]+)",
            r"gastos variables\s*:\s*R?\$?\s*([\d\.,]+)",
        ],
    )

    dividas = _extract_money(
        text,
        [
            r"d[ií]vidas?\s*:\s*R?\$?\s*([\d\.,]+)",
            r"d[ií]vidas?\s*mensais\s*:\s*R?\$?\s*([\d\.,]+)",
            r"d[ií]vida\s*mensal\s*:\s*R?\$?\s*([\d\.,]+)",
            r"debts?\s*:\s*R?\$?\s*([\d\.,]+)",
            r"deudas?\s*:\s*R?\$?\s*([\d\.,]+)",
        ],
    )

    reserva = _extract_money(
        text,
        [
            r"reserva\s*:\s*R?\$?\s*([\d\.,]+)",
            r"reserva atual\s*:\s*R?\$?\s*([\d\.,]+)",
            r"guardado\s*:\s*R?\$?\s*([\d\.,]+)",
            r"guardado\s*R?\$?\s*([\d\.,]+)",
            r"savings\s*:\s*R?\$?\s*([\d\.,]+)",
            r"ahorro\s*:\s*R?\$?\s*([\d\.,]+)",
        ],
    )

    if renda <= 0:
        raise ValueError(
            "Não consegui identificar sua renda. Envie no formato: Renda: 3000"
        )

    return {
        "nome": nome,
        "renda_mensal": renda,
        "gastos_fixos": gastos_fixos,
        "gastos_variaveis": gastos_variaveis,
        "dividas_mensais": dividas,
        "reserva_atual": reserva,
        "objetivo": objetivo,
    }
