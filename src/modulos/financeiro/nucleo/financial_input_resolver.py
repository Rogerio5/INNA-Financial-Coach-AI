"""
Resolução determinística de dados financeiros para agentes.

Este módulo separa:
- extração de dados;
- precedência entre mensagem e memória;
- verificação de campos ausentes;
- preparação dos argumentos da ferramenta financeira.

Nenhum cálculo financeiro é realizado aqui.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from math import isfinite
import re
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from src.channels.message_parser import (
    parse_financial_message,
)
from src.compartilhado.memoria.extractor import (
    extrair_memoria_da_mensagem_inna,
)


MAX_MONETARY_VALUE = Decimal(
    "1000000000000"
)

REQUIRED_FINANCIAL_FIELDS = (
    "renda_mensal",
    "gastos_fixos",
    "gastos_variaveis",
    "dividas_mensais",
    "reserva_atual",
)

FIELD_LABELS = {
    "renda_mensal": "renda mensal",
    "gastos_fixos": "gastos fixos mensais",
    "gastos_variaveis": (
        "gastos variáveis mensais"
    ),
    "dividas_mensais": (
        "dívidas ou parcelas mensais"
    ),
    "reserva_atual": "reserva atual",
}

ALIASES = {
    "renda_mensal": (
        "renda_mensal",
        "monthly_income",
        "renda",
        "income",
    ),
    "gastos_fixos": (
        "gastos_fixos",
        "fixed_expenses",
        "despesas_fixas",
    ),
    "gastos_variaveis": (
        "gastos_variaveis",
        "variable_expenses",
        "despesas_variaveis",
    ),
    "dividas_mensais": (
        "dividas_mensais",
        "monthly_debts",
        "debts",
        "parcelas_mensais",
    ),
    "reserva_atual": (
        "reserva_atual",
        "valor_reserva",
        "current_reserve",
        "reserve",
    ),
    "gastos_mensais_total": (
        "gastos_mensais",
        "despesas_mensais",
        "monthly_expenses",
    ),
    "possui_dividas": (
        "possui_dividas",
        "has_debts",
    ),
    "gastos_incluem_dividas": (
        "gastos_incluem_dividas",
        "expenses_include_debts",
    ),
    "moeda": (
        "moeda",
        "currency",
    ),
    "idioma": (
        "idioma",
        "language",
    ),
}

NESTED_CONTAINER_NAMES = (
    "dados",
    "data",
    "resultado",
    "result",
    "financial_data",
    "financial_inputs",
    "diagnostico_financeiro",
    "memory",
    "memoria",
    "memoria_json",
    "user_memory",
)


class FinancialInputResolution(BaseModel):
    """
    Resultado da resolução dos dados financeiros.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    ready: bool

    arguments: dict[str, Any] | None = None

    missing_fields: list[str] = Field(
        default_factory=list,
    )

    collected_data: dict[str, Any] = Field(
        default_factory=dict,
    )

    field_sources: dict[str, str] = Field(
        default_factory=dict,
    )

    warnings: list[str] = Field(
        default_factory=list,
    )

    clarification_message: str | None = None


def _normalize_text_number(
    value: str,
) -> str:
    normalized = str(value).strip()

    normalized = re.sub(
        r"(?i)\b(?:BRL|USD|EUR|R\$|US\$)\b",
        "",
        normalized,
    )

    normalized = normalized.replace(
        "\u00a0",
        "",
    ).replace(
        " ",
        "",
    )

    normalized = re.sub(
        r"[^0-9,\.\-]",
        "",
        normalized,
    )

    if "," in normalized and "." in normalized:
        if (
            normalized.rfind(",")
            > normalized.rfind(".")
        ):
            normalized = (
                normalized
                .replace(".", "")
                .replace(",", ".")
            )
        else:
            normalized = normalized.replace(
                ",",
                "",
            )

    elif "," in normalized:
        normalized = normalized.replace(
            ",",
            ".",
        )

    return normalized


