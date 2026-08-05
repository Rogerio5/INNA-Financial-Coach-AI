from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.evaluation.cli import (
    EvaluationCliExitCode,
    build_cli_summary,
    build_parser,
    main,
    render_text_summary,
    run_live_command,
    run_official_command,
)
from src.evaluation.live_payload_provider import (
    LiveInnaPayloadProvider,
)


def parse_args(
    *arguments: str,
):
    return build_parser().parse_args(list(arguments))


def test_parser_accepts_run_official() -> None:
    args = parse_args(
        "run-official",
        "--no-report",
    )

    assert args.command == "run-official"
    assert args.no_report is True


def test_run_official_passes_without_report() -> None:
    args = parse_args(
        "run-official",
        "--no-report",
    )

    result = run_official_command(args)

    assert result.passed is True
    assert result.batch.total_cases == 11
    assert result.batch.passed_cases == 11
    assert result.external_report is None
    assert result.internal_report is None


def test_cli_summary() -> None:
    args = parse_args(
        "run-official",
        "--no-report",
    )

    result = run_official_command(args)
    summary = build_cli_summary(result)

    assert summary["total_cases"] == 11
    assert summary["quality_gate_passed"] is True
    assert summary["production_evaluation"] is False


def test_text_summary() -> None:
    args = parse_args(
        "run-official",
        "--no-report",
    )

    result = run_official_command(args)
    content = render_text_summary(result)

    assert "Casos totais: 11" in content
    assert "Quality Gate: APROVADO" in content
    assert "Execução de produção: não" in content


