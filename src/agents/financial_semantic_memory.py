"""
Memória financeira semântica de curto prazo da INNA.

Responsabilidades:
- recuperar somente mensagens anteriores do usuário;
- extrair dados financeiros sem inventar valores;
- preservar a prioridade da mensagem atual;
- resolver consultas simples de saldo;
- não substituir o diagnóstico financeiro formal.
"""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, InvalidOperation
import re
import unicodedata
from typing import Any, Mapping, Sequence

from src.services.memory.extractor import (
    extrair_memoria_da_mensagem_inna,
)


_BALANCE_TERMS = {
    "meu saldo",
    "saldo mensal",
    "qual era meu saldo",
    "qual foi meu saldo",
    "quanto sobrava",
    "quanto sobrou",
    "quanto me sobrava",
    "monthly balance",
    "my balance",
}

_PREVIOUS_CONTEXT_TERMS = {
    "antes",
    "anterior",
    "anteriormente",
    "informei",
    "falei",
    "disse",
    "mencionei",
    "dados anteriores",
    "informacoes anteriores",
    "informações anteriores",
    "previous",
    "earlier",
    "before",
}

_INCOME_KEYS = (
    "renda_mensal",
    "renda",
    "income",
    "monthly_income",
)

_TOTAL_EXPENSE_KEYS = (
    "gastos_mensais_total",
    "gastos_mensais",
    "gastos",
    "despesas_mensais",
    "despesas",
    "expenses",
    "monthly_expenses",
)

_FIXED_EXPENSE_KEYS = (
    "gastos_fixos",
    "despesas_fixas",
    "fixed_expenses",
)

_VARIABLE_EXPENSE_KEYS = (
    "gastos_variaveis",
    "gastos_variáveis",
    "despesas_variaveis",
    "despesas_variáveis",
    "variable_expenses",
)

_DEBT_KEYS = (
    "dividas_mensais",
    "dívidas_mensais",
    "parcelas_mensais",
    "monthly_debts",
)

_EMPTY_DEFAULT_KEYS = {
    "tem_memoria",
    "nome",
    "idioma",
    "moeda",
    "preferencia_linguagem",
    "nivel_confianca",
    "tags",
}

_MONEY_VALUE_PATTERN = (
    r"(?:r\$\s*)?"
    r"(-?(?:"
    r"\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?"
    r"|\d+(?:,\d{1,2})?"
    r"|\d+(?:\.\d{1,2})?"
    r"))"
    r"(?!\d)"
)

_INCOME_PATTERNS = (
    re.compile(
        r"(?:minha\s+)?renda(?:\s+mensal)?"
        r"\s*(?:e|é|era|:|de)?\s*" + _MONEY_VALUE_PATTERN,
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"(?:eu\s+)?(?:ganho|recebo)"
        r"\s*(?:por\s+m[eê]s|mensalmente)?"
        r"\s*(?:é|era|:|de)?\s*" + _MONEY_VALUE_PATTERN,
        flags=re.IGNORECASE,
    ),
)

_TOTAL_EXPENSE_PATTERNS = (
    re.compile(
        r"(?:meus\s+)?gastos"
        r"(?!\s+(?:fixos|vari[aá]veis))"
        r"(?:\s+mensais)?"
        r"\s*(?:s[aã]o|eram|e|é|era|:|de)?\s*" + _MONEY_VALUE_PATTERN,
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"(?:minhas\s+)?despesas"
        r"(?!\s+(?:fixas|vari[aá]veis))"
        r"(?:\s+mensais)?"
        r"\s*(?:s[aã]o|eram|e|é|era|:|de)?\s*" + _MONEY_VALUE_PATTERN,
        flags=re.IGNORECASE,
    ),
)

_FIXED_EXPENSE_PATTERNS = (
    re.compile(
        r"(?:gastos|despesas)\s+fix(?:os|as)"
        r"\s*(?:s[aã]o|eram|e|é|era|:|de)?\s*" + _MONEY_VALUE_PATTERN,
        flags=re.IGNORECASE,
    ),
)

