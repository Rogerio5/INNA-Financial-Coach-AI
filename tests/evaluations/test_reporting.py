from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType

import pytest

from src.evaluation.batch_runner import (
    EvaluationBatchRunner,
)
from src.evaluation.case_catalog import (
    build_core_dataset,
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
from src.evaluation.reporting import (
    EvaluationReportSerializationError,
    _validate_external_report_projection,
    batch_report_to_json,
    build_batch_report,
    build_external_generated_date,
    build_external_run_reference,
    build_report_filename,
    to_json_compatible,
    write_batch_report,
)


class ExampleEnum(StrEnum):
    VALUE = "value"


def build_batch():
    return EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=(SyntheticPassingPayloadProvider()),
    ).run(
        (build_core_dataset(),),
        runner_settings=(
            EvaluationRunnerSettings(
                mode=EvaluationRunMode.LOCAL,
            )
        ),
        metadata={
            "production_evaluation": False,
        },
    )


def build_external_projection(
    *,
    batch: dict | None = None,
    cases: list | None = None,
) -> dict:
    return {
        "schema_version": "1.0.0",
        "report_type": "inna-evaluation-batch",
        "generated_at": None,
        "batch": batch or {},
        "summary": {},
        "datasets": [],
        "categories": [],
        "metrics": [],
        "cases": cases or [],
    }


def test_json_compatible_scalars() -> None:
    assert to_json_compatible(None) is None
    assert to_json_compatible(True) is True
    assert to_json_compatible(10) == 10
    assert to_json_compatible(1.5) == 1.5
    assert to_json_compatible("text") == "text"


def test_json_compatible_special_types() -> None:
    value = {
        "enum": ExampleEnum.VALUE,
        "datetime": datetime(
            2026,
            7,
            25,
            tzinfo=UTC,
        ),
        "path": Path("artifact.json"),
        "mapping": MappingProxyType(
            {
                "key": "value",
            }
        ),
        "tuple": (
            "a",
            "b",
        ),
    }

    serialized = to_json_compatible(value)

    assert serialized["enum"] == "value"
    assert serialized["datetime"].startswith("2026-07-25")
    assert serialized["path"] == "artifact.json"
    assert serialized["mapping"] == {
        "key": "value",
    }
    assert serialized["tuple"] == [
        "a",
        "b",
    ]


def test_json_compatible_rejects_unknown_type() -> None:
    with pytest.raises(
        EvaluationReportSerializationError,
    ):
        to_json_compatible(object())


def test_build_batch_report() -> None:
    report = build_batch_report(
        build_batch(),
        sanitize=False,
    )

    assert report["schema_version"] == "1.0.0"
    assert report["report_type"] == ("inna-evaluation-batch")
    assert report["summary"]["total_cases"] == 6
    assert report["summary"]["passed_cases"] == 6
    assert len(report["cases"]) == 6


def test_report_can_omit_case_details() -> None:
    report = build_batch_report(
        build_batch(),
        sanitize=False,
        include_case_details=False,
    )

    assert report["cases"] == []


def test_report_serializes_to_valid_json() -> None:
    content = batch_report_to_json(
        build_batch(),
        sanitize=False,
    )

    payload = json.loads(content)

    assert payload["summary"]["total_cases"] == 6


def test_report_filename() -> None:
    filename = build_report_filename(build_batch())

    assert filename.startswith("inna-evaluation-")
    assert filename.endswith(".json")


def test_write_report(
    tmp_path: Path,
) -> None:
    destination = write_batch_report(
        build_batch(),
        output_directory=tmp_path,
        sanitize=False,
    )

    assert destination.is_file()

    payload = json.loads(destination.read_text(encoding="utf-8"))

    assert payload["summary"]["total_cases"] == 6


def test_write_custom_filename(
    tmp_path: Path,
) -> None:
    destination = write_batch_report(
        build_batch(),
        output_directory=tmp_path,
        filename="custom-report",
        sanitize=False,
    )

    assert destination.name == ("custom-report.json")


