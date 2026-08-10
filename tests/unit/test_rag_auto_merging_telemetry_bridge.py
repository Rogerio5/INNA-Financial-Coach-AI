from src.agent_tools.rag_tools import (
    _extract_retrieval_telemetry,
)
from src.evaluation.live_payload_provider import (
    _retrieval_telemetry_metadata,
)
from src.rag_engine import (
    _build_auto_merging_trace_summary,
)


def test_auto_merging_trace_summary_when_applied() -> None:
    summary = _build_auto_merging_trace_summary(
        [
            {
                "auto_merging_applied": True,
                "auto_merging_child_count": 2,
            },
            {
                "auto_merging_applied": False,
                "auto_merging_child_count": 0,
            },
        ],
        {
            "auto_merging_ms": 0.14,
        },
    )

    assert summary == {
        "observed": True,
        "applied": True,
        "merged_result_count": 1,
        "child_count": 2,
        "duration_ms": 0.14,
    }


def test_auto_merging_trace_summary_when_disabled() -> None:
    summary = _build_auto_merging_trace_summary(
        [
            {
                "score": 1.0,
            },
        ],
        {
            "auto_merging_ms": 0.0,
        },
    )

    assert summary == {
        "observed": False,
        "applied": False,
        "merged_result_count": 0,
        "child_count": 0,
        "duration_ms": 0.0,
    }


def test_formal_tool_exposes_only_safe_retrieval_telemetry() -> None:
    telemetry = _extract_retrieval_telemetry(
        {
            "retrieval_trace": {
                "query": "conteudo interno",
                "results": [
                    {
                        "chunk_text": (
                            "texto que não deve "
                            "ser propagado"
                        ),
                    }
                ],
                "auto_merging": {
                    "observed": True,
                    "applied": True,
                    "merged_result_count": 1,
                    "child_count": 2,
                    "duration_ms": 0.19,
                },
            },
            "sql": "não expor",
        }
    )

    assert telemetry == {
        "observed": True,
        "applied": True,
        "merged_result_count": 1,
        "child_count": 2,
        "duration_ms": 0.19,
    }

    assert "query" not in telemetry
    assert "results" not in telemetry
    assert "sql" not in telemetry


def test_live_provider_flattens_safe_auto_merging_metadata() -> None:
    metadata = _retrieval_telemetry_metadata(
        {
            "structured_response": {
                "rag_execution": {
                    "retrieval_telemetry": {
                        "observed": True,
                        "applied": True,
                        "merged_result_count": 1,
                        "child_count": 2,
                        "duration_ms": 0.21,
                    }
                }
            }
        }
    )

    assert metadata == {
        "auto_merging_observed": True,
        "auto_merging_applied": True,
        "auto_merging_merged_result_count": 1,
        "auto_merging_child_count": 2,
        "auto_merging_ms": 0.21,
    }
