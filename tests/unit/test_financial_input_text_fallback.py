from __future__ import annotations

import pytest

from src.agents.financial_input_resolver import (
    resolver_entrada_financeira,
)


def _resolve(message: str):
    return resolver_entrada_financeira(
        {
            "user_message": message,
            "language": "pt",
            "currency": "BRL",
            "context": {},
            "structured_response": {},
            "conversation_history": [],
        }
    )


def test_extracts_complete_natural_language_message():
    result = _resolve(
        (
            "Minha renda mensal é 5000 reais, "
            "meus gastos fixos são 2000 reais, "
            "meus gastos variáveis são 800 reais, "
            "minhas dívidas mensais são 300 reais "
            "e minha reserva atual é 1000 reais."
        )
    )

    assert result.ready is True
    assert result.missing_fields == []

    assert result.arguments is not None
    assert result.arguments["renda_mensal"] == 5000.0
    assert result.arguments["gastos_fixos"] == 2000.0
    assert result.arguments["gastos_variaveis"] == 800.0
    assert result.arguments["dividas_mensais"] == 300.0
    assert result.arguments["reserva_atual"] == 1000.0


def test_extracts_colon_separated_financial_values():
    result = _resolve(
        (
            "Renda: 5000; "
            "Gastos fixos: 2000; "
            "Gastos variáveis: 800; "
            "Dívidas: 300; "
            "Reserva: 1000."
        )
    )

    assert result.ready is True
    assert result.arguments is not None

    assert result.arguments == {
        "renda_mensal": 5000.0,
        "gastos_fixos": 2000.0,
        "gastos_variaveis": 800.0,
        "dividas_mensais": 300.0,
        "reserva_atual": 1000.0,
        "gastos_incluem_dividas": False,
        "moeda": "BRL",
        "idioma": "pt",
    }


def test_extracts_brazilian_currency_format():
    result = _resolve(
        (
            "Renda mensal: R$ 5.000,00; "
            "despesas fixas: R$ 2.000,00; "
            "despesas variáveis: R$ 800,00; "
            "parcelas mensais: R$ 300,00; "
            "reserva atual: R$ 1.000,00."
        )
    )

    assert result.ready is True
    assert result.arguments is not None

    assert result.arguments["renda_mensal"] == 5000.0
    assert result.arguments["gastos_fixos"] == 2000.0
    assert result.arguments["gastos_variaveis"] == 800.0
    assert result.arguments["dividas_mensais"] == 300.0
    assert result.arguments["reserva_atual"] == 1000.0


def test_incomplete_message_remains_incomplete():
    result = _resolve("Minha renda mensal é 5000 reais.")

    assert result.ready is False

    assert set(result.missing_fields) == {
        "gastos_fixos",
        "gastos_variaveis",
        "dividas_mensais",
        "reserva_atual",
    }


def test_field_sources_identify_deterministic_fallback():
    result = _resolve(
        (
            "Renda: 5000; "
            "Gastos fixos: 2000; "
            "Gastos variáveis: 800; "
            "Dívidas: 300; "
            "Reserva: 1000."
        )
    )

    assert result.ready is True

    for field in (
        "renda_mensal",
        "gastos_fixos",
        "gastos_variaveis",
        "dividas_mensais",
        "reserva_atual",
    ):
        assert result.field_sources[field] in {
            "current_message_parser",
            "current_message_extractor",
            ("current_message_deterministic_fallback"),
        }


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        (
            "Dívidas mensais são 0 reais.",
            0.0,
        ),
        (
            "Parcelas: 250.",
            250.0,
        ),
        (
            "Minha reserva está em 1500 reais.",
            1500.0,
        ),
    ],
)
def test_individual_field_variations(
    message: str,
    expected: float,
):
    result = _resolve(message)

    collected = result.collected_data

    if "dívida" in message.lower() or "parcela" in message.lower():
        assert collected["dividas_mensais"] == expected
    else:
        assert collected["reserva_atual"] == expected


def test_fallback_repairs_invalid_zero_from_parser(
    monkeypatch,
):
    monkeypatch.setattr(
        ("src.agents.financial_input_resolver.parse_financial_message"),
        lambda message: {
            "renda_mensal": 5000.0,
            "gastos_fixos": 0.0,
            "gastos_variaveis": 800.0,
            "dividas_mensais": 300.0,
            "reserva_atual": 1000.0,
        },
    )

    result = _resolve(
        (
            "Renda mensal: R$ 5.000,00; "
            "despesas fixas: R$ 2.000,00; "
            "despesas variáveis: R$ 800,00; "
            "parcelas mensais: R$ 300,00; "
            "reserva atual: R$ 1.000,00."
        )
    )

    assert result.ready is True
    assert result.arguments is not None

    assert result.arguments["gastos_fixos"] == 2000.0

    assert result.field_sources["gastos_fixos"] == (
        "current_message_deterministic_fallback"
    )

    assert "message_parser_values_repaired_by_fallback" in result.warnings


def test_explicit_zero_is_not_replaced():
    result = _resolve(
        (
            "Renda: 5000; "
            "Gastos fixos: 0; "
            "Gastos variáveis: 800; "
            "Dívidas: 300; "
            "Reserva: 1000."
        )
    )

    assert result.ready is True
    assert result.arguments is not None
    assert result.arguments["gastos_fixos"] == 0.0
