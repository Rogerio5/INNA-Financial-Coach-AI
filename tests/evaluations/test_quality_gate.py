from __future__ import annotations

from dataclasses import replace
from types import MappingProxyType

import pytest

from src.evaluation.batch_runner import (
    BatchCaseStatus,
    BatchRunStatus,
    EvaluationBatchRunner,
)
from src.evaluation.case_catalog import (
    official_datasets,
)
from src.evaluation.deepeval_runner import (
    EvaluationRunMode,
    EvaluationRunnerSettings,
)
from src.evaluation.deterministic_executors import (
    build_deterministic_runner,
)
from src.evaluation.payload_providers import (
    SyntheticPassingPayloadProvider,
)
from src.evaluation.quality_gate import (
    QualityGateRule,
    QualityGateSettings,
    QualityGateSeverity,
    QualityGateViolation,
    evaluate_quality_gate,
)


def build_official_batch():
    return EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=(SyntheticPassingPayloadProvider()),
    ).run(
        official_datasets(),
        runner_settings=(
            EvaluationRunnerSettings(
                mode=EvaluationRunMode.LOCAL,
            )
        ),
        metadata={
            "execution_type": ("synthetic-infrastructure-validation"),
            "production_evaluation": False,
        },
    )


def test_default_gate_passes() -> None:
    result = evaluate_quality_gate(build_official_batch())

    assert result.passed is True
    assert result.violations == ()
    assert not result.critical_violations
    assert not result.error_violations


def test_gate_evaluates_rules() -> None:
    result = evaluate_quality_gate(build_official_batch())

    assert result.evaluated_rules > 0
    assert result.batch_id


def test_gate_rejects_synthetic_as_production() -> None:
    result = evaluate_quality_gate(
        build_official_batch(),
        QualityGateSettings(
            require_production_execution=True,
        ),
    )

    assert result.passed is False

    assert any(
        violation.rule == (QualityGateRule.SYNTHETIC_PRODUCTION_MISMATCH)
        for violation in result.violations
    )


def test_production_violation_is_critical() -> None:
    result = evaluate_quality_gate(
        build_official_batch(),
        QualityGateSettings(
            require_production_execution=True,
        ),
    )

    violation = next(
        violation
        for violation in result.violations
        if violation.rule == (QualityGateRule.SYNTHETIC_PRODUCTION_MISMATCH)
    )

    assert violation.severity == (QualityGateSeverity.CRITICAL)


def test_gate_rejects_missing_dataset() -> None:
    result = evaluate_quality_gate(
        build_official_batch(),
        QualityGateSettings(
            required_dataset_ids=("missing-dataset@1.0.0",),
        ),
    )

    assert result.passed is False

    assert any(
        violation.rule == QualityGateRule.REQUIRED_DATASET
        for violation in result.violations
    )


def test_missing_critical_metric_is_warning() -> None:
    result = evaluate_quality_gate(
        build_official_batch(),
        QualityGateSettings(
            critical_metric_ids=("missing-metric",),
            fail_on_warning=False,
        ),
    )

    assert result.passed is True
    assert result.warning_violations

    violation = result.warning_violations[0]

    assert violation.rule == (QualityGateRule.CRITICAL_METRIC)
    assert violation.metadata["metric_id"] == "missing-metric"


def test_warning_can_fail_gate() -> None:
    result = evaluate_quality_gate(
        build_official_batch(),
        QualityGateSettings(
            critical_metric_ids=("missing-metric",),
            fail_on_warning=True,
        ),
    )

    assert result.passed is False
    assert result.warning_violations


@pytest.mark.parametrize(
    "invalid_rate",
    (
        -0.1,
        1.1,
    ),
)
def test_settings_reject_invalid_rate(
    invalid_rate: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="minimum_pass_rate",
    ):
        QualityGateSettings(
            minimum_pass_rate=invalid_rate,
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "maximum_failed_cases",
        "maximum_blocked_cases",
        "maximum_error_cases",
    ),
)
def test_settings_reject_negative_case_limits(
    field_name: str,
) -> None:
    arguments = {
        field_name: -1,
    }

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        QualityGateSettings(**arguments)


def test_settings_reject_negative_cost() -> None:
    with pytest.raises(
        ValueError,
        match="maximum_total_cost",
    ):
        QualityGateSettings(
            maximum_total_cost=-0.01,
        )


