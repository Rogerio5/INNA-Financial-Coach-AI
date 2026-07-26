from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any

from src.evaluation.batch_runner import (
    BatchRunResult,
    EvaluationBatchRunner,
)
from src.evaluation.case_catalog import (
    official_case_count,
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
    QualityGateResult,
    QualityGateSettings,
    evaluate_quality_gate,
)
from src.evaluation.reporting import (
    write_batch_report,
)


class EvaluationCliExitCode(IntEnum):
    SUCCESS = 0
    QUALITY_GATE_FAILED = 2
    CONFIGURATION_ERROR = 3
    EXECUTION_ERROR = 4
    REPORT_ERROR = 5


@dataclass(frozen=True, slots=True)
class CliRunResult:
    batch: BatchRunResult
    quality_gate: QualityGateResult
    external_report: Path | None
    internal_report: Path | None

    @property
    def passed(self) -> bool:
        return self.quality_gate.passed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inna-evaluation",
        description=(
            "CLI oficial para execução local das avaliações "
            "LLMOps da INNA."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    run_parser = subparsers.add_parser(
        "run-official",
        help=(
            "Executa os datasets oficiais usando o "
            "provedor sintético de infraestrutura."
        ),
    )

    run_parser.add_argument(
        "--output-directory",
        default="artifacts/evaluations",
        help=(
            "Diretório do relatório externo sanitizado."
        ),
    )

    run_parser.add_argument(
        "--internal-output-directory",
        default="artifacts/evaluations/internal",
        help=(
            "Diretório do relatório interno completo."
        ),
    )

    run_parser.add_argument(
        "--write-internal-report",
        action="store_true",
        help=(
            "Também grava relatório interno completo. "
            "Esse arquivo não deve ser exportado."
        ),
    )

    run_parser.add_argument(
        "--summary-only",
        action="store_true",
        help=(
            "Remove os detalhes dos casos do relatório."
        ),
    )

    run_parser.add_argument(
        "--minimum-pass-rate",
        type=_rate_argument,
        default=1.0,
        help=(
            "Taxa mínima de aprovação entre 0 e 1. "
            "Padrão: 1.0."
        ),
    )

    run_parser.add_argument(
        "--maximum-failed-cases",
        type=_non_negative_int_argument,
        default=0,
    )

    run_parser.add_argument(
        "--maximum-blocked-cases",
        type=_non_negative_int_argument,
        default=0,
    )

    run_parser.add_argument(
        "--maximum-error-cases",
        type=_non_negative_int_argument,
        default=0,
    )

    run_parser.add_argument(
        "--maximum-total-cost",
        type=_non_negative_float_argument,
        default=0.0,
    )

    run_parser.add_argument(
        "--fail-on-warning",
        action="store_true",
    )

    run_parser.add_argument(
        "--require-production-execution",
        action="store_true",
        help=(
            "Exige execução real da aplicação. Como este "
            "comando usa payload sintético, o gate será "
            "bloqueado quando esta opção for usada."
        ),
    )

    run_parser.add_argument(
        "--json-output",
        action="store_true",
        help=(
            "Imprime o resumo da execução em JSON."
        ),
    )

    run_parser.add_argument(
        "--no-report",
        action="store_true",
        help=(
            "Executa o lote e o gate sem gravar relatório."
        ),
    )

    return parser


def run_official_command(
    args: argparse.Namespace,
) -> CliRunResult:
    provider = SyntheticPassingPayloadProvider()

    batch_runner = EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=provider,
    )

    batch = batch_runner.run(
        official_datasets(),
        runner_settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
        ),
        metadata={
            "execution_type": (
                "synthetic-infrastructure-validation"
            ),
            "provider": (
                "SyntheticPassingPayloadProvider"
            ),
            "production_evaluation": False,
            "official_case_count": (
                official_case_count()
            ),
            "cli_command": "run-official",
        },
    )

    gate_settings = QualityGateSettings(
        minimum_pass_rate=args.minimum_pass_rate,
        maximum_failed_cases=(
            args.maximum_failed_cases
        ),
        maximum_blocked_cases=(
            args.maximum_blocked_cases
        ),
        maximum_error_cases=(
            args.maximum_error_cases
        ),
        maximum_total_cost=(
            args.maximum_total_cost
        ),
        require_production_execution=(
            args.require_production_execution
        ),
        fail_on_warning=args.fail_on_warning,
    )

    gate = evaluate_quality_gate(
        batch,
        gate_settings,
    )

    external_report: Path | None = None
    internal_report: Path | None = None

    if not args.no_report:
        external_report = write_batch_report(
            batch,
            output_directory=(
                args.output_directory
            ),
            quality_gate=gate,
            sanitize=True,
            include_case_details=(
                not args.summary_only
            ),
        )

        if args.write_internal_report:
            internal_report = write_batch_report(
                batch,
                output_directory=(
                    args.internal_output_directory
                ),
                quality_gate=gate,
                sanitize=False,
                include_case_details=(
                    not args.summary_only
                ),
                filename=(
                    "inna-evaluation-internal-complete"
                ),
            )

    return CliRunResult(
        batch=batch,
        quality_gate=gate,
        external_report=external_report,
        internal_report=internal_report,
    )


