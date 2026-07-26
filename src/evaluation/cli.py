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
from src.evaluation.datasets import (
    EvaluationDataset,
    build_dataset,
)
from src.evaluation.deepeval_runner import (
    EvaluationRunMode,
    EvaluationRunnerSettings,
)
from src.evaluation.deterministic_executors import (
    build_deterministic_runner,
)
from src.evaluation.live_payload_provider import (
    LiveInnaPayloadProvider,
)
from src.evaluation.payload_providers import (
    EvaluationPayloadProvider,
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

    command: str = "run-official"

    execution_type: str = (
        "synthetic-infrastructure-validation"
    )

    production_evaluation: bool = False

    case_id: str | None = None

    @property
    def passed(self) -> bool:
        return self.quality_gate.passed


def _add_report_arguments(
    parser: argparse.ArgumentParser,
    *,
    output_directory: str,
    internal_output_directory: str,
) -> None:
    parser.add_argument(
        "--output-directory",
        default=output_directory,
        help=(
            "Diretório do relatório externo "
            "sanitizado."
        ),
    )

    parser.add_argument(
        "--internal-output-directory",
        default=internal_output_directory,
        help=(
            "Diretório do relatório interno "
            "completo."
        ),
    )

    parser.add_argument(
        "--write-internal-report",
        action="store_true",
        help=(
            "Também grava o relatório interno "
            "completo. Esse arquivo não deve "
            "ser exportado."
        ),
    )

    parser.add_argument(
        "--summary-only",
        action="store_true",
        help=(
            "Remove os detalhes dos casos "
            "do relatório."
        ),
    )

    parser.add_argument(
        "--no-report",
        action="store_true",
        help=(
            "Executa o lote e o quality gate "
            "sem gravar relatório."
        ),
    )


def _add_quality_gate_arguments(
    parser: argparse.ArgumentParser,
) -> None:
    parser.add_argument(
        "--minimum-pass-rate",
        type=_rate_argument,
        default=1.0,
        help=(
            "Taxa mínima de aprovação entre "
            "0 e 1. Padrão: 1.0."
        ),
    )

    parser.add_argument(
        "--maximum-failed-cases",
        type=_non_negative_int_argument,
        default=0,
    )

    parser.add_argument(
        "--maximum-blocked-cases",
        type=_non_negative_int_argument,
        default=0,
    )

    parser.add_argument(
        "--maximum-error-cases",
        type=_non_negative_int_argument,
        default=0,
    )

    parser.add_argument(
        "--maximum-total-cost",
        type=_non_negative_float_argument,
        default=0.0,
    )

    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
    )