def _to_non_negative_float(
    value: Any,
) -> float | None:
    if value is None or isinstance(
        value,
        bool,
    ):
        return None

    try:
        if isinstance(
            value,
            (int, float, Decimal),
        ):
            decimal_value = Decimal(
                str(value)
            )
        else:
            normalized = (
                _normalize_text_number(
                    str(value)
                )
            )

            if not normalized:
                return None

            decimal_value = Decimal(
                normalized
            )
    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        return None

    float_value = float(decimal_value)

    if not isfinite(float_value):
        return None

    if (
        decimal_value < 0
        or decimal_value
        > MAX_MONETARY_VALUE
    ):
        return None

    return round(float_value, 2)


def _to_optional_bool(
    value: Any,
) -> bool | None:
    if isinstance(value, bool):
        return value

    if value is None:
        return None

    normalized = str(
        value
    ).strip().lower()

    if normalized in {
        "true",
        "1",
        "sim",
        "yes",
    }:
        return True

    if normalized in {
        "false",
        "0",
        "não",
        "nao",
        "no",
    }:
        return False

    return None


def _get_alias_value(
    mapping: dict[str, Any],
    canonical_name: str,
) -> tuple[bool, Any]:
    for alias in ALIASES[
        canonical_name
    ]:
        if alias in mapping:
            return True, mapping[alias]

    return False, None


def _iter_relevant_mappings(
    value: Any,
    *,
    max_depth: int = 3,
):
    if (
        max_depth < 0
        or not isinstance(value, dict)
    ):
        return

    yield value

    for name in NESTED_CONTAINER_NAMES:
        nested = value.get(name)

        if isinstance(nested, dict):
            yield from _iter_relevant_mappings(
                nested,
                max_depth=max_depth - 1,
            )


def _merge_candidate(
    *,
    candidate: Any,
    source_name: str,
    collected: dict[str, Any],
    sources: dict[str, str],
    warnings: list[str],
    overwrite: bool,
) -> None:
    if not isinstance(candidate, dict):
        return

    for mapping in _iter_relevant_mappings(
        candidate
    ):
        for field_name in (
            "renda_mensal",
            "gastos_fixos",
            "gastos_variaveis",
            "dividas_mensais",
            "reserva_atual",
            "gastos_mensais_total",
        ):
            found, raw_value = (
                _get_alias_value(
                    mapping,
                    field_name,
                )
            )

            if not found:
                continue

            normalized = (
                _to_non_negative_float(
                    raw_value
                )
            )

            if normalized is None:
                warning = (
                    f"invalid_value:"
                    f"{field_name}:"
                    f"{source_name}"
                )

                if warning not in warnings:
                    warnings.append(warning)

                continue

            if (
                overwrite
                or field_name
                not in collected
            ):
                collected[field_name] = (
                    normalized
                )
                sources[field_name] = (
                    source_name
                )

        for field_name in (
            "possui_dividas",
            "gastos_incluem_dividas",
        ):
            found, raw_value = (
                _get_alias_value(
                    mapping,
                    field_name,
                )
            )

            if not found:
                continue

            normalized_bool = (
                _to_optional_bool(
                    raw_value
                )
            )

            if normalized_bool is None:
                continue

            if (
                overwrite
                or field_name
                not in collected
            ):
                collected[field_name] = (
                    normalized_bool
                )
                sources[field_name] = (
                    source_name
                )

        for field_name in (
            "moeda",
            "idioma",
        ):
            found, raw_value = (
                _get_alias_value(
                    mapping,
                    field_name,
                )
            )

            if not found:
                continue

            normalized_text = str(
                raw_value or ""
            ).strip()

            if not normalized_text:
                continue

            if field_name == "moeda":
                normalized_text = (
                    normalized_text.upper()
                )

            if (
                overwrite
                or field_name
                not in collected
            ):
                collected[field_name] = (
                    normalized_text[:10]
                )
                sources[field_name] = (
                    source_name
                )


