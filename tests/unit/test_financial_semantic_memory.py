from __future__ import annotations

from src.agents.financial_input_resolver import (
    resolver_entrada_financeira,
)
from src.agents.financial_semantic_memory import (
    extract_financial_memory_from_history,
    is_simple_balance_follow_up,
    resolve_simple_balance_follow_up,
)


def _state(
    current_message: str,
    history: list[dict[str, str]],
) -> dict:
    return {
        "user_message": current_message,
        "thread_id": "semantic-memory-test",
        "currency": "BRL",
        "conversation_history": [
            *history,
            {
                "role": "user",
                "content": current_message,
            },
        ],
        "context": {
            "current_message": current_message,
            "selected_history": history,
        },
        "trace": [],
    }


def test_extracts_financial_values_from_previous_user_message():
    state = _state(
        "Qual era meu saldo mensal?",
        [
            {
                "role": "user",
                "content": (
                    "Minha renda mensal é 5000 reais "
                    "e meus gastos são 3200 reais."
                ),
            }
        ],
    )

    memory = (
        extract_financial_memory_from_history(
            state
        )
    )

    serialized = str(memory)

    assert "5000" in serialized
    assert "3200" in serialized


def test_ignores_current_message_in_history():
    state = _state(
        "Minha renda mensal agora é 7000 reais.",
        [
            {
                "role": "user",
                "content": (
                    "Minha renda mensal era "
                    "5000 reais."
                ),
            }
        ],
    )

    memory = (
        extract_financial_memory_from_history(
            state
        )
    )

    assert "7000" not in str(memory)


def test_assistant_messages_are_not_financial_memory_sources():
    state = _state(
        "Qual era meu saldo mensal?",
        [
            {
                "role": "assistant",
                "content": (
                    "Sua renda é 999999 reais "
                    "e seus gastos são 1 real."
                ),
            }
        ],
    )

    memory = (
        extract_financial_memory_from_history(
            state
        )
    )

    assert memory == {}


def test_detects_contextual_balance_follow_up():
    assert is_simple_balance_follow_up(
        "Com base no que informei antes, "
        "qual era meu saldo mensal?"
    )


def test_does_not_intercept_new_complete_diagnosis():
    assert not is_simple_balance_follow_up(
        "Minha renda é 5000 e meus gastos "
        "fixos são 2000."
    )


def test_resolves_simple_balance_without_full_diagnosis():
    state = _state(
        (
            "Com base no que informei antes, "
            "qual era meu saldo mensal?"
        ),
        [
            {
                "role": "user",
                "content": (
                    "Minha renda mensal é 5000 reais "
                    "e meus gastos são 3200 reais."
                ),
            }
        ],
    )

    result = resolve_simple_balance_follow_up(
        state
    )

    assert result is not None
    assert result["current_agent"] == "financial_agent"
    assert result["semantic_memory_used"] is True
    assert result["semantic_memory_operation"] == (
        "simple_balance"
    )

    response = result["response"]

    assert "R$ 5.000,00" in response
    assert "R$ 3.200,00" in response
    assert "R$ 1.800,00" in response
    assert "não recalcula score" in response


def test_returns_none_when_history_has_no_income():
    state = _state(
        (
            "Com base no que informei antes, "
            "qual era meu saldo mensal?"
        ),
        [
            {
                "role": "user",
                "content": (
                    "Meus gastos eram 3200 reais."
                ),
            }
        ],
    )

    assert (
        resolve_simple_balance_follow_up(
            state
        )
        is None
    )


def test_current_explicit_values_keep_priority_over_history():
    state = _state(
        (
            "Renda mensal: 7000; "
            "gastos fixos: 2000; "
            "gastos variáveis: 1000."
        ),
        [
            {
                "role": "user",
                "content": (
                    "Minha renda mensal era 5000; "
                    "gastos fixos: 1500; "
                    "gastos variáveis: 500."
                ),
            }
        ],
    )

    resolution = resolver_entrada_financeira(
        state
    )

    assert resolution.ready is True
    assert resolution.arguments is not None

    assert (
        resolution.arguments["renda_mensal"]
        == 7000
    )

    assert (
        resolution.arguments["gastos_fixos"]
        == 2000
    )

    assert (
        resolution.arguments["gastos_variaveis"]
        == 1000
    )


def test_aggregate_history_does_not_invent_expense_split():
    state = _state(
        "Faça meu diagnóstico financeiro.",
        [
            {
                "role": "user",
                "content": (
                    "Minha renda mensal é 5000 reais "
                    "e meus gastos são 3200 reais."
                ),
            }
        ],
    )

    resolution = resolver_entrada_financeira(
        state
    )

    assert resolution.ready is False

    assert (
        "gastos_fixos"
        in resolution.missing_fields
    )

    assert (
        "gastos_variaveis"
        in resolution.missing_fields
    )

    assert (
        "aggregate_expenses_not_split"
        in resolution.warnings
    )