def test_sanitized_report_excludes_case_content() -> None:
    report = build_batch_report(
        build_batch(),
        sanitize=True,
        include_case_details=True,
    )

    assert report["cases"]

    first_case = report["cases"][0]

    assert set(first_case) == {
        "dataset_id",
        "case_id",
        "category",
        "status",
        "has_evaluation",
        "error_type",
    }

    assert "input_text" not in first_case
    assert "actual_output" not in first_case
    assert "evaluation" not in first_case
    assert "metadata" not in first_case
    assert "retrieval_context" not in first_case


def test_internal_report_can_include_complete_details() -> None:
    report = build_batch_report(
        build_batch(),
        sanitize=False,
        include_case_details=True,
    )

    assert report["cases"]

    first_case = report["cases"][0]

    assert "evaluation" in first_case
    assert first_case["evaluation"] is not None
    assert "metric_results" in first_case["evaluation"]


def test_sanitized_report_uses_metadata_allowlist() -> None:
    batch = build_batch()

    altered = replace(
        batch,
        metadata={
            "execution_type": "synthetic-test",
            "production_evaluation": False,
            "production_execution": False,
            "official_case_count": 6,
            "cli_command": "run-official",
            "confidential_value": ("Não deve ser exportado."),
        },
    )

    report = build_batch_report(
        altered,
        sanitize=True,
    )

    metadata = report["batch"]["metadata"]

    assert metadata == {
        "production_evaluation": False,
        "production_execution": False,
        "official_case_count": 6,
    }

    assert "execution_type" not in metadata
    assert "cli_command" not in metadata
    assert "confidential_value" not in metadata


def test_sanitized_quality_gate_excludes_raw_values() -> None:
    from src.evaluation.quality_gate import (
        QualityGateRule,
        QualityGateSeverity,
        QualityGateViolation,
    )

    class Gate:
        passed = False
        evaluated_rules = 1
        batch_id = "batch-safe"
        violations = (
            QualityGateViolation(
                rule=QualityGateRule.BATCH_STATUS,
                severity=QualityGateSeverity.ERROR,
                message="O lote foi reprovado.",
                actual={
                    "confidential": "valor privado",
                },
                expected={
                    "confidential": "valor esperado",
                },
                metadata={
                    "secret": "não exportar",
                },
            ),
        )

    report = build_batch_report(
        build_batch(),
        quality_gate=Gate(),
        sanitize=True,
    )

    gate = report["quality_gate"]
    violation = gate["violations"][0]

    assert gate["passed"] is False
    assert gate["batch_id"] is None
    assert gate["run_reference"] == (report["run_reference"])

    assert set(violation) == {
        "rule",
        "severity",
        "message",
    }

    assert "actual" not in violation
    assert "expected" not in violation
    assert "metadata" not in violation


def test_sanitized_report_excludes_internal_batch_ids() -> None:
    batch = build_batch()

    report = build_batch_report(
        batch,
        sanitize=True,
    )

    assert report["batch"]["batch_id"] is None
    assert report["run_reference"].startswith("run-")


def test_internal_report_preserves_batch_id() -> None:
    batch = build_batch()

    report = build_batch_report(
        batch,
        sanitize=False,
    )

    assert report["batch"]["batch_id"] == (batch.batch_id)


def test_sanitized_report_excludes_internal_timestamps() -> None:
    batch = build_batch()

    report = build_batch_report(
        batch,
        sanitize=True,
    )

    assert report["generated_at"] is None
    assert report["batch"]["started_at"] is None
    assert report["batch"]["finished_at"] is None


def test_internal_report_preserves_timestamps() -> None:
    batch = build_batch()

    report = build_batch_report(
        batch,
        sanitize=False,
    )

    assert report["generated_at"] is not None
    assert report["batch"]["started_at"] == (batch.started_at.isoformat())
    assert report["batch"]["finished_at"] == (batch.finished_at.isoformat())