def _add_output_arguments(
    parser: argparse.ArgumentParser,
) -> None:
    parser.add_argument(
        "--json-output",
        action="store_true",
        help=(
            "Imprime o resumo da execução "
            "em JSON."
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inna-evaluation",
        description=(
            "CLI oficial para execução local das "
            "avaliações LLMOps da INNA."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    official_parser = subparsers.add_parser(
        "run-official",
        help=(
            "Executa os datasets oficiais usando "
            "o provedor sintético de infraestrutura."
        ),
    )

    _add_report_arguments(
        official_parser,
        output_directory=(
            "artifacts/evaluations"
        ),
        internal_output_directory=(
            "artifacts/evaluations/internal"
        ),
    )

    _add_quality_gate_arguments(
        official_parser
    )

    official_parser.add_argument(
        "--require-production-execution",
        action="store_true",
        help=(
            "Exige execução real da aplicação. "
            "Como run-official utiliza payload "
            "sintético, o gate será reprovado "
            "quando essa opção for usada."
        ),
    )

    _add_output_arguments(
        official_parser
    )

    live_parser = subparsers.add_parser(
        "run-live",
        help=(
            "Executa um caso oficial usando "
            "o grafo real da aplicação INNA."
        ),
    )

    live_parser.add_argument(
        "--case-id",
        required=True,
        help=(
            "Identificador do caso oficial que "
            "será executado pela aplicação real."
        ),
    )

    live_parser.add_argument(
        "--gate-profile",
        choices=(
            "single-case",
            "release",
        ),
        default="single-case",
        help=(
            "Perfil do Quality Gate. "
            "'single-case' valida somente o caso "
            "e o dataset selecionados. "
            "'release' exige todos os datasets "
            "e métricas críticas oficiais."
        ),
    )

    _add_report_arguments(
        live_parser,
        output_directory=(
            "artifacts/evaluations/live"
        ),
        internal_output_directory=(
            "artifacts/evaluations/live/internal"
        ),
    )

    _add_quality_gate_arguments(
        live_parser
    )

    _add_output_arguments(
        live_parser
    )

    return parser


def _build_quality_gate_settings(
    args: argparse.Namespace,
    *,
    require_production_execution: bool,
) -> QualityGateSettings:
    return QualityGateSettings(
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
            require_production_execution
        ),
        fail_on_warning=args.fail_on_warning,
    )


def _write_reports(
    *,
    args: argparse.Namespace,
    batch: BatchRunResult,
    gate: QualityGateResult,
    internal_filename: str,
) -> tuple[
    Path | None,
    Path | None,
]:
    external_report: Path | None = None
    internal_report: Path | None = None

    if args.no_report:
        return (
            external_report,
            internal_report,
        )

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
            filename=internal_filename,
        )

    return (
        external_report,
        internal_report,
    )


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
            "production_execution": False,
            "official_case_count": (
                official_case_count()
            ),
            "cli_command": "run-official",
        },
    )

    gate = evaluate_quality_gate(
        batch,
        _build_quality_gate_settings(
            args,
            require_production_execution=(
                args.require_production_execution
            ),
        ),
    )

    (
        external_report,
        internal_report,
    ) = _write_reports(
        args=args,
        batch=batch,
        gate=gate,
        internal_filename=(
            "inna-evaluation-internal-complete"
        ),
    )

    return CliRunResult(
        batch=batch,
        quality_gate=gate,
        external_report=external_report,
        internal_report=internal_report,
        command="run-official",
        execution_type=(
            "synthetic-infrastructure-validation"
        ),
        production_evaluation=False,
        case_id=None,
    )


def _select_live_dataset(
    case_id: str,
) -> EvaluationDataset:
    normalized_case_id = case_id.strip()

    if not normalized_case_id:
        raise ValueError(
            "case_id não pode ser vazio."
        )

    for dataset in official_datasets():
        if normalized_case_id not in (
            dataset.case_ids
        ):
            continue

        case = dataset.get_case(
            normalized_case_id
        )

        return build_dataset(
            name=dataset.name,
            version=dataset.version,
            cases=(case,),
            description=(
                "Seleção oficial para avaliação "
                "real da INNA."
            ),
            owner=dataset.owner,
            tags=(
                *dataset.tags,
                "live-evaluation",
            ),
            metadata={
                **dict(dataset.metadata),
                "live_selection": True,
                "selected_case_id": (
                    normalized_case_id
                ),
                "production_execution": True,
            },
        )

    raise ValueError(
        "Caso oficial não encontrado: "
        f"{normalized_case_id}"
    )


def run_live_command(
    args: argparse.Namespace,
    *,
    provider: (
        EvaluationPayloadProvider | None
    ) = None,
) -> CliRunResult:
    normalized_case_id = (
        args.case_id.strip()
    )

    selected_dataset = (
        _select_live_dataset(
            normalized_case_id
        )
    )

    resolved_provider = (
        provider
        if provider is not None
        else LiveInnaPayloadProvider()
    )

    batch_runner = EvaluationBatchRunner(
        runner=build_deterministic_runner(),
        payload_provider=resolved_provider,
    )

    batch = batch_runner.run(
        (selected_dataset,),
        runner_settings=EvaluationRunnerSettings(
            mode=EvaluationRunMode.LOCAL,
        ),
        continue_on_case_error=False,
        metadata={
            "execution_type": (
                "live-application-evaluation"
            ),
            "provider": (
                type(
                    resolved_provider
                ).__name__
            ),
            "production_evaluation": True,
            "production_execution": True,
            "selected_case_id": (
                normalized_case_id
            ),
            "gate_profile": (
                args.gate_profile
            ),
            "cli_command": "run-live",
        },
    )

    if args.gate_profile == "single-case":
        critical_metric_ids = tuple(
            summary.metric_id
            for summary in batch.metric_summaries
        )

        required_dataset_ids = tuple(
            summary.dataset_id
            for summary in batch.dataset_summaries
        )
    else:
        default_gate_settings = (
            QualityGateSettings()
        )

        critical_metric_ids = (
            default_gate_settings
            .critical_metric_ids
        )

        required_dataset_ids = (
            default_gate_settings
            .required_dataset_ids
        )

    gate = evaluate_quality_gate(
        batch,
        QualityGateSettings(
            minimum_pass_rate=(
                args.minimum_pass_rate
            ),
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
            critical_metric_ids=(
                critical_metric_ids
            ),
            required_dataset_ids=(
                required_dataset_ids
            ),
            require_production_execution=True,
            fail_on_warning=args.fail_on_warning,
        ),
    )

    (
        external_report,
        internal_report,
    ) = _write_reports(
        args=args,
        batch=batch,
        gate=gate,
        internal_filename=(
            "inna-live-evaluation-"
            "internal-complete"
        ),
    )

    return CliRunResult(
        batch=batch,
        quality_gate=gate,
        external_report=external_report,
        internal_report=internal_report,
        command="run-live",
        execution_type=(
            "live-application-evaluation"
        ),
        production_evaluation=True,
        case_id=normalized_case_id,
    )