def build_cli_summary(
    result: CliRunResult,
) -> dict[str, Any]:
    batch = result.batch
    gate = result.quality_gate

    return {
        "command": "run-official",
        "execution_type": (
            "synthetic-infrastructure-validation"
        ),
        "production_evaluation": False,
        "batch_id": batch.batch_id,
        "batch_status": batch.status.value,
        "total_cases": batch.total_cases,
        "passed_cases": batch.passed_cases,
        "failed_cases": batch.failed_cases,
        "blocked_cases": batch.blocked_cases,
        "error_cases": batch.error_cases,
        "pass_rate": batch.pass_rate,
        "total_estimated_cost": (
            batch.total_estimated_cost
        ),
        "quality_gate_passed": gate.passed,
        "quality_gate_violations": [
            {
                "rule": violation.rule.value,
                "severity": (
                    violation.severity.value
                ),
                "message": violation.message,
                "actual": violation.actual,
                "expected": violation.expected,
            }
            for violation in gate.violations
        ],
        "external_report": (
            str(result.external_report)
            if result.external_report
            else None
        ),
        "internal_report": (
            str(result.internal_report)
            if result.internal_report
            else None
        ),
    }


def render_text_summary(
    result: CliRunResult,
) -> str:
    batch = result.batch
    gate = result.quality_gate

    lines = [
        "INNA LLMOps — Avaliação Oficial",
        "=" * 42,
        (
            "Tipo de execução: "
            "validação sintética da infraestrutura"
        ),
        "Execução de produção: não",
        f"Batch ID: {batch.batch_id}",
        f"Status do lote: {batch.status.value}",
        f"Casos totais: {batch.total_cases}",
        f"Casos aprovados: {batch.passed_cases}",
        f"Casos reprovados: {batch.failed_cases}",
        f"Casos bloqueados: {batch.blocked_cases}",
        f"Casos com erro: {batch.error_cases}",
        f"Taxa de aprovação: {batch.pass_rate:.2%}",
        (
            "Custo estimado: "
            f"US$ {batch.total_estimated_cost:.6f}"
        ),
        (
            "Quality Gate: "
            f"{'APROVADO' if gate.passed else 'REPROVADO'}"
        ),
    ]

    if result.external_report is not None:
        lines.append(
            "Relatório externo: "
            f"{result.external_report}"
        )

    if result.internal_report is not None:
        lines.append(
            "Relatório interno: "
            f"{result.internal_report}"
        )

    if gate.violations:
        lines.extend(
            (
                "",
                "Violações:",
            )
        )

        for violation in gate.violations:
            lines.append(
                "- "
                f"[{violation.severity.value}] "
                f"{violation.rule.value}: "
                f"{violation.message}"
            )

    return "\n".join(lines)


def main(
    argv: Sequence[str] | None = None,
) -> int:
    parser = build_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)

    try:
        if args.command != "run-official":
            parser.error(
                f"Comando não suportado: {args.command}"
            )

        result = run_official_command(args)

        if args.json_output:
            print(
                json.dumps(
                    build_cli_summary(result),
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                    allow_nan=False,
                )
            )
        else:
            print(
                render_text_summary(result)
            )

        if result.quality_gate.passed:
            return int(
                EvaluationCliExitCode.SUCCESS
            )

        return int(
            EvaluationCliExitCode
            .QUALITY_GATE_FAILED
        )

    except (
        ValueError,
        argparse.ArgumentTypeError,
    ) as error:
        print(
            f"Erro de configuração: {error}",
            file=sys.stderr,
        )

        return int(
            EvaluationCliExitCode
            .CONFIGURATION_ERROR
        )

    except OSError as error:
        print(
            f"Erro ao gravar relatório: {error}",
            file=sys.stderr,
        )

        return int(
            EvaluationCliExitCode.REPORT_ERROR
        )

    except Exception as error:
        print(
            "Erro inesperado durante a avaliação: "
            f"{type(error).__name__}: {error}",
            file=sys.stderr,
        )

        return int(
            EvaluationCliExitCode.EXECUTION_ERROR
        )


def _rate_argument(
    value: str,
) -> float:
    try:
        parsed = float(value)
    except ValueError as exception:
        raise argparse.ArgumentTypeError(
            "A taxa precisa ser numérica."
        ) from exception

    if not 0.0 <= parsed <= 1.0:
        raise argparse.ArgumentTypeError(
            "A taxa precisa estar entre 0 e 1."
        )

    return parsed


def _non_negative_int_argument(
    value: str,
) -> int:
    try:
        parsed = int(value)
    except ValueError as exception:
        raise argparse.ArgumentTypeError(
            "O valor precisa ser inteiro."
        ) from exception

    if parsed < 0:
        raise argparse.ArgumentTypeError(
            "O valor não pode ser negativo."
        )

    return parsed


def _non_negative_float_argument(
    value: str,
) -> float:
    try:
        parsed = float(value)
    except ValueError as exception:
        raise argparse.ArgumentTypeError(
            "O valor precisa ser numérico."
        ) from exception

    if parsed < 0:
        raise argparse.ArgumentTypeError(
            "O valor não pode ser negativo."
        )

    return parsed


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CliRunResult",
    "EvaluationCliExitCode",
    "build_cli_summary",
    "build_parser",
    "main",
    "render_text_summary",
    "run_official_command",
]