_VARIABLE_EXPENSE_PATTERNS = (
    re.compile(
        r"(?:gastos|despesas)\s+vari[aá]veis"
        r"\s*(?:s[aã]o|eram|e|é|era|:|de)?\s*" + _MONEY_VALUE_PATTERN,
        flags=re.IGNORECASE,
    ),
)

_DEBT_PATTERNS = (
    re.compile(
        r"(?:d[ií]vidas|parcelas)"
        r"(?:\s+mensais)?"
        r"\s*(?:s[aã]o|eram|e|é|era|:|de)?\s*" + _MONEY_VALUE_PATTERN,
        flags=re.IGNORECASE,
    ),
)


def _normalize_text(value: Any) -> str:
    text = str(value or "").strip().lower()

    return "".join(
        character
        for character in unicodedata.normalize(
            "NFKD",
            text,
        )
        if not unicodedata.combining(character)
    )


def _contains_any(
    text: str,
    terms: set[str],
) -> bool:
    normalized = _normalize_text(text)

    return any(_normalize_text(term) in normalized for term in terms)


def _message_to_mapping(
    raw_message: Any,
) -> dict[str, Any] | None:
    if isinstance(raw_message, Mapping):
        return dict(raw_message)

    model_dump = getattr(
        raw_message,
        "model_dump",
        None,
    )

    if callable(model_dump):
        dumped = model_dump()

        if isinstance(dumped, Mapping):
            return dict(dumped)

    return None


def _normalize_history(
    raw_history: Any,
) -> list[dict[str, str]]:
    if not isinstance(raw_history, Sequence) or isinstance(
        raw_history,
        (str, bytes, bytearray),
    ):
        return []

    normalized: list[dict[str, str]] = []

    for raw_message in raw_history:
        message = _message_to_mapping(raw_message)

        if message is None:
            continue

        role = str(message.get("role", "")).strip().lower()

        content = str(message.get("content", "")).strip()

        if (
            role
            not in {
                "user",
                "assistant",
                "system",
                "tool",
            }
            or not content
        ):
            continue

        normalized.append(
            {
                "role": role,
                "content": content,
            }
        )

    return normalized


def _history_candidates(
    state: Mapping[str, Any],
) -> list[dict[str, str]]:
    context = state.get("context")

    if not isinstance(context, Mapping):
        context = {}

    normalized_selected = _normalize_history(context.get("selected_history"))

    if normalized_selected:
        return normalized_selected

    return _normalize_history(state.get("conversation_history"))


def _current_message(
    state: Mapping[str, Any],
) -> str:
    context = state.get("context")

    if not isinstance(context, Mapping):
        context = {}

    return str(
        context.get("current_message")
        or context.get("user_message")
        or state.get("user_message")
        or ""
    ).strip()


def _previous_user_messages(
    state: Mapping[str, Any],
) -> list[str]:
    current_message = _current_message(state)

    previous: list[str] = []

    for message in _history_candidates(state):
        if message["role"] != "user":
            continue

        content = message["content"]

        if current_message and content == current_message:
            continue

        previous.append(content)

    return previous


def _is_meaningful_value(
    value: Any,
) -> bool:
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, Mapping):
        return any(_is_meaningful_value(item) for item in value.values())

    if isinstance(value, (list, tuple, set)):
        return bool(value)

    return True


