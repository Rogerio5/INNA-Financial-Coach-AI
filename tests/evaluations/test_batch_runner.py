from __future__ import annotations

from types import MappingProxyType
from typing import Any

import pytest

from src.evaluation.batch_runner import (
    BatchCaseStatus,
    BatchRunStatus,
    EvaluationBatchRunner,
)
from src.evaluation.case_catalog import (
    build_core_dataset,
    official_case_count,
    official_datasets,
)
from src.evaluation.contracts import (
    InnaEvaluationCase,
)
from src.evaluation.deepeval_integration import (
    DeepEvalCasePayload,
)
from src.evaluation.deepeval_runner import (
    EvaluationRunMode,
    EvaluationRunnerSettings,
)
from src.evaluation.deterministic_executors import (
    build_deterministic_runner,
)
from src.evaluation.payload_providers import (
    PayloadProviderError,
    RecordedPayloadNotFoundError,
    RecordedPayloadProvider,
    SyntheticPassingPayloadProvider,
)


def test_synthetic_provider_builds_payload() -> None:
    case = build_core_dataset().cases[0]

    provider = SyntheticPassingPayloadProvider()

    payload = provider(case)

    assert isinstance(
        payload,
        DeepEvalCasePayload,
    )
    assert payload.case_id == case.case_id
    assert payload.actual_output
    assert payload.metadata[
        "synthetic_provider"
    ] is True
    assert payload.metadata[
        "production_execution"
    ] is False


def test_synthetic_provider_metadata_is_immutable(
) -> None:
    provider = SyntheticPassingPayloadProvider(
        metadata={
            "source": "test",
        }
    )

    assert isinstance(
        provider.metadata,
        MappingProxyType,
    )

    with pytest.raises(TypeError):
        provider.metadata["source"] = "changed"


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        (
            "latency_ms",
            -1,
        ),
        (
            "estimated_cost",
            -0.1,
        ),
    ),
)
def test_synthetic_provider_rejects_negative_values(
    field_name: str,
    value: float,
) -> None:
    arguments: dict[str, Any] = {
        field_name: value,
    }

    with pytest.raises(ValueError):
        SyntheticPassingPayloadProvider(
            **arguments
        )


def test_recorded_provider_returns_payload() -> None:
    case = build_core_dataset().cases[0]
    payload = SyntheticPassingPayloadProvider()(
        case
    )

    provider = RecordedPayloadProvider(
        {
            case.case_id: payload,
        }
    )

    assert provider(case) is payload


def test_recorded_provider_rejects_missing_case() -> None:
    case = build_core_dataset().cases[0]

    provider = RecordedPayloadProvider({})

    with pytest.raises(
        RecordedPayloadNotFoundError,
    ):
        provider(case)


def test_recorded_provider_rejects_mismatch() -> None:
    first_case = build_core_dataset().cases[0]
    second_case = build_core_dataset().cases[1]

    payload = SyntheticPassingPayloadProvider()(
        second_case
    )

    provider = RecordedPayloadProvider(
        {
            first_case.case_id: payload,
        }
    )

    with pytest.raises(
        PayloadProviderError,
        match="incompatível",
    ):
        provider(first_case)


def test_official_batch_passes() -> None:
    batch_runner = EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=(
            SyntheticPassingPayloadProvider()
        ),
    )

    result = batch_runner.run(
        official_datasets(),
        runner_settings=(
            EvaluationRunnerSettings(
                mode=EvaluationRunMode.LOCAL,
            )
        ),
    )

    assert result.status == (
        BatchRunStatus.PASSED
    )
    assert result.total_cases == (
        official_case_count()
    )
    assert result.total_cases == 11
    assert result.passed_cases == 11
    assert result.failed_cases == 0
    assert result.error_cases == 0
    assert result.pass_rate == pytest.approx(
        1.0
    )