_FINANCIAL_TEXT_PATTERNS = {
    "renda_mensal": (
        r"(?i)\b(?:minha\s+)?renda(?:\s+mensal)?"
        r"\s*(?:é|e|eh|foi|fica|está|esta|:|=)?\s*"
        r"(?:de\s+)?(?:R\$\s*)?"
        r"(?P<value>\d[\d.\s]*(?:,\d{1,2})?)"
        r"\s*(?:reais|real|BRL)?\b",
    ),
    "gastos_fixos": (
        r"(?i)\b(?:meus|minhas|os|as)?\s*"
        r"(?:gastos?|despesas?)\s+fix(?:os|as)"
        r"(?:\s+mensais?)?"
        r"\s*(?:são|sao|é|e|eh|ficam|:|=)?\s*"
        r"(?:de\s+)?(?:R\$\s*)?"
        r"(?P<value>\d[\d.\s]*(?:,\d{1,2})?)"
        r"\s*(?:reais|real|BRL)?\b",
    ),
    "gastos_variaveis": (
        r"(?i)\b(?:meus|minhas|os|as)?\s*"
        r"(?:gastos?|despesas?)\s+vari[aá]veis"
        r"(?:\s+mensais?)?"
        r"\s*(?:são|sao|é|e|eh|ficam|:|=)?\s*"
        r"(?:de\s+)?(?:R\$\s*)?"
        r"(?P<value>\d[\d.\s]*(?:,\d{1,2})?)"
        r"\s*(?:reais|real|BRL)?\b",
    ),
    "dividas_mensais": (
        r"(?i)\b(?:minhas|meus|as|os)?\s*"
        r"(?:d[ií]vidas?|parcelas?)"
        r"(?:\s+mensais?)?"
        r"\s*(?:são|sao|é|e|eh|ficam|:|=)?\s*"
        r"(?:de\s+)?(?:R\$\s*)?"
        r"(?P<value>\d[\d.\s]*(?:,\d{1,2})?)"
        r"\s*(?:reais|real|BRL)?\b",
    ),
    "reserva_atual": (
        r"(?i)\b(?:minha|a)?\s*"
        r"reserva(?:\s+atual)?"
        r"\s*(?:é|e|eh|está|esta|fica|:|=)?\s*"
        r"(?:em\s+|de\s+)?(?:R\$\s*)?"
        r"(?P<value>\d[\d.\s]*(?:,\d{1,2})?)"
        r"\s*(?:reais|real|BRL)?\b",
    ),
}


def _extract_financial_fields_from_text(
    message: str,
) -> dict[str, float]:
    """
    Extrai campos financeiros explícitos da mensagem.

    Funciona como fallback determinístico quando o parser
    principal falha ou retorna somente parte dos campos.
    """
    text = str(
        message or ""
    ).strip()

    if not text:
        return {}

    extracted: dict[str, float] = {}

    for field_name, patterns in (
        _FINANCIAL_TEXT_PATTERNS.items()
    ):
        pattern_options = (
            patterns
            if isinstance(
                patterns,
                tuple,
            )
            else (
                patterns,
            )
        )

        for pattern in pattern_options:
            match = re.search(
                pattern,
                text,
            )

            if not match:
                continue

            normalized = (
                _to_non_negative_float(
                    match.group("value")
                )
            )

            if normalized is None:
                continue

            extracted[field_name] = (
                normalized
            )

            break

    return extracted


def _safe_parse_current_message(
    message: str,
    warnings: list[str],
) -> dict:
    if not message.strip():
        return {}

    try:
        result = parse_financial_message(
            message
        )

        return (
            result
            if isinstance(result, dict)
            else {}
        )
    except Exception:
        warnings.append(
            "message_parser_failed"
        )

        return {}