def test_main_returns_success(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(
        (
            "run-official",
            "--no-report",
        )
    )

    captured = capsys.readouterr()

    assert exit_code == (EvaluationCliExitCode.SUCCESS)
    assert "Quality Gate: APROVADO" in (captured.out)


def test_main_json_output(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(
        (
            "run-official",
            "--no-report",
            "--json-output",
        )
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["total_cases"] == 11
    assert payload["quality_gate_passed"] is True


def test_production_requirement_fails_gate(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(
        (
            "run-official",
            "--no-report",
            "--require-production-execution",
        )
    )

    captured = capsys.readouterr()

    assert exit_code == (EvaluationCliExitCode.QUALITY_GATE_FAILED)

    assert "Quality Gate: REPROVADO" in (captured.out)


def test_cli_writes_external_report(
    tmp_path: Path,
) -> None:
    exit_code = main(
        (
            "run-official",
            "--output-directory",
            str(tmp_path),
        )
    )

    assert exit_code == 0
    assert tuple(tmp_path.glob("*.json"))


def test_cli_writes_internal_report(
    tmp_path: Path,
) -> None:
    external_directory = tmp_path / "external"
    internal_directory = tmp_path / "internal"

    exit_code = main(
        (
            "run-official",
            "--output-directory",
            str(external_directory),
            "--internal-output-directory",
            str(internal_directory),
            "--write-internal-report",
        )
    )

    assert exit_code == 0
    assert tuple(external_directory.glob("*.json"))
    assert tuple(internal_directory.glob("*.json"))


@pytest.mark.parametrize(
    "invalid_rate",
    (
        "-0.1",
        "1.1",
        "invalid",
    ),
)
def test_parser_rejects_invalid_rate(
    invalid_rate: str,
) -> None:
    with pytest.raises(SystemExit):
        parse_args(
            "run-official",
            "--minimum-pass-rate",
            invalid_rate,
        )


def test_summary_only_report(
    tmp_path: Path,
) -> None:
    exit_code = main(
        (
            "run-official",
            "--output-directory",
            str(tmp_path),
            "--summary-only",
        )
    )

    assert exit_code == 0

    report = next(tmp_path.glob("*.json"))

    payload = json.loads(report.read_text(encoding="utf-8"))

    assert payload["cases"] == []


def _live_success_state():
    return {
        "response": (
            "Gastos fixos são recorrentes, "
            "gastos variáveis mudam conforme "
            "o consumo e a reserva financeira "
            "protege o orçamento."
        ),
        "current_agent": "education_agent",
        "current_team": "knowledge_team",
        "intent": "educacao_financeira",
        "task_status": "completed",
        "task_completion_score": 1.0,
        "tool_results": [
            {
                "tool": ("buscar_conhecimento_rag"),
                "status": "success",
            }
        ],
        "structured_response": {
            "rag_execution": {
                "retrieved_documents": 1,
                "duration_ms": 10.0,
                "retrieval_context": [
                    ("Gastos fixos, gastos variáveis e reserva financeira.")
                ],
            }
        },
    }


def _live_test_provider():
    return LiveInnaPayloadProvider(
        graph_executor=(lambda **kwargs: _live_success_state())
    )


def test_parser_accepts_run_live() -> None:
    args = parse_args(
        "run-live",
        "--case-id",
        "rag-financial-education-001",
        "--no-report",
    )

    assert args.command == "run-live"
    assert args.case_id == "rag-financial-education-001"
    assert args.gate_profile == "single-case"
    assert args.no_report is True


def test_parser_accepts_release_gate_profile() -> None:
    args = parse_args(
        "run-live",
        "--case-id",
        "rag-financial-education-001",
        "--gate-profile",
        "release",
        "--no-report",
    )

    assert args.gate_profile == "release"


def test_parser_rejects_invalid_gate_profile() -> None:
    with pytest.raises(SystemExit):
        parse_args(
            "run-live",
            "--case-id",
            "rag-financial-education-001",
            "--gate-profile",
            "invalid",
        )


def test_run_live_single_case_passes() -> None:
    args = parse_args(
        "run-live",
        "--case-id",
        "rag-financial-education-001",
        "--gate-profile",
        "single-case",
        "--no-report",
    )

    result = run_live_command(
        args,
        provider=_live_test_provider(),
    )

    assert result.passed is True
    assert result.production_evaluation is True
    assert result.command == "run-live"
    assert result.case_id == "rag-financial-education-001"
    assert result.batch.total_cases == 1
    assert result.batch.passed_cases == 1
    assert result.quality_gate.violations == ()


def test_run_live_release_profile_fails_for_single_case() -> None:
    args = parse_args(
        "run-live",
        "--case-id",
        "rag-financial-education-001",
        "--gate-profile",
        "release",
        "--no-report",
    )

    result = run_live_command(
        args,
        provider=_live_test_provider(),
    )

    assert result.batch.status.value == "passed"
    assert result.quality_gate.passed is False

    rules = {violation.rule.value for violation in result.quality_gate.violations}

    assert "required-dataset" in rules


def test_run_live_text_summary() -> None:
    args = parse_args(
        "run-live",
        "--case-id",
        "rag-financial-education-001",
        "--no-report",
    )

    result = run_live_command(
        args,
        provider=_live_test_provider(),
    )

    content = render_text_summary(result)

    assert "INNA LLMOps — Avaliação Real" in content
    assert "Execução de produção: sim" in content
    assert "Caso: rag-financial-education-001" in content
    assert "Taxa de aprovação: 100,00%" in content
    assert "Quality Gate: APROVADO" in content


def test_run_live_json_summary() -> None:
    args = parse_args(
        "run-live",
        "--case-id",
        "rag-financial-education-001",
        "--no-report",
    )

    result = run_live_command(
        args,
        provider=_live_test_provider(),
    )

    summary = build_cli_summary(result)

    assert summary["command"] == "run-live"
    assert summary["execution_type"] == "live-application-evaluation"
    assert summary["production_evaluation"] is True
    assert summary["case_id"] == "rag-financial-education-001"
    assert summary["total_cases"] == 1
    assert summary["passed_cases"] == 1
    assert summary["quality_gate_passed"] is True


def test_run_live_rejects_unknown_case() -> None:
    args = parse_args(
        "run-live",
        "--case-id",
        "case-does-not-exist",
        "--no-report",
    )

    with pytest.raises(
        ValueError,
        match="Caso oficial não encontrado",
    ):
        run_live_command(
            args,
            provider=_live_test_provider(),
        )