def _clean_extracted_memory(
    extracted: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(extracted, Mapping):
        return {}

    cleaned: dict[str, Any] = {}

    nested_data = extracted.get("dados")

    if isinstance(nested_data, Mapping):
        nested_aliases = {
            "renda_mensal": "renda_mensal",
            "gastos_mensais": ("gastos_mensais_total"),
            "gastos_mensais_total": ("gastos_mensais_total"),
            "gastos_fixos": "gastos_fixos",
            "gastos_variaveis": ("gastos_variaveis"),
            "dividas_mensais": ("dividas_mensais"),
            "valor_reserva": "reserva_atual",
            "reserva_atual": "reserva_atual",
        }

        for source_key, target_key in nested_aliases.items():
            nested_value = nested_data.get(source_key)

            if _is_meaningful_value(nested_value):
                cleaned[target_key] = deepcopy(nested_value)

    for key, value in extracted.items():
        if key in _EMPTY_DEFAULT_KEYS:
            continue

        if not _is_meaningful_value(value):
            continue

        if key == "memoria_json" and isinstance(value, Mapping):
            nested = {
                nested_key: nested_value
                for nested_key, nested_value in value.items()
                if _is_meaningful_value(nested_value)
            }

            if nested:
                cleaned[key] = nested

            continue

        cleaned[key] = deepcopy(value)

    return cleaned


def _parse_money_text(
    value: str,
) -> float | None:
    text = str(value or "").strip()

    if not text:
        return None

    text = re.sub(
        r"[^0-9,.\-]",
        "",
        text,
    )

    if not text:
        return None

    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")

    elif "," in text:
        text = text.replace(",", ".")

    try:
        result = float(text)
    except ValueError:
        return None

    if result < 0:
        return None

    return result


def _match_first_money(
    message: str,
    patterns: Sequence[re.Pattern[str]],
) -> float | None:
    for pattern in patterns:
        match = pattern.search(message)

        if match is None:
            continue

        parsed = _parse_money_text(match.group(1))

        if parsed is not None:
            return parsed

    return None


def _deterministic_message_fallback(
    message: str,
) -> dict[str, Any]:
    fallback: dict[str, Any] = {}

    income = _match_first_money(
        message,
        _INCOME_PATTERNS,
    )

    total_expenses = _match_first_money(
        message,
        _TOTAL_EXPENSE_PATTERNS,
    )

    fixed_expenses = _match_first_money(
        message,
        _FIXED_EXPENSE_PATTERNS,
    )

    variable_expenses = _match_first_money(
        message,
        _VARIABLE_EXPENSE_PATTERNS,
    )

    monthly_debts = _match_first_money(
        message,
        _DEBT_PATTERNS,
    )

    if income is not None:
        fallback["renda_mensal"] = income

    if total_expenses is not None:
        fallback["gastos_mensais_total"] = total_expenses

    if fixed_expenses is not None:
        fallback["gastos_fixos"] = fixed_expenses

    if variable_expenses is not None:
        fallback["gastos_variaveis"] = variable_expenses

    if monthly_debts is not None:
        fallback["dividas_mensais"] = monthly_debts

    return fallback


def _extract_message_financial_values(
    message: str,
) -> dict[str, Any]:
    extracted: dict[str, Any] = {}

    try:
        raw_extracted = extrair_memoria_da_mensagem_inna(message)

        extracted.update(_clean_extracted_memory(raw_extracted))

    except Exception:
        pass

    fallback = _deterministic_message_fallback(message)

    for key, value in fallback.items():
        extracted.setdefault(key, value)

    return extracted


def extract_financial_memory_from_history(
    state: Mapping[str, Any] | None,
    *,
    max_user_messages: int = 12,
) -> dict[str, Any]:
    """
    Extrai memória financeira das mensagens anteriores.

    Mensagens mais recentes possuem prioridade sobre
    mensagens mais antigas. A mensagem atual não é incluída.
    """
    safe_state = dict(state) if isinstance(state, Mapping) else {}

    max_user_messages = max(
        1,
        min(int(max_user_messages), 50),
    )

    messages = _previous_user_messages(safe_state)[-max_user_messages:]

    merged: dict[str, Any] = {}

    for message in messages:
        extracted = _extract_message_financial_values(message)

        for key, value in extracted.items():
            if _is_meaningful_value(value):
                # Mensagens mais recentes sobrescrevem
                # informações antigas do mesmo campo.
                merged[key] = deepcopy(value)

    return deepcopy(merged)


def _first_value(
    data: Mapping[str, Any],
    keys: Sequence[str],
) -> Any:
    for key in keys:
        value = data.get(key)

        if value is not None:
            return value

    memory_json = data.get("memoria_json")

    if isinstance(memory_json, Mapping):
        for key in keys:
            value = memory_json.get(key)

            if value is not None:
                return value

    return None


def _to_decimal(
    value: Any,
) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, Decimal):
        return value

    if isinstance(value, (int, float)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return None

    parsed = _parse_money_text(str(value))

    if parsed is None:
        return None

    return Decimal(str(parsed))


def _total_expenses(
    memory: Mapping[str, Any],
) -> Decimal | None:
    aggregate = _to_decimal(
        _first_value(
            memory,
            _TOTAL_EXPENSE_KEYS,
        )
    )

    if aggregate is not None:
        return aggregate

    fixed = _to_decimal(
        _first_value(
            memory,
            _FIXED_EXPENSE_KEYS,
        )
    )

    variable = _to_decimal(
        _first_value(
            memory,
            _VARIABLE_EXPENSE_KEYS,
        )
    )

    debt = _to_decimal(
        _first_value(
            memory,
            _DEBT_KEYS,
        )
    )

    components = [
        value
        for value in (
            fixed,
            variable,
            debt,
        )
        if value is not None
    ]

    if not components:
        return None

    return sum(
        components,
        Decimal("0"),
    )


def _format_money(
    value: Decimal,
    currency: str,
) -> str:
    currency = str(currency or "BRL").strip().upper()

    normalized = value.quantize(Decimal("0.01"))

    raw = f"{normalized:,.2f}"

    if currency == "BRL":
        localized = raw.replace(",", "_").replace(".", ",").replace("_", ".")

        return f"R$ {localized}"

    return f"{currency} {raw}"


def is_simple_balance_follow_up(
    message: str,
) -> bool:
    return _contains_any(
        message,
        _BALANCE_TERMS,
    ) and _contains_any(
        message,
        _PREVIOUS_CONTEXT_TERMS,
    )


def resolve_simple_balance_follow_up(
    state: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Resolve saldo simples usando dados anteriores.

    Não executa diagnóstico, score, risco ou recomendação.
    Não inventa a divisão entre gastos fixos e variáveis.
    """
    safe_state = dict(state) if isinstance(state, Mapping) else {}

    message = _current_message(safe_state)

    if not is_simple_balance_follow_up(message):
        return None

    memory = extract_financial_memory_from_history(safe_state)

    income = _to_decimal(
        _first_value(
            memory,
            _INCOME_KEYS,
        )
    )

    expenses = _total_expenses(memory)

    if income is None or expenses is None:
        return None

    balance = income - expenses

    currency = (
        str(
            safe_state.get("currency")
            or safe_state.get("moeda")
            or memory.get("moeda")
            or "BRL"
        )
        .strip()
        .upper()
    )

    response = (
        "Com base nos dados financeiros informados "
        "anteriormente, sua renda mensal era "
        f"{_format_money(income, currency)}, seus gastos "
        f"mensais eram {_format_money(expenses, currency)} "
        "e seu saldo mensal estimado era "
        f"{_format_money(balance, currency)}. "
        "Este é um cálculo simples de renda menos gastos; "
        "não recalcula score nem nível de risco."
    )

    trace = list(safe_state.get("trace", []))

    trace.append("financial_semantic_memory:simple_balance_resolved")

    return {
        "current_agent": "financial_agent",
        "response": response,
        "conversation_history": [
            {
                "role": "assistant",
                "content": response,
            }
        ],
        "trace": trace,
        "semantic_memory_used": True,
        "semantic_memory_operation": ("simple_balance"),
        "semantic_memory_sources": {
            "renda_mensal": ("conversation_history"),
            "gastos_mensais": ("conversation_history"),
        },
    }


__all__ = [
    "extract_financial_memory_from_history",
    "is_simple_balance_follow_up",
    "resolve_simple_balance_follow_up",
]
