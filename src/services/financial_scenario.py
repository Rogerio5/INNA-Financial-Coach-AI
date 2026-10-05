"""Small, conservative goal calculator: explicit BRL inputs, no inferred balances."""
from __future__ import annotations

from decimal import Decimal, ROUND_CEILING
import re
import unicodedata

_AMOUNT = r"(?P<amount>\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?|\d+(?:,\d{1,2})?)(?!\d|[.,]\d)"
_LINK = r"\s*(?:(?:de|e|eh|atual|total|mensal|em|:|=)\s*){0,3}(?:r\$\s*)?"
_LABELS = {
    "income": r"\brenda(?: mensal)?\b",
    "budget": r"\borcamento(?: mensal)?(?: de despesas)?\b",
    "spent": r"\b(?:despesas?|gastos?)(?: ja)? realizad[oa]s?\b",
    "balance": r"\bsaldo(?: (?:da|de|na) conta| bancario)\b",
    "saved": r"\b(?:reserva (?:acumulada|atual)|(?:ja )?tenho guardad[oa]s?|valor (?:ja )?guardado)\b",
    "target": r"\b(?:meta(?: de reserva| financeira)?|objetivo(?: de reserva)?|quero (?:juntar|guardar))\b",
}
_MONTH_WORDS = dict(zip(
    ("um", "dois", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze"),
    range(1, 13),
))


def _normalize(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower())
                   if not unicodedata.combining(c))


def _money(value: Decimal) -> str:
    return "R$ " + f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def answer_financial_scenario(question: str, language: str = "pt") -> dict | None:
    """Handle an unambiguous goal scenario; leave other requests to normal RAG.

    No guessed fields, rates, currencies or mixed scenarios. Amounts use the
    Brazilian decimal convention. Monthly contributions round UP to cents so
    the suggested total never falls short of the target.
    """
    if not language.lower().replace("_", "-").startswith("pt"):
        return None
    text = _normalize(question)
    if not re.search(r"\b(?:calcule|calcular|quanto|aporte|planej\w*)\b", text):
        return None
    if re.search(r"€|\bus\$|\busd\b|\beur\b|\bdolar|\bjuros\b|\brendimento|\binflacao|\btaxa\b|\bpor cento\b|%", text):
        return None
    values: dict[str, Decimal] = {}
    for field, label in _LABELS.items():
        matches = list(re.finditer(label + _LINK + _AMOUNT, text))
        # A correction or two scenarios should never silently pick one number.
        if len(matches) > 1:
            return None
        if matches:
            raw = matches[0].group("amount")
            value = Decimal(raw.replace(".", "").replace(",", "."))
            if value > Decimal("1000000000"):
                return None
            values[field] = value
    if re.search(r"\d+\s+(?:ou|a|ate)\s+\d+\s+meses", text):
        return None
    periods = re.findall(r"\b(\d+|" + "|".join(_MONTH_WORDS) + r")\s+mes(?:es)?\b", text)
    months_set = {int(p) if p.isdigit() else _MONTH_WORDS[p] for p in periods}
    if len(months_set) != 1 or not {"target", "saved"}.issubset(values):
        return None
    months = months_set.pop()
    if not 1 <= months <= 1200 or values["target"] <= 0:
        return None
    # Explicit negatives/alternate numeric conventions are not partially parsed.
    if re.search(r"(?:r\$\s*)?-\s*\d|\d\.\d{1,2}(?!\d)|\d+,\d{3}", text):
        return None
    remaining = max(Decimal(0), values["target"] - values["saved"])
    monthly = (remaining / months).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    lines = ["Com os valores informados, este é o seu planejamento:"]
    for field, title in (("income", "Renda mensal"), ("budget", "Orçamento de despesas (planejado)"),
                         ("spent", "Gastos realizados até agora"), ("balance", "Saldo da conta informado")):
        if field in values:
            lines.append(f"• {title}: {_money(values[field])}.")
    lines += ["", "Sua meta", f"• Objetivo: {_money(values['target'])}.",
              f"• Já reservado: {_money(values['saved'])}.",
              f"• Falta guardar: {_money(remaining)}."]
    if remaining:
        lines.append(f"• Para {months} meses: {_money(monthly)} por mês, sem considerar rendimentos.")
        lines.append("O aporte foi arredondado para cima em centavos; ajuste o último depósito ao valor que faltar.")
    else:
        lines.append("A reserva informada já alcançou a meta. Não é necessário novo aporte para esse objetivo.")
    if {"income", "budget"}.issubset(values):
        planned = values["income"] - values["budget"]
        lines += ["", f"Sobra mensal planejada: {_money(values['income'])} − {_money(values['budget'])} = {_money(planned)}."]
        if remaining:
            if planned >= monthly:
                lines.append(f"Após o aporte da meta, restariam {_money(planned - monthly)} no orçamento planejado.")
            else:
                lines.append(f"O aporte supera a sobra planejada em {_money(monthly - planned)}. Revise o prazo, a meta ou as despesas antes de assumir esse valor.")
    if any(k in values for k in ("budget", "spent", "balance")):
        lines += ["", "Como ler os números",
                  "Orçamento é o plano de despesas. Gastos realizados são o que já saiu. Saldo da conta é o valor disponível informado por você; ele não é substituído pela renda menos os gastos registrados.",
                  "A reserva pode já fazer parte do saldo da conta. Não some os dois sem confirmar onde o dinheiro está."]
    lines += ["", "Cálculo feito apenas com os dados desta mensagem. Não houve consulta a banco nem movimentação de dinheiro."]
    return {"resposta": "\n".join(lines), "fontes": [], "modo": "financial_goal_calculation",
            "calculation": {"target": str(values["target"]), "saved": str(values["saved"]),
                            "remaining": str(remaining), "monthly": str(monthly), "months": months,
                            "currency": "BRL", "assumption": "no_returns"}}