def build_cli_summary(
    result: CliRunResult,
) -> dict[str, Any]:
    batch = result.batch
    gate = result.quality_gate

    return {
        "command": result.command,
        "execution_type": (
            result.execution_type
        ),
        "production_evaluation": (
            result.production_evaluation
        ),
        "case_id": result.case_id,
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


def _format_percentage_pt_br(
    value: float,
) -> str:
    return (
        f"{value:.2%}"
        .replace(".", ",")
    )


def render_text_summary(
    result: CliRunResult,
) -> str:
    batch = result.batch
    gate = result.quality_gate

    if result.production_evaluation:
        title = (
            "INNA LLMOps — Avaliação Real"
        )
        execution_label = "aplicação real"
        production_label = "sim"
    else:
        title = (
            "INNA LLMOps — Avaliação Oficial"
        )
        execution_label = (
            "validação sintética da "
            "infraestrutura"
        )
        production_label = "não"

    lines = [
        title,
        "=" * 42,
        (
            "Tipo de execução: "
            f"{execution_label}"
        ),
        (
            "Execução de produção: "
            f"{production_label}"
        ),
    ]

    if result.case_id:
        lines.append(
            f"Caso: {result.case_id}"
        )

    lines.extend(
        (
            f"Batch ID: {batch.batch_id}",
            (
                "Status do lote: "
                f"{batch.status.value}"
            ),
            (
                "Casos totais: "
                f"{batch.total_cases}"
            ),
            (
                "Casos aprovados: "
                f"{batch.passed_cases}"
            ),
            (
                "Casos reprovados: "
                f"{batch.failed_cases}"
            ),
            (
                "Casos bloqueados: "
                f"{batch.blocked_cases}"
            ),
            (
                "Casos com erro: "
                f"{batch.error_cases}"
            ),
            (
                "Taxa de aprovação: "
                f"{_format_percentage_pt_br(batch.pass_rate)}"
            ),
            (
                "Custo estimado: "
                f"US$ {batch.total_estimated_cost:.6f}"
            ),
            (
                "Quality Gate: "
                f"{'APROVADO' if gate.passed else 'REPROVADO'}"
            ),
        )
    )

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
        if args.command == "run-official":
            result = run_official_command(
                args
            )
        elif args.command == "run-live":
            result = run_live_command(
                args
            )
        else:
            parser.error(
                "Comando não suportado: "
                f"{args.command}"
            )

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
                render_text_summary(
                    result
                )
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
        KeyError,
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
            "Erro ao gravar relatório: "
            f"{error}",
            file=sys.stderr,
        )

        return int(
            EvaluationCliExitCode
            .REPORT_ERROR
        )

    except Exception as error:
        print(
            "Erro inesperado durante a avaliação: "
            f"{type(error).__name__}: {error}",
            file=sys.stderr,
        )

        return int(
            EvaluationCliExitCode
            .EXECUTION_ERROR
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
            "A taxa precisa estar entre "
            "0 e 1."
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
    "run_live_command",
    "run_official_command",
]