def test_settings_normalize_metric_ids() -> None:
    settings = QualityGateSettings(
        critical_metric_ids=(
            " FORBIDDEN-TERMS ",
            "forbidden-terms",
            "CONTRACT-VALIDATION",
        ),
    )

    assert settings.critical_metric_ids == (
        "forbidden-terms",
        "contract-validation",
    )


def test_settings_remove_duplicate_datasets() -> None:
    settings = QualityGateSettings(
        required_dataset_ids=(
            "inna-core@1.0.0",
            "inna-core@1.0.0",
        ),
    )

    assert settings.required_dataset_ids == ("inna-core@1.0.0",)


def test_violation_metadata_is_immutable() -> None:
    violation = QualityGateViolation(
        rule=QualityGateRule.BATCH_STATUS,
        severity=QualityGateSeverity.ERROR,
        message="Falha sintética.",
        metadata={
            "source": "test",
        },
    )

    assert isinstance(
        violation.metadata,
        MappingProxyType,
    )

    with pytest.raises(TypeError):
        violation.metadata["source"] = "changed"


def test_violation_message_is_normalized() -> None:
    violation = QualityGateViolation(
        rule=QualityGateRule.BATCH_STATUS,
        severity=QualityGateSeverity.ERROR,
        message="  Falha sintética.  ",
    )

    assert violation.message == ("Falha sintética.")


def test_violation_rejects_empty_message() -> None:
    with pytest.raises(
        ValueError,
        match="message",
    ):
        QualityGateViolation(
            rule=QualityGateRule.BATCH_STATUS,
            severity=QualityGateSeverity.ERROR,
            message=" ",
        )


def test_gate_rejects_batch_error_count() -> None:
    batch = build_official_batch()

    altered = replace(
        batch,
        case_results=(
            replace(
                batch.case_results[0],
                status=BatchCaseStatus.ERROR,
                evaluation=None,
                error_type="RuntimeError",
                error_message="Synthetic error",
            ),
            *batch.case_results[1:],
        ),
    )

    result = evaluate_quality_gate(altered)

    assert result.passed is False
    assert result.critical_violations

    assert any(
        violation.rule == QualityGateRule.MAXIMUM_ERROR_CASES
        for violation in result.violations
    )


def test_gate_rejects_failed_case() -> None:
    batch = build_official_batch()

    altered = replace(
        batch,
        status=BatchRunStatus.FAILED,
        case_results=(
            replace(
                batch.case_results[0],
                status=BatchCaseStatus.FAILED,
            ),
            *batch.case_results[1:],
        ),
    )

    result = evaluate_quality_gate(altered)

    assert result.passed is False

    rules = {violation.rule for violation in result.violations}

    assert QualityGateRule.BATCH_STATUS in rules
    assert QualityGateRule.MINIMUM_PASS_RATE in rules
    assert QualityGateRule.MAXIMUM_FAILED_CASES in rules


def test_gate_rejects_blocked_case() -> None:
    batch = build_official_batch()

    altered = replace(
        batch,
        case_results=(
            replace(
                batch.case_results[0],
                status=BatchCaseStatus.BLOCKED,
            ),
            *batch.case_results[1:],
        ),
    )

    result = evaluate_quality_gate(altered)

    assert result.passed is False

    assert any(
        violation.rule == QualityGateRule.MAXIMUM_BLOCKED_CASES
        for violation in result.violations
    )


def test_gate_allows_configured_pass_rate() -> None:
    batch = build_official_batch()

    altered = replace(
        batch,
        case_results=(
            replace(
                batch.case_results[0],
                status=BatchCaseStatus.FAILED,
            ),
            *batch.case_results[1:],
        ),
    )

    result = evaluate_quality_gate(
        altered,
        QualityGateSettings(
            minimum_pass_rate=0.90,
            maximum_failed_cases=1,
            critical_metric_ids=(),
        ),
    )

    assert altered.pass_rate == pytest.approx(10 / 11)
    assert altered.failed_cases == 1
    assert result.passed is True
    assert result.violations == ()


def test_gate_checks_maximum_cost() -> None:
    batch = build_official_batch()

    altered = replace(
        batch,
        total_estimated_cost=0.10,
    )

    result = evaluate_quality_gate(
        altered,
        QualityGateSettings(
            maximum_total_cost=0.05,
        ),
    )

    assert result.passed is False

    violation = next(
        violation
        for violation in result.violations
        if violation.rule == QualityGateRule.MAXIMUM_TOTAL_COST
    )

    assert violation.actual == pytest.approx(0.10)
    assert violation.expected == pytest.approx(0.05)
