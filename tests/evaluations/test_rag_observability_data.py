import pandas as pd
import pytest

from src.evaluation.rag_observability_data import (
    EXPECTED_RAG_LOG_COLUMNS,
    build_field_coverage,
    build_latest_questions,
    build_mode_distribution,
    build_rag_observability_summary,
    export_rag_observability_csv,
)


def test_empty_summary_has_no_simulated_metrics():
    summary = build_rag_observability_summary(pd.DataFrame())

    assert summary.has_data is False
    assert summary.total_questions == 0
    assert summary.gemini_count is None
    assert summary.security_count is None
    assert summary.fallback_count is None
    assert summary.average_latency_ms is None
    assert summary.maximum_latency_ms is None


def test_summary_uses_real_values():
    frame = pd.DataFrame(
        {
            "pergunta": ["a", "b", "c"],
            "gemini": [True, False, "sim"],
            "seguranca": [1, 0, 1],
            "fallback": ["no", "yes", "false"],
            "tempo_ms": [100, 200, 300],
        }
    )

    summary = build_rag_observability_summary(frame)

    assert summary.has_data is True
    assert summary.total_questions == 3
    assert summary.gemini_count == 2
    assert summary.security_count == 2
    assert summary.fallback_count == 1
    assert summary.average_latency_ms == pytest.approx(200.0)
    assert summary.maximum_latency_ms == pytest.approx(300.0)


def test_mode_distribution_is_real_only():
    frame = pd.DataFrame(
        {
            "modo": [
                "hybrid",
                "hybrid",
                "security",
                None,
            ]
        }
    )

    result = build_mode_distribution(frame)

    assert result.iloc[0]["mode"] == "hybrid"
    assert result.iloc[0]["total"] == 2
    assert set(result["mode"]) == {
        "hybrid",
        "security",
        "unregistered",
    }


def test_latest_questions_uses_real_date_order():
    frame = pd.DataFrame(
        {
            "pergunta": ["old", "new"],
            "data_hora": [
                "2026-01-01T00:00:00Z",
                "2026-02-01T00:00:00Z",
            ],
        }
    )

    result = build_latest_questions(
        frame,
        limit=1,
    )

    assert result.iloc[0]["pergunta"] == "new"


def test_export_preserves_real_rows():
    frame = pd.DataFrame(
        {
            "pergunta": ["real"],
            "modo": ["hybrid"],
        }
    )

    csv_text = export_rag_observability_csv(frame)

    assert "real" in csv_text
    assert "hybrid" in csv_text


def test_field_coverage_includes_expected_contract():
    frame = pd.DataFrame(
        {
            "pergunta": ["a", None],
            "modo": ["hybrid", "vector"],
        }
    )

    rows = build_field_coverage(frame)

    assert len(rows) == len(EXPECTED_RAG_LOG_COLUMNS)

    by_field = {item["field"]: item for item in rows}

    assert by_field["pergunta"]["coverage_rate"] == pytest.approx(0.5)

    assert by_field["modo"]["coverage_rate"] == pytest.approx(1.0)

    assert by_field["tempo_ms"]["available"] is False
