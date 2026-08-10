from __future__ import annotations

import pytest

from src.evaluation.gemini_cost_accounting import (
    GEMINI_35_FLASH_LITE_MODEL,
    calculate_gemini_35_flash_lite_cost,
)


def test_free_tier_has_zero_actual_cost() -> None:
    result = calculate_gemini_35_flash_lite_cost(
        input_tokens=1_000_000,
        output_tokens=1_000_000,
        billing_mode="free_tier",
    )

    assert (
        result.model_name
        == GEMINI_35_FLASH_LITE_MODEL
    )

    assert result.total_tokens == 2_000_000

    assert (
        result.actual_billed_cost_usd
        == pytest.approx(0.0)
    )

    assert (
        result.paid_equivalent_cost_usd
        == pytest.approx(2.80)
    )

    assert (
        result.free_tier_savings_usd
        == pytest.approx(2.80)
    )


def test_paid_standard_uses_equivalent_cost() -> None:
    result = calculate_gemini_35_flash_lite_cost(
        input_tokens=1_000_000,
        output_tokens=1_000_000,
        billing_mode="paid_standard",
    )

    assert (
        result.actual_billed_cost_usd
        == pytest.approx(2.80)
    )

    assert (
        result.paid_equivalent_cost_usd
        == pytest.approx(2.80)
    )

    assert (
        result.free_tier_savings_usd
        == pytest.approx(0.0)
    )


def test_small_usage_cost_is_precise() -> None:
    result = calculate_gemini_35_flash_lite_cost(
        input_tokens=1_000,
        output_tokens=200,
    )

    # 1000 input:
    # 1000 / 1M * 0.30 = 0.0003
    #
    # 200 output:
    # 200 / 1M * 2.50 = 0.0005
    #
    # total = 0.0008

    assert (
        result.paid_equivalent_cost_usd
        == pytest.approx(0.0008)
    )

    assert (
        result.actual_billed_cost_usd
        == pytest.approx(0.0)
    )


@pytest.mark.parametrize(
    "field,value",
    (
        ("input_tokens", -1),
        ("output_tokens", -1),
    ),
)
def test_negative_tokens_are_rejected(
    field: str,
    value: int,
) -> None:
    kwargs = {
        "input_tokens": 0,
        "output_tokens": 0,
    }

    kwargs[field] = value

    with pytest.raises(
        ValueError,
        match="não pode ser negativo",
    ):
        calculate_gemini_35_flash_lite_cost(
            **kwargs
        )


def test_invalid_billing_mode_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="billing_mode inválido",
    ):
        calculate_gemini_35_flash_lite_cost(
            input_tokens=100,
            output_tokens=100,
            billing_mode="invalid",  # type: ignore[arg-type]
        )