def _safe_extract_memory(
    message: str,
    warnings: list[str],
) -> dict:
    if not message.strip():
        return {}

    try:
        result = (
            extrair_memoria_da_mensagem_inna(
                message
            )
        )

        return (
            result
            if isinstance(result, dict)
            else {}
        )
    except Exception:
        warnings.append(
            "memory_extractor_failed"
        )

        return {}


def _clarification_message(
    missing_fields: list[str],
) -> str:
    labels = [
        FIELD_LABELS[field]
        for field in missing_fields
    ]

    if len(labels) == 1:
        fields_text = labels[0]
    else:
        fields_text = (
            ", ".join(labels[:-1])
            + " e "
            + labels[-1]
        )

    return (
        "Para calcular seu diagnóstico com "
        "segurança, preciso que você informe "
        f"{fields_text}. "
        "Você pode enviar no formato: "
        "Renda: 3000; Gastos fixos: 1400; "
        "Gastos variáveis: 700; "
        "Dívidas: 300; Reserva: 500."
    )


def resolver_entrada_financeira(
    state: dict[str, Any],
) -> FinancialInputResolution:
    """
    Resolve os dados financeiros sem inventar valores.

    Dados da mensagem atual têm prioridade sobre
    memória persistida.
    """
    state = dict(state or {})

    collected: dict[str, Any] = {}
    sources: dict[str, str] = {}
    warnings: list[str] = []

    context = state.get("context")

    if not isinstance(context, dict):
        context = {}

    structured_response = state.get(
        "structured_response"
    )

    if not isinstance(
        structured_response,
        dict,
    ):
        structured_response = {}

    # Histórico conversacional é utilizado como
    # memória semântica de baixa prioridade.
    #
    # A mensagem atual e os dados estruturados explícitos
    # continuam tendo prioridade e podem sobrescrevê-lo.
    from src.agents.financial_semantic_memory import (
        extract_financial_memory_from_history,
    )

    history_memory = (
        extract_financial_memory_from_history(
            state
        )
    )

    # Memória é a fonte de menor prioridade.
    memory_candidates = [
        history_memory,
        state.get("memory"),
        state.get("memoria"),
        context.get("memory"),
        context.get("memoria"),
        context.get("user_memory"),
        structured_response.get("memory"),
        structured_response.get("memoria"),
    ]

    for candidate in memory_candidates:
        _merge_candidate(
            candidate=candidate,
            source_name="memory",
            collected=collected,
            sources=sources,
            warnings=warnings,
            overwrite=False,
        )

    # Contexto construído para a execução atual.
    _merge_candidate(
        candidate=context,
        source_name="context",
        collected=collected,
        sources=sources,
        warnings=warnings,
        overwrite=True,
    )

    message = str(
        context.get("current_message")
        or context.get("user_message")
        or state.get("user_message")
        or ""
    ).strip()

    extracted_memory = _safe_extract_memory(
        message,
        warnings,
    )

    _merge_candidate(
        candidate=extracted_memory,
        source_name="current_message_extractor",
        collected=collected,
        sources=sources,
        warnings=warnings,
        overwrite=True,
    )

    parsed_message = (
        _safe_parse_current_message(
            message,
            warnings,
        )
    )

    _merge_candidate(
        candidate=parsed_message,
        source_name="current_message_parser",
        collected=collected,
        sources=sources,
        warnings=warnings,
        overwrite=True,
    )

    deterministic_fallback = (
        _extract_financial_fields_from_text(
            message
        )
    )

    fallback_missing_fields = {
        field: value
        for field, value
        in deterministic_fallback.items()
        if field not in collected
    }

    _merge_candidate(
        candidate=fallback_missing_fields,
        source_name=(
            "current_message_deterministic_fallback"
        ),
        collected=collected,
        sources=sources,
        warnings=warnings,
        overwrite=False,
    )

    # Corrige resultados claramente inconsistentes
    # do parser principal. Isso ocorre, por exemplo,
    # quando "R$ 2.000,00" é interpretado como 0.0.
    fallback_repairs = {
        field: fallback_value
        for field, fallback_value
        in deterministic_fallback.items()
        if (
            field in collected
            and sources.get(field)
            == "current_message_parser"
            and collected.get(field) == 0.0
            and fallback_value > 0.0
        )
    }

    _merge_candidate(
        candidate=fallback_repairs,
        source_name=(
            "current_message_deterministic_fallback"
        ),
        collected=collected,
        sources=sources,
        warnings=warnings,
        overwrite=True,
    )

    if fallback_repairs:
        warnings.append(
            "message_parser_values_repaired_by_fallback"
        )

    if (
        deterministic_fallback
        and "message_parser_failed"
        in warnings
    ):
        warnings.append(
            "message_parser_recovered_by_fallback"
        )

    # Entradas estruturadas atuais possuem
    # a maior prioridade.
    #
    # Não enviamos o state inteiro para _merge_candidate,
    # pois ele contém estruturas como memory e context.
    # A busca recursiva nessas estruturas poderia fazer
    # uma memória antiga sobrescrever a mensagem atual.
    direct_explicit_state: dict[
        str,
        Any,
    ] = {}

    for aliases in ALIASES.values():
        for alias in aliases:
            if alias in state:
                direct_explicit_state[
                    alias
                ] = state[alias]

    explicit_candidates = [
        direct_explicit_state,
        state.get("financial_inputs"),
        context.get("financial_inputs"),
        structured_response.get(
            "financial_inputs"
        ),
        structured_response.get(
            "diagnostico_financeiro"
        ),
    ]

    for candidate in explicit_candidates:
        _merge_candidate(
            candidate=candidate,
            source_name="explicit_state",
            collected=collected,
            sources=sources,
            warnings=warnings,
            overwrite=True,
        )

    if (
        "dividas_mensais"
        not in collected
        and collected.get(
            "possui_dividas"
        ) is False
    ):
        collected["dividas_mensais"] = 0.0
        sources["dividas_mensais"] = (
            sources.get(
                "possui_dividas",
                "explicit_no_debt",
            )
        )

    if (
        "gastos_mensais_total"
        in collected
        and (
            "gastos_fixos"
            not in collected
            or "gastos_variaveis"
            not in collected
        )
    ):
        warnings.append(
            "aggregate_expenses_not_split"
        )

    collected.setdefault(
        "gastos_incluem_dividas",
        False,
    )

    collected.setdefault(
        "moeda",
        str(
            state.get("currency")
            or state.get("moeda")
            or "BRL"
        ).strip().upper(),
    )

    collected.setdefault(
        "idioma",
        str(
            state.get("language")
            or state.get("idioma")
            or "pt"
        ).strip(),
    )

    missing_fields = [
        field
        for field in REQUIRED_FINANCIAL_FIELDS
        if field not in collected
    ]

    if missing_fields:
        return FinancialInputResolution(
            ready=False,
            arguments=None,
            missing_fields=missing_fields,
            collected_data=collected,
            field_sources=sources,
            warnings=warnings,
            clarification_message=(
                _clarification_message(
                    missing_fields
                )
            ),
        )

    arguments = {
        field: collected[field]
        for field in REQUIRED_FINANCIAL_FIELDS
    }

    arguments.update({
        "gastos_incluem_dividas": bool(
            collected.get(
                "gastos_incluem_dividas",
                False,
            )
        ),
        "moeda": str(
            collected["moeda"]
        ).upper(),
        "idioma": str(
            collected["idioma"]
        ),
    })

    return FinancialInputResolution(
        ready=True,
        arguments=arguments,
        missing_fields=[],
        collected_data=collected,
        field_sources=sources,
        warnings=warnings,
        clarification_message=None,
    )


__all__ = [
    "FIELD_LABELS",
    "FinancialInputResolution",
    "REQUIRED_FINANCIAL_FIELDS",
    "resolver_entrada_financeira",
]
