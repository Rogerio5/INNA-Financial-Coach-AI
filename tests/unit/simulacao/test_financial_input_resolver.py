from __future__ import annotations

from unittest.mock import patch

from src.agents.financial_input_resolver import (
    resolver_entrada_financeira,
)


def _complete_data(
    **overrides,
) -> dict:
    values = {
        "renda_mensal": 4000,
        "gastos_fixos": 1800,
        "gastos_variaveis": 700,
        "dividas_mensais": 300,
        "reserva_atual": 1000,
    }

    values.update(overrides)

    return values


def test_resolves_explicit_structured_data():
    result = resolver_entrada_financeira({
        "financial_inputs": (
            _complete_data()
        ),
        "language": "pt",
        "currency": "BRL",
    })

    assert result.ready is True

    assert result.arguments == {
        **_complete_data(),
        "gastos_incluem_dividas": False,
        "moeda": "BRL",
        "idioma": "pt",
    }


def test_current_message_overrides_memory():
    memory = {
        "renda_mensal": 3000,
        "gastos_mensais": 2000,
        "valor_reserva": 100,
    }

    parsed = _complete_data(
        renda_mensal=4500,
    )

    with (
        patch(
            "src.agents.financial_input_resolver."
            "extrair_memoria_da_mensagem_inna",
            return_value={
                "dados": {},
            },
        ),
        patch(
            "src.agents.financial_input_resolver."
            "parse_financial_message",
            return_value=parsed,
        ),
    ):
        result = resolver_entrada_financeira({
            "user_message": (
                "Renda: 4500; Gastos fixos: "
                "1800; Gastos variáveis: 700; "
                "Dívidas: 300; Reserva: 1000"
            ),
            "memory": memory,
        })

    assert result.ready is True
    assert (
        result.arguments["renda_mensal"]
        == 4500
    )

    assert (
        result.field_sources["renda_mensal"]
        == "current_message_parser"
    )


def test_memory_can_fill_missing_current_data():
    memory = _complete_data(
        reserva_atual=2500,
    )

    with (
        patch(
            "src.agents.financial_input_resolver."
            "extrair_memoria_da_mensagem_inna",
            return_value={},
        ),
        patch(
            "src.agents.financial_input_resolver."
            "parse_financial_message",
            return_value={},
        ),
    ):
        result = resolver_entrada_financeira({
            "user_message": (
                "Quero analisar minhas finanças"
            ),
            "memory": memory,
        })

    assert result.ready is True

    assert (
        result.arguments["reserva_atual"]
        == 2500
    )


def test_does_not_split_aggregate_expenses():
    with (
        patch(
            "src.agents.financial_input_resolver."
            "extrair_memoria_da_mensagem_inna",
            return_value={
                "dados": {
                    "renda_mensal": 4000,
                    "gastos_mensais": 2500,
                    "valor_reserva": 1000,
                    "possui_dividas": False,
                }
            },
        ),
        patch(
            "src.agents.financial_input_resolver."
            "parse_financial_message",
            return_value={},
        ),
    ):
        result = resolver_entrada_financeira({
            "user_message": (
                "Minha renda é 4000 e gasto "
                "2500 por mês"
            ),
        })

    assert result.ready is False

    assert "gastos_fixos" in (
        result.missing_fields
    )

    assert "gastos_variaveis" in (
        result.missing_fields
    )

    assert (
        "aggregate_expenses_not_split"
        in result.warnings
    )


def test_explicit_no_debt_becomes_zero():
    data = {
        "renda_mensal": 4000,
        "gastos_fixos": 1800,
        "gastos_variaveis": 700,
        "reserva_atual": 1000,
        "possui_dividas": False,
    }

    result = resolver_entrada_financeira({
        "financial_inputs": data,
    })

    assert result.ready is True

    assert (
        result.arguments["dividas_mensais"]
        == 0.0
    )


def test_missing_fields_generate_clarification():
    with (
        patch(
            "src.agents.financial_input_resolver."
            "extrair_memoria_da_mensagem_inna",
            return_value={},
        ),
        patch(
            "src.agents.financial_input_resolver."
            "parse_financial_message",
            return_value={
                "renda_mensal": 3000,
            },
        ),
    ):
        result = resolver_entrada_financeira({
            "user_message": "Renda: 3000",
        })

    assert result.ready is False

    assert "gastos_fixos" in (
        result.missing_fields
    )

    assert (
        result.clarification_message
        is not None
    )

    assert "Gastos fixos" in (
        result.clarification_message
    )


def test_invalid_negative_value_is_not_accepted():
    result = resolver_entrada_financeira({
        "financial_inputs": (
            _complete_data(
                renda_mensal=-100,
            )
        ),
    })

    assert result.ready is False

    assert "renda_mensal" in (
        result.missing_fields
    )

    assert any(
        warning.startswith(
            "invalid_value:renda_mensal"
        )
        for warning in result.warnings
    )
