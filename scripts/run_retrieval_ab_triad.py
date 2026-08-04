from __future__ import annotations

import argparse
import importlib
import inspect
import json
from pathlib import Path
from typing import Any

from src.evaluation.retrieval_ab_triad import (
    TriadVariantInput,
    evaluate_retrieval_ab_with_rag_triad,
    write_retrieval_ab_triad_report,
)


def _load_callable(
    specification: str,
):
    module_name, separator, attribute_name = (
        specification.partition(
            ":"
        )
    )

    if not separator:
        raise ValueError(
            "Use o formato modulo:funcao."
        )

    module = importlib.import_module(
        module_name
    )

    value = getattr(
        module,
        attribute_name,
    )

    if not callable(value):
        raise TypeError(
            f"{specification} não é chamável."
        )

    return value


def _call_provider(
    provider,
    *,
    case_id: str,
) -> Any:
    signature = inspect.signature(
        provider
    )

    required_parameters = [
        parameter
        for parameter in (
            signature.parameters.values()
        )
        if (
            parameter.default
            is inspect.Signature.empty
            and parameter.kind
            not in {
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            }
        )
    ]

    if not required_parameters:
        provided = provider()
    else:
        provided = provider(
            case_id
        )

    if isinstance(
        provided,
        dict,
    ):
        if case_id not in provided:
            raise KeyError(
                f"Caso não encontrado: {case_id}"
            )

        return provided[
            case_id
        ]

    return provided


def _variant_from_payload(
    payload: dict[str, Any],
    field_name: str,
) -> TriadVariantInput:
    value = payload.get(
        field_name
    )

    if not isinstance(
        value,
        dict,
    ):
        raise ValueError(
            f"Campo obrigatório ausente: {field_name}"
        )

    return TriadVariantInput(
        actual_output=str(
            value.get(
                "actual_output",
                "",
            )
        ),
        context=tuple(
            value.get(
                "context",
                [],
            )
            or []
        ),
        retrieval_context=tuple(
            value.get(
                "retrieval_context",
                [],
            )
            or []
        ),
        metadata=dict(
            value.get(
                "metadata",
                {},
            )
            or {}
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Executa comparação A/B com a RAG Triad "
            "real da INNA."
        )
    )

    parser.add_argument(
        "--input-json",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--case-provider",
        required=True,
        help=(
            "Função que fornece o InnaEvaluationCase. "
            "Formato: modulo:funcao"
        ),
    )

    parser.add_argument(
        "--case-id",
        required=True,
    )

    parser.add_argument(
        "--runner-settings-provider",
        help=(
            "Fornecedor opcional de EvaluationRunnerSettings."
        ),
    )

    parser.add_argument(
        "--quality-thresholds-provider",
        help=(
            "Fornecedor opcional de QualityGateThresholds."
        ),
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "artifacts/evaluation/retrieval_ab_triad"
        ),
    )

    parser.add_argument(
        "--label",
        default="week3-retrieval-ab-triad",
    )

    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.005,
    )

    parser.add_argument(
        "--external-run",
        action="store_true",
    )

    args = parser.parse_args()

    input_payload = json.loads(
        args.input_json.read_text(
            encoding="utf-8",
        )
    )

    case_provider = _load_callable(
        args.case_provider
    )

    case = _call_provider(
        case_provider,
        case_id=args.case_id,
    )

    runner_settings = None

    if args.runner_settings_provider:
        provider = _load_callable(
            args.runner_settings_provider
        )

        runner_settings = _call_provider(
            provider,
            case_id=args.case_id,
        )

    thresholds = None

    if args.quality_thresholds_provider:
        provider = _load_callable(
            args.quality_thresholds_provider
        )

        thresholds = _call_provider(
            provider,
            case_id=args.case_id,
        )

    result = evaluate_retrieval_ab_with_rag_triad(
        case=case,
        baseline=_variant_from_payload(
            input_payload,
            "baseline",
        ),
        candidate=_variant_from_payload(
            input_payload,
            "candidate",
        ),
        runner_settings=runner_settings,
        quality_gate_thresholds=thresholds,
        external_run=args.external_run,
        tolerance=args.tolerance,
        metadata={
            "case_id": args.case_id,
            "input_file": str(
                args.input_json
            ),
        },
    )

    reports = write_retrieval_ab_triad_report(
        result,
        output_directory=args.output_dir,
        run_label=args.label,
    )

    print(
        "RUN_ID="
        + reports["run_id"]
    )

    print(
        "RECOMMENDATION="
        + result.recommendation
    )

    for reason in result.recommendation_reasons:
        print(
            "RECOMMENDATION_REASON="
            + reason
        )

    for axis_name, delta in (
        result.axis_deltas.items()
    ):
        print(
            "AXIS_DELTA_"
            + axis_name.upper()
            + "="
            + str(delta)
        )

    print(
        "JSON_REPORT="
        + reports["json_path"]
    )

    print(
        "MARKDOWN_REPORT="
        + reports["markdown_path"]
    )

    print(
        "HISTORY="
        + reports["history_path"]
    )

    print(
        "WEEK3_RETRIEVAL_AB_TRIAD_RUN=OK"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
