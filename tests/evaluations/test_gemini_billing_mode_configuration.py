from __future__ import annotations

from pathlib import Path

import pytest

from src.evaluation.gemini_cost_accounting import (
    DEFAULT_GEMINI_BILLING_MODE,
    GEMINI_BILLING_MODE_ENV,
    resolve_gemini_billing_mode,
)
from src.evaluation.live_payload_provider import (
    LiveInnaPayloadProvider,
)


def _case():
    from src.evaluation.case_catalog import (
        build_core_dataset,
    )

    return build_core_dataset().get_case(
        "rag-financial-education-001"
    )


def _state():
    return {
        "response": (
            "Uma reserva de emergência "
            "protege o planejamento."
        ),
        "structured_response": {
            "rag_execution": {
                "retrieved_documents": 1,
                "duration_ms": 10,
                "retrieval_context": [
                    "Reserva para imprevistos."
                ],
                "llm_usage": {
                    "input_tokens": 1000,
                    "output_tokens": 200,
                    "total_tokens": 1200,
                },
            }
        },
    }


def test_billing_defaults_to_free_tier(
    monkeypatch,
):
    monkeypatch.delenv(
        GEMINI_BILLING_MODE_ENV,
        raising=False,
    )

    assert (
        resolve_gemini_billing_mode()
        == DEFAULT_GEMINI_BILLING_MODE
        == "free_tier"
    )


def test_billing_reads_paid_standard_from_env(
    monkeypatch,
):
    monkeypatch.setenv(
        GEMINI_BILLING_MODE_ENV,
        "paid_standard",
    )

    assert (
        resolve_gemini_billing_mode()
        == "paid_standard"
    )


def test_billing_is_case_and_space_normalized(
    monkeypatch,
):
    monkeypatch.setenv(
        GEMINI_BILLING_MODE_ENV,
        "  PAID_STANDARD  ",
    )

    assert (
        resolve_gemini_billing_mode()
        == "paid_standard"
    )


def test_invalid_billing_mode_is_rejected(
    monkeypatch,
):
    monkeypatch.setenv(
        GEMINI_BILLING_MODE_ENV,
        "unknown_mode",
    )

    with pytest.raises(
        ValueError,
        match="INNA_GEMINI_BILLING_MODE",
    ):
        resolve_gemini_billing_mode()


def test_live_provider_uses_paid_mode(
    monkeypatch,
):
    monkeypatch.setenv(
        GEMINI_BILLING_MODE_ENV,
        "paid_standard",
    )

    state = _state()

    provider = LiveInnaPayloadProvider(
        graph_executor=(
            lambda **kwargs: state
        )
    )

    payload = provider(
        _case()
    )

    metadata = payload.metadata

    assert metadata[
        "billing_mode"
    ] == "paid_standard"

    assert metadata[
        "actual_billed_cost_usd"
    ] == pytest.approx(
        0.0008
    )

    assert metadata[
        "paid_equivalent_cost_usd"
    ] == pytest.approx(
        0.0008
    )

    assert metadata[
        "free_tier_savings_usd"
    ] == 0.0


def test_live_provider_uses_free_mode(
    monkeypatch,
):
    monkeypatch.setenv(
        GEMINI_BILLING_MODE_ENV,
        "free_tier",
    )

    state = _state()

    provider = LiveInnaPayloadProvider(
        graph_executor=(
            lambda **kwargs: state
        )
    )

    payload = provider(
        _case()
    )

    metadata = payload.metadata

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

    assert metadata[
        "free_tier_savings_usd"
    ] == pytest.approx(
        0.0008
    )


def test_runtime_sources_use_dynamic_billing():
    provider_source = Path(
        "src/evaluation/live_payload_provider.py"
    ).read_text(
        encoding="utf-8"
    )

    rag_source = Path(
        "src/rag_engine.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "resolve_gemini_billing_mode()"
        in provider_source
    )

    assert (
        "resolve_gemini_billing_mode()"
        in rag_source
    )

    assert (
        'billing_mode="free_tier"'
        not in provider_source
    )

    assert (
        '"billing_mode": "free_tier"'
        not in rag_source
    )
