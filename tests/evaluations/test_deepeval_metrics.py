from __future__ import annotations

from typing import Any

import pytest

from src.evaluation.case_catalog import (
    build_conversation_dataset,
    build_core_dataset,
)
from src.evaluation.deepeval_integration import (
    DeepEvalCasePayload,
)
from src.evaluation.deepeval_metrics import (
    MetricDefinition,
    MetricExecutionMode,
    MetricInputField,
    MetricInputValidationError,
    MetricKind,
    MetricNotFoundError,
    MetricProfile,
    MetricProfileNotFoundError,
    MetricRegistry,
    MetricRegistryError,
    build_default_metric_registry,
    build_default_metrics,
    build_default_profiles,
    required_payload_fields_missing,
)


def build_payload(
    *,
    expected_output: str | None = None,
    context: tuple[str, ...] = (),
    retrieval_context: tuple[str, ...] = (),
    metadata: dict[str, Any] | None = None,
) -> DeepEvalCasePayload:
    return DeepEvalCasePayload(
        case_id="metric-case",
        input_text="Entrada sintética.",
        actual_output="Resposta sintética.",
        expected_output=expected_output,
        context=context,
        retrieval_context=retrieval_context,
        metadata=metadata or {
            "execution_id": "run-001",
        },
    )


def test_default_metrics_are_unique() -> None:
    metrics = build_default_metrics()

    metric_ids = tuple(
        metric.metric_id
        for metric in metrics
    )

    assert len(metric_ids) == len(
        set(metric_ids)
    )


def test_default_profiles_are_unique() -> None:
    profiles = build_default_profiles()

    profile_ids = tuple(
        profile.profile_id
        for profile in profiles
    )

    categories = tuple(
        profile.category
        for profile in profiles
    )

    assert len(profile_ids) == len(
        set(profile_ids)
    )

    assert len(categories) == len(
        set(categories)
    )


def test_default_registry() -> None:
    registry = build_default_metric_registry()

    assert len(registry) == len(
        build_default_metrics()
    )

    assert registry.all_profiles()
    assert registry.local_metrics()
    assert registry.live_metrics()


def test_metric_definition_normalizes_values() -> None:
    metric = MetricDefinition(
        metric_id="  custom-metric  ",
        display_name=" Custom Metric ",
        description=" Description ",
        kind=MetricKind.DETERMINISTIC,
        execution_mode=MetricExecutionMode.LOCAL,
        categories=(
            " RAG ",
            "rag",
        ),
    )

    assert metric.metric_id == "custom-metric"
    assert metric.display_name == "Custom Metric"
    assert metric.description == "Description"
    assert metric.categories == ("rag",)


@pytest.mark.parametrize(
    ("raw_metric_id", "normalized_metric_id"),
    (
        (
            "Metric",
            "metric",
        ),
        (
            "ANSWER-RELEVANCY",
            "answer-relevancy",
        ),
        (
            "  Financial-Safety  ",
            "financial-safety",
        ),
    ),
)
def test_metric_id_is_normalized(
    raw_metric_id: str,
    normalized_metric_id: str,
) -> None:
    metric = MetricDefinition(
        metric_id=raw_metric_id,
        display_name="Normalized Metric",
        description=(
            "Valida a normalização canônica do ID."
        ),
        kind=MetricKind.DETERMINISTIC,
        execution_mode=MetricExecutionMode.LOCAL,
    )

    assert metric.metric_id == normalized_metric_id



@pytest.mark.parametrize(
    "invalid_metric_id",
    (
        "",
        "metric_name",
        "metric name",
        "-metric",
        "metric-",
        "metric--name",
        "1metric",
        "@metric",
    ),
)
def test_metric_rejects_invalid_id(
    invalid_metric_id: str,
) -> None:
    with pytest.raises(ValueError):
        MetricDefinition(
            metric_id=invalid_metric_id,
            display_name="Metric",
            description="Description",
            kind=MetricKind.DETERMINISTIC,
            execution_mode=(
                MetricExecutionMode.LOCAL
            ),
        )


@pytest.mark.parametrize(
    "threshold",
    (
        -0.1,
        1.1,
        2.0,
    ),
)
def test_metric_rejects_invalid_threshold(
    threshold: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="threshold",
    ):
        MetricDefinition(
            metric_id="invalid-threshold",
            display_name="Metric",
            description="Description",
            kind=MetricKind.DETERMINISTIC,
            execution_mode=(
                MetricExecutionMode.LOCAL
            ),
            threshold=threshold,
        )


def test_geval_requires_criteria() -> None:
    with pytest.raises(
        ValueError,
        match="criteria",
    ):
        MetricDefinition(
            metric_id="missing-criteria",
            display_name="Metric",
            description="Description",
            kind=MetricKind.GEVAL,
            execution_mode=(
                MetricExecutionMode.LIVE_OPT_IN
            ),
            deepeval_class_name="GEval",
        )


def test_deepeval_metric_requires_class_name() -> None:
    with pytest.raises(
        ValueError,
        match="deepeval_class_name",
    ):
        MetricDefinition(
            metric_id="missing-class",
            display_name="Metric",
            description="Description",
            kind=MetricKind.DEEPEVAL,
            execution_mode=(
                MetricExecutionMode.LIVE_OPT_IN
            ),
        )


