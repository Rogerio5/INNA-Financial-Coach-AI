from __future__ import annotations

from typing import Any

import pytest

from src.evaluation.case_catalog import (
    build_core_dataset,
)
from src.evaluation.live_payload_provider import (
    LiveInnaPayloadProvider,
)


def _rag_case():
    return build_core_dataset().get_case(
        "rag-financial-education-001"
    )


def _state_with_usage(
    usage: dict[str, Any],
) -> dict[str, Any]:
    return {
        "response": (
            "Uma reserva de emergência "
            "ajuda a lidar com imprevistos "
            "sem comprometer o planejamento."
        ),
        "structured_response": {
            "rag_execution": {
                "retrieved_documents": 1,
                "duration_ms": 12.5,
                "retrieval_context": [
                    (
                        "A reserva financeira "
                        "protege contra "
                        "imprevistos."
                    )
                ],
                "llm_usage": usage,
            }
        },
    }


def test_live_provider_exposes_free_tier_accounting():
    state = _state_with_usage({
        "input_tokens": 120,
        "output_tokens": 30,
        "total_tokens": 150,
    })

    provider = LiveInnaPayloadProvider(
        graph_executor=(
            lambda **kwargs: state
        )
    )

    payload = provider(
        _rag_case()
    )

    metadata = payload.metadata

    assert metadata[
        "input_tokens"
    ] == 120

    assert metadata[
        "output_tokens"
    ] == 30

    assert metadata[
        "total_tokens"
    ] == 150

    assert metadata[
        "generation_model"
    ] == "gemini-3.5-flash-lite"

    assert metadata[
        "billing_mode"
    ] == "free_tier"

    assert metadata[
        "actual_billed_cost_usd"
    ] == 0.0

    assert metadata[
        "paid_equivalent_cost_usd"
    ] == pytest.approx(
        0.000111
    )

    assert metadata[
        "free_tier_savings_usd"
    ] == pytest.approx(
        0.000111
    )

    assert metadata[
        "paid_input_rate_per_1m_usd"
    ] == 0.30

    assert metadata[
        "paid_output_rate_per_1m_usd"
    ] == 2.50

    assert metadata[
        "pricing_snapshot_date"
    ] == "2026-08-09"

    assert metadata[
        "token_usage_observed"
    ] is True


def test_live_provider_handles_missing_usage_safely():
    state = _state_with_usage({})

    provider = LiveInnaPayloadProvider(
        graph_executor=(
            lambda **kwargs: state
        )
    )

    payload = provider(
        _rag_case()
    )

    metadata = payload.metadata

    assert metadata[
        "input_tokens"
    ] == 0

    assert metadata[
        "output_tokens"
    ] == 0

    assert metadata[
        "total_tokens"
    ] == 0

    assert metadata[
        "actual_billed_cost_usd"
    ] == 0.0

    assert metadata[
        "paid_equivalent_cost_usd"
    ] == 0.0

    assert metadata[
        "free_tier_savings_usd"
    ] == 0.0

    assert metadata[
        "token_usage_observed"
    ] is False


def test_live_provider_normalizes_invalid_usage():
    state = _state_with_usage({
        "input_tokens": "invalid",
        "output_tokens": -50,
        "total_tokens": None,
    })

    provider = LiveInnaPayloadProvider(
        graph_executor=(
            lambda **kwargs: state
        )
    )

    payload = provider(
        _rag_case()
    )

    metadata = payload.metadata

    assert metadata[
        "input_tokens"
    ] == 0

    assert metadata[
        "output_tokens"
    ] == 0

    assert metadata[
        "total_tokens"
    ] == 0

    assert metadata[
        "paid_equivalent_cost_usd"
    ] == 0.0


def test_observed_accounting_cannot_be_overridden():
    state = _state_with_usage({
        "input_tokens": 1000,
        "output_tokens": 200,
        "total_tokens": 1200,
    })

    provider = LiveInnaPayloadProvider(
        graph_executor=(
            lambda **kwargs: state
        ),
        metadata={
            "input_tokens": 999999,
            "billing_mode": "paid_standard",
            "actual_billed_cost_usd": 999.0,
            "paid_equivalent_cost_usd": 999.0,
        },
    )

    payload = provider(
        _rag_case()
    )

    metadata = payload.metadata

    assert metadata[
        "input_tokens"
    ] == 1000

    assert metadata[
        "output_tokens"
    ] == 200

    assert metadata[
        "billing_mode"
    ] == "free_tier"

    assert metadata[
        "actual_billed_cost_usd"
    ] == 0.0

    assert metadata[
        "paid_equivalent_cost_usd"
    ] == pytest.approx(
        0.0008
    )


def test_deepeval_reservation_cost_remains_separate():
    state = _state_with_usage({
        "input_tokens": 1000,
        "output_tokens": 200,
        "total_tokens": 1200,
    })

    provider = LiveInnaPayloadProvider(
        graph_executor=(
            lambda **kwargs: state
        ),
        estimated_cost=0.05,
    )

    payload = provider(
        _rag_case()
    )

    metadata = payload.metadata

    assert metadata[
        "estimated_cost"
    ] == 0.05

    assert metadata[
        "actual_billed_cost_usd"
    ] == 0.0

    assert metadata[
        "paid_equivalent_cost_usd"
    ] == pytest.approx(
        0.0008
    )