def test_external_run_reference_is_stable() -> None:
    first = build_external_run_reference("batch-internal-001")
    second = build_external_run_reference("batch-internal-001")

    assert first == second
    assert first.startswith("run-")
    assert len(first) == 12


def test_external_run_reference_changes_by_batch() -> None:
    first = build_external_run_reference("batch-internal-001")
    second = build_external_run_reference("batch-internal-002")

    assert first != second


def test_external_run_reference_rejects_empty_id() -> None:
    with pytest.raises(
        ValueError,
        match="batch_id",
    ):
        build_external_run_reference(" ")


def test_external_generated_date() -> None:
    value = datetime(
        2026,
        7,
        26,
        1,
        30,
        tzinfo=UTC,
    )

    assert build_external_generated_date(value) == "2026-07-26"


def test_external_generated_date_requires_timezone() -> None:
    value = datetime(
        2026,
        7,
        26,
        1,
        30,
    )

    with pytest.raises(
        ValueError,
        match="timezone",
    ):
        build_external_generated_date(value)


def test_sanitized_report_contains_safe_reference() -> None:
    batch = build_batch()

    report = build_batch_report(
        batch,
        sanitize=True,
    )

    expected_reference = build_external_run_reference(batch.batch_id)

    assert report["run_reference"] == (expected_reference)
    assert report["generated_date"] == (batch.started_at.date().isoformat())
    assert report["batch"]["run_reference"] == (expected_reference)

    assert report["batch"]["batch_id"] is None
    assert report["generated_at"] is None
    assert report["batch"]["started_at"] is None
    assert report["batch"]["finished_at"] is None


def test_sanitized_quality_gate_uses_run_reference() -> None:
    from src.evaluation.quality_gate import (
        evaluate_quality_gate,
    )

    batch = build_batch()
    gate = evaluate_quality_gate(batch)

    report = build_batch_report(
        batch,
        quality_gate=gate,
        sanitize=True,
    )

    assert report["quality_gate"]["batch_id"] is None

    assert report["quality_gate"]["run_reference"] == report["run_reference"]


def test_internal_report_keeps_complete_traceability() -> None:
    batch = build_batch()

    report = build_batch_report(
        batch,
        sanitize=False,
    )

    assert report["batch"]["batch_id"] == (batch.batch_id)
    assert report["generated_at"] is not None
    assert report["batch"]["started_at"] == (batch.started_at.isoformat())
    assert report["batch"]["finished_at"] == (batch.finished_at.isoformat())


def test_external_projection_rejects_user_content() -> None:
    payload = build_external_projection(
        cases=[
            {
                "input_text": ("Conteúdo que não pode ser exportado."),
            },
        ],
    )

    with pytest.raises(
        EvaluationReportSerializationError,
        match="Campo proibido",
    ):
        _validate_external_report_projection(payload)


def test_external_projection_rejects_secret() -> None:
    payload = build_external_projection(
        batch={
            "api_key": ("valor-que-nao-pode-ser-exportado"),
        },
    )

    with pytest.raises(
        EvaluationReportSerializationError,
        match="segredo",
    ):
        _validate_external_report_projection(payload)


def test_external_projection_rejects_secret_key_case_insensitive() -> None:
    payload = build_external_projection(
        batch={
            "CLIENT_SECRET": "valor-privado",
        },
    )

    with pytest.raises(
        EvaluationReportSerializationError,
        match="segredo",
    ):
        _validate_external_report_projection(payload)


@pytest.mark.parametrize(
    "secret_key",
    (
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "password",
        "passwd",
        "token",
        "access_token",
        "refresh_token",
        "private_key",
        "authorization",
        "credential",
        "credentials",
    ),
)
def test_external_projection_rejects_known_secret_keys(
    secret_key: str,
) -> None:
    payload = build_external_projection(
        batch={
            secret_key: "valor-privado",
        },
    )

    with pytest.raises(
        EvaluationReportSerializationError,
        match="segredo",
    ):
        _validate_external_report_projection(payload)