def test_local_metric_properties() -> None:
    metric = build_default_metric_registry().get(
        "expected-terms"
    )

    assert metric.is_local is True
    assert metric.is_live is False
    assert metric.is_llm_judge is False


def test_live_metric_properties() -> None:
    metric = build_default_metric_registry().get(
        "answer-relevancy"
    )

    assert metric.is_live is True
    assert metric.is_local is False
    assert metric.is_llm_judge is True


def test_metric_supports_category() -> None:
    registry = build_default_metric_registry()

    faithfulness = registry.get(
        "faithfulness"
    )

    assert faithfulness.supports_category("rag")
    assert faithfulness.supports_category(
        "EMERGENCY-FUND"
    )
    assert not faithfulness.supports_category(
        "routing"
    )


def test_profile_rejects_empty_metrics() -> None:
    with pytest.raises(
        ValueError,
        match="pelo menos",
    ):
        MetricProfile(
            profile_id="empty-profile",
            category="test",
            metric_ids=(),
            description="Profile",
        )


def test_registry_rejects_duplicate_metric() -> None:
    metric = build_default_metrics()[0]

    registry = MetricRegistry(
        metrics=(metric,)
    )

    with pytest.raises(
        MetricRegistryError,
        match="já registrada",
    ):
        registry.register_metric(metric)


def test_registry_rejects_unknown_profile_metric() -> None:
    registry = MetricRegistry()

    profile = MetricProfile(
        profile_id="invalid-profile",
        category="invalid",
        metric_ids=(
            "unknown-metric",
        ),
        description="Invalid profile",
    )

    with pytest.raises(
        MetricRegistryError,
        match="não registradas",
    ):
        registry.register_profile(profile)


def test_registry_get_unknown_metric() -> None:
    registry = build_default_metric_registry()

    with pytest.raises(
        MetricNotFoundError,
    ):
        registry.get("unknown")


def test_registry_get_unknown_profile() -> None:
    registry = build_default_metric_registry()

    with pytest.raises(
        MetricProfileNotFoundError,
    ):
        registry.get_profile("unknown")


def test_unknown_category_uses_default_profile() -> None:
    registry = build_default_metric_registry()

    profile = registry.profile_for_category(
        "unknown-category"
    )

    assert profile.profile_id == (
        "default-profile"
    )


def test_for_category_excludes_live_by_default() -> None:
    registry = build_default_metric_registry()

    metrics = registry.for_category(
        "financial-diagnosis"
    )

    assert metrics

    assert all(
        metric.is_local
        for metric in metrics
    )


def test_for_category_can_include_live() -> None:
    registry = build_default_metric_registry()

    metrics = registry.for_category(
        "financial-diagnosis",
        include_live=True,
    )

    assert any(
        metric.is_live
        for metric in metrics
    )


def test_human_review_profile_is_local_only() -> None:
    registry = build_default_metric_registry()

    case = (
        build_conversation_dataset()
        .get_case(
            "human-review-sensitive-guidance-001"
        )
    )

    selection = registry.for_case(
        case,
        include_live=True,
    )

    assert selection.live_metrics == ()

    assert "human-review-policy" in (
        selection.metric_ids
    )


def test_rag_profile_contains_rag_metrics() -> None:
    registry = build_default_metric_registry()

    case = build_core_dataset().get_case(
        "rag-financial-education-001"
    )

    selection = registry.for_case(
        case,
        include_live=True,
    )

    assert "faithfulness" in selection.metric_ids
    assert (
        "contextual-relevancy"
        in selection.metric_ids
    )
    assert (
        "retrieval-contract"
        in selection.metric_ids
    )


def test_required_fields_missing() -> None:
    registry = build_default_metric_registry()

    metric = registry.get("faithfulness")

    payload = build_payload()

    missing = required_payload_fields_missing(
        metric,
        payload,
    )

    assert missing == (
        MetricInputField.RETRIEVAL_CONTEXT,
    )


def test_metric_validation_blocks_missing_field() -> None:
    registry = build_default_metric_registry()

    metric = registry.get("faithfulness")

    with pytest.raises(
        MetricInputValidationError,
        match="retrieval_context",
    ):
        metric.validate_payload(
            build_payload()
        )


def test_metric_validation_accepts_complete_payload() -> None:
    registry = build_default_metric_registry()

    metric = registry.get("faithfulness")

    metric.validate_payload(
        build_payload(
            retrieval_context=(
                "Documento recuperado.",
            )
        )
    )


def test_registry_validates_complete_selection() -> None:
    registry = build_default_metric_registry()

    case = build_core_dataset().get_case(
        "rag-financial-education-001"
    )

    selection = registry.for_case(
        case,
        include_live=True,
    )

    payload = build_payload(
        retrieval_context=(
            "Documento recuperado.",
        )
    )

    registry.validate_selection(
        selection,
        payload,
    )


def test_metric_metadata_is_immutable() -> None:
    metric = MetricDefinition(
        metric_id="immutable-metric",
        display_name="Immutable",
        description="Immutable metadata",
        kind=MetricKind.DETERMINISTIC,
        execution_mode=MetricExecutionMode.LOCAL,
        metadata={
            "source": "test",
        },
    )

    with pytest.raises(TypeError):
        metric.metadata["source"] = "changed"