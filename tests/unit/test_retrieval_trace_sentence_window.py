from src.services.rag.retrieval_trace import (
    build_result_traces,
)


def test_retrieval_trace_preserves_sentence_window_metadata():
    results = [
        {
            "chunk_id": 114,
            "documento_key": "inna-edu-orcamento-002",
            "titulo": "Orçamento",
            "fonte": "knowledge_base",
            "score": 0.67,
            "score_hibrido": 1.2,
            "score_rerank": 1.7,
            "sentence_window_applied": True,
            "sentence_window_policy": "selective_allowlist",
            "sentence_window_document_key": (
                "inna-edu-orcamento-002"
            ),
        }
    ]

    traces = build_result_traces(results)

    assert len(traces) == 1

    payload = traces[0].to_dict()

    assert payload["document_key"] == (
        "inna-edu-orcamento-002"
    )
    assert payload["sentence_window_applied"] is True
    assert payload["sentence_window_policy"] == (
        "selective_allowlist"
    )
    assert payload[
        "sentence_window_document_key"
    ] == "inna-edu-orcamento-002"


def test_retrieval_trace_keeps_metadata_optional():
    traces = build_result_traces(
        [
            {
                "chunk_id": 113,
                "titulo": "Orçamento",
            }
        ]
    )

    payload = traces[0].to_dict()

    assert payload["document_key"] is None
    assert payload["sentence_window_applied"] is None
    assert payload["sentence_window_policy"] is None
    assert payload[
        "sentence_window_document_key"
    ] is None


def test_retrieval_trace_normalizes_boolean_metadata():
    traces = build_result_traces(
        [
            {
                "chunk_id": 115,
                "document_key": "inna-edu-orcamento-002",
                "sentence_window_applied": "true",
            }
        ]
    )

    payload = traces[0].to_dict()

    assert payload["sentence_window_applied"] is True
