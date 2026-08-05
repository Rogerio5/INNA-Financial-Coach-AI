from types import SimpleNamespace

import pytest

from src.evaluation.rag_lab_experiment_metadata import (
    EXPERIMENT_METADATA_FIELDS,
    MetadataAvailability,
    build_experiment_metadata_readiness,
    build_experiment_metadata_snapshot,
    extract_experiment_metadata,
    get_available_metadata_filter_values,
)


def _history(*entries):
    return SimpleNamespace(
        entries=entries,
    )


def test_defines_expected_professional_fields():
    field_keys = {field.key for field in EXPERIMENT_METADATA_FIELDS}

    assert {
        "retrieval_strategy",
        "reranker_enabled",
        "top_k",
        "model_name",
        "prompt_version",
        "embedding_model",
        "knowledge_base_version",
        "chunk_size",
        "chunk_overlap",
        "latency_ms",
        "input_tokens",
        "output_tokens",
        "estimated_cost_usd",
    }.issubset(field_keys)


def test_extracts_direct_attributes_first():
    entry = SimpleNamespace(
        model_name="gemini-example",
        top_k=5,
        metadata={
            "model_name": "outro-modelo",
            "top_k": 10,
        },
    )

    metadata = extract_experiment_metadata(entry)

    assert metadata["model_name"] == ("gemini-example")
    assert metadata["top_k"] == 5


def test_extracts_top_level_metadata():
    entry = SimpleNamespace(
        metadata={
            "retrieval_strategy": "hybrid",
            "reranker_enabled": True,
            "top_k": 5,
        }
    )

    metadata = extract_experiment_metadata(entry)

    assert metadata == {
        "retrieval_strategy": "hybrid",
        "reranker_enabled": True,
        "top_k": 5,
    }


def test_extracts_nested_rag_metadata():
    entry = SimpleNamespace(
        metadata={
            "rag": {
                "embedding_model": ("embedding-example"),
                "knowledge_base_version": "kb-v2",
                "chunk_size": 650,
            }
        }
    )

    metadata = extract_experiment_metadata(entry)

    assert metadata["embedding_model"] == "embedding-example"

    assert metadata["knowledge_base_version"] == "kb-v2"

    assert metadata["chunk_size"] == 650


def test_empty_snapshot_uses_honest_empty_state():
    entry = SimpleNamespace()

    snapshot = build_experiment_metadata_snapshot(entry)

    assert len(snapshot) == len(EXPERIMENT_METADATA_FIELDS)

    assert all(item.available is False for item in snapshot)

    assert all(
        item.display_value == "Não registrado nesta execução" for item in snapshot
    )


def test_snapshot_formats_boolean_latency_and_cost():
    entry = SimpleNamespace(
        metadata={
            "reranker_enabled": True,
            "latency_ms": 1250.25,
            "estimated_cost_usd": 0.001234,
        }
    )

    snapshot = {item.key: item for item in (build_experiment_metadata_snapshot(entry))}

    assert snapshot["reranker_enabled"].display_value == "Habilitado"

    assert "1,250.25 ms" in snapshot["latency_ms"].display_value

    assert snapshot["estimated_cost_usd"].display_value == "US$ 0.001234"


def test_readiness_is_unavailable_without_metadata():
    readiness = {
        item.key: item
        for item in (
            build_experiment_metadata_readiness(
                _history(
                    SimpleNamespace(),
                    SimpleNamespace(),
                )
            )
        )
    }

    model = readiness["model_name"]

    assert model.availability == MetadataAvailability.UNAVAILABLE
    assert model.available_runs == 0
    assert model.total_runs == 2
    assert model.coverage_rate == 0.0


def test_readiness_is_partial_when_some_runs_have_value():
    readiness = {
        item.key: item
        for item in (
            build_experiment_metadata_readiness(
                _history(
                    SimpleNamespace(metadata={"model_name": ("gemini-example")}),
                    SimpleNamespace(),
                )
            )
        )
    }

    model = readiness["model_name"]

    assert model.availability == MetadataAvailability.PARTIAL
    assert model.available_runs == 1
    assert model.total_runs == 2
    assert model.coverage_rate == pytest.approx(0.5)


def test_readiness_is_available_for_all_runs():
    readiness = {
        item.key: item
        for item in (
            build_experiment_metadata_readiness(
                _history(
                    SimpleNamespace(metadata={"retrieval_strategy": ("hybrid")}),
                    SimpleNamespace(metadata={"retrieval_strategy": ("vector")}),
                )
            )
        )
    }

    strategy = readiness["retrieval_strategy"]

    assert strategy.availability == MetadataAvailability.AVAILABLE
    assert strategy.available_runs == 2
    assert strategy.coverage_rate == 1.0
    assert strategy.distinct_values == (
        "hybrid",
        "vector",
    )


def test_available_filter_values_are_real_only():
    history = _history(
        SimpleNamespace(metadata={"retrieval_strategy": "hybrid"}),
        SimpleNamespace(metadata={"retrieval_strategy": "vector"}),
        SimpleNamespace(),
        SimpleNamespace(metadata={"retrieval_strategy": "hybrid"}),
    )

    values = get_available_metadata_filter_values(
        history,
        "retrieval_strategy",
    )

    assert values == (
        "hybrid",
        "vector",
    )


def test_unknown_filter_field_is_rejected():
    with pytest.raises(
        KeyError,
        match="desconhecido",
    ):
        get_available_metadata_filter_values(
            _history(),
            "campo_inexistente",
        )


def test_empty_history_is_supported():
    readiness = build_experiment_metadata_readiness(_history())

    assert all(item.total_runs == 0 for item in readiness)

    assert all(
        item.availability == MetadataAvailability.UNAVAILABLE for item in readiness
    )
