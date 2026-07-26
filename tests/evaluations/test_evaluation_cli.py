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
    run_official_command,
)


def parse_args(
    *arguments: str,
):
    return build_parser().parse_args(
        list(arguments)
    )


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
    assert summary[
        "quality_gate_passed"
    ] is True
    assert summary[
        "production_evaluation"
    ] is False


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

    assert exit_code == (
        EvaluationCliExitCode.SUCCESS
    )
    assert "Quality Gate: APROVADO" in (
        captured.out
    )


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
    assert payload[
        "quality_gate_passed"
    ] is True


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

    assert exit_code == (
        EvaluationCliExitCode
        .QUALITY_GATE_FAILED
    )

    assert "Quality Gate: REPROVADO" in (
        captured.out
    )


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
    assert tuple(
        tmp_path.glob("*.json")
    )


def test_cli_writes_internal_report(
    tmp_path: Path,
) -> None:
    external_directory = (
        tmp_path / "external"
    )
    internal_directory = (
        tmp_path / "internal"
    )

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
    assert tuple(
        external_directory.glob("*.json")
    )
    assert tuple(
        internal_directory.glob("*.json")
    )


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

    report = next(
        tmp_path.glob("*.json")
    )

    payload = json.loads(
        report.read_text(
            encoding="utf-8"
        )
    )

    assert payload["cases"] == []