def test_batch_has_three_dataset_summaries() -> None:
    batch_runner = EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=(
            SyntheticPassingPayloadProvider()
        ),
    )

    result = batch_runner.run(
        official_datasets(),
        runner_settings=(
            EvaluationRunnerSettings(
                mode=EvaluationRunMode.LOCAL,
            )
        ),
    )

    summaries = {
        item.dataset_id: item
        for item in result.dataset_summaries
    }

    assert set(summaries) == {
        "inna-core@1.0.0",
        "inna-safety@1.0.0",
        "inna-conversation@1.0.0",
    }

    assert summaries[
        "inna-core@1.0.0"
    ].total_cases == 6

    assert summaries[
        "inna-safety@1.0.0"
    ].total_cases == 3

    assert summaries[
        "inna-conversation@1.0.0"
    ].total_cases == 2


def test_batch_creates_metric_summaries() -> None:
    batch_runner = EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=(
            SyntheticPassingPayloadProvider()
        ),
    )

    result = batch_runner.run(
        official_datasets(),
        runner_settings=(
            EvaluationRunnerSettings(
                mode=EvaluationRunMode.LOCAL,
            )
        ),
    )

    metric_ids = {
        summary.metric_id
        for summary in result.metric_summaries
    }

    assert "contract-validation" in metric_ids
    assert "expected-terms" in metric_ids
    assert "forbidden-terms" in metric_ids


def test_batch_isolates_provider_error() -> None:
    cases_called = 0

    def failing_provider(
        case: InnaEvaluationCase,
    ) -> DeepEvalCasePayload:
        nonlocal cases_called
        cases_called += 1

        if cases_called == 1:
            raise RuntimeError(
                "Falha sintética."
            )

        return SyntheticPassingPayloadProvider()(
            case
        )

    dataset = build_core_dataset()

    batch_runner = EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=failing_provider,
    )

    result = batch_runner.run(
        (dataset,),
        runner_settings=(
            EvaluationRunnerSettings(
                mode=EvaluationRunMode.LOCAL,
            )
        ),
        continue_on_case_error=True,
    )

    assert result.total_cases == 6
    assert result.error_cases == 1
    assert result.passed_cases == 5
    assert result.status == (
        BatchRunStatus.PARTIAL
    )


def test_batch_can_stop_after_case_error() -> None:
    def failing_provider(
        case: InnaEvaluationCase,
    ) -> DeepEvalCasePayload:
        raise RuntimeError(
            "Falha sintética."
        )

    batch_runner = EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=failing_provider,
    )

    result = batch_runner.run(
        (
            build_core_dataset(),
        ),
        runner_settings=(
            EvaluationRunnerSettings(
                mode=EvaluationRunMode.LOCAL,
            )
        ),
        continue_on_case_error=False,
    )

    assert result.total_cases == 1
    assert result.error_cases == 1
    assert result.status == (
        BatchRunStatus.ERROR
    )


def test_batch_metadata_is_immutable() -> None:
    result = EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=(
            SyntheticPassingPayloadProvider()
        ),
    ).run(
        (
            build_core_dataset(),
        ),
        runner_settings=(
            EvaluationRunnerSettings(
                mode=EvaluationRunMode.LOCAL,
            )
        ),
        metadata={
            "source": "test",
        },
    )

    assert isinstance(
        result.metadata,
        MappingProxyType,
    )

    with pytest.raises(TypeError):
        result.metadata["source"] = "changed"


def test_case_results_reference_evaluations() -> None:
    result = EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=(
            SyntheticPassingPayloadProvider()
        ),
    ).run(
        (
            build_core_dataset(),
        ),
        runner_settings=(
            EvaluationRunnerSettings(
                mode=EvaluationRunMode.LOCAL,
            )
        ),
    )

    assert all(
        case_result.status
        == BatchCaseStatus.PASSED
        for case_result in result.case_results
    )

    assert all(
        case_result.evaluation is not None
        for case_result in result.case_results
    )