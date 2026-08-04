from __future__ import annotations

import dataclasses
import enum
import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

PayloadBuilder = Callable[..., Any]
RunnerFactory = Callable[[], Any]
ComparisonFunction = Callable[..., Any]
QualityGateFunction = Callable[..., Any]


_AXIS_ALIASES = {
    "answer_relevancy": "answer_relevancy",
    "answer_relevance": "answer_relevancy",
    "answerrelevancy": "answer_relevancy",
    "faithfulness": "faithfulness",
    "groundedness": "faithfulness",
    "contextual_relevancy": "contextual_relevancy",
    "contextual_relevance": "contextual_relevancy",
    "context_relevancy": "contextual_relevancy",
    "context_relevance": "contextual_relevancy",
}


@dataclass(frozen=True)
class TriadVariantInput:
    """
    Entrada de uma variante submetida à RAG Triad real.
    """

    actual_output: str

    context: tuple[str, ...] = ()
    retrieval_context: tuple[str, ...] = ()

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class TriadVariantEvaluation:
    """
    Resultado da avaliação DeepEval de uma variante.
    """

    name: str
    evaluation_run: Any
    rag_triad: Mapping[str, Any] | None


@dataclass(frozen=True)
class RetrievalABTriadEvaluation:
    """
    Comparação completa entre baseline e Sentence-Window.
    """

    schema_version: int

    generated_at: str

    baseline: TriadVariantEvaluation
    candidate: TriadVariantEvaluation

    axis_scores: Mapping[
        str,
        Mapping[str, float | None],
    ]

    axis_deltas: Mapping[
        str,
        float | None,
    ]

    comparison: Any | None
    quality_gate: Any | None

    recommendation: str
    recommendation_reasons: tuple[str, ...]

    tolerance: float


def _normalize_text(
    value: object,
) -> str:
    return str(
        value or ""
    ).strip()


def _normalize_context(
    values: Sequence[object] | None,
) -> tuple[str, ...]:
    if not values:
        return ()

    normalized: list[str] = []

    for value in values:
        rendered = _normalize_text(
            value
        )

        if (
            rendered
            and rendered not in normalized
        ):
            normalized.append(
                rendered
            )

    return tuple(
        normalized
    )


def _normalize_variant(
    value: TriadVariantInput,
) -> TriadVariantInput:
    output = _normalize_text(
        value.actual_output
    )

    if len(output) < 2:
        raise ValueError(
            "actual_output precisa conter uma resposta válida."
        )

    return TriadVariantInput(
        actual_output=output,
        context=_normalize_context(
            value.context
        ),
        retrieval_context=_normalize_context(
            value.retrieval_context
        ),
        metadata=dict(
            value.metadata
        ),
    )


def _safe_external(
    value: Any,
) -> Any:
    """
    Converte contratos internos em estruturas JSON seguras.
    """

    if value is None:
        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    if isinstance(
        value,
        enum.Enum,
    ):
        return value.value

    if isinstance(
        value,
        (
            datetime,
            date,
        ),
    ):
        return value.isoformat()

    if isinstance(
        value,
        Path,
    ):
        return str(value)

    if isinstance(
        value,
        Mapping,
    ):
        return {
            str(key): _safe_external(
                item
            )
            for key, item in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
            frozenset,
        ),
    ):
        return [
            _safe_external(
                item
            )
            for item in value
        ]

    model_dump = getattr(
        value,
        "model_dump",
        None,
    )

    if callable(model_dump):
        return _safe_external(
            model_dump(
                mode="json"
            )
        )

    to_dict = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(to_dict):
        return _safe_external(
            to_dict()
        )

    if (
        dataclasses.is_dataclass(
            value
        )
        and not isinstance(
            value,
            type,
        )
    ):
        return {
            field_definition.name: (
                _safe_external(
                    getattr(
                        value,
                        field_definition.name,
                    )
                )
            )
            for field_definition
            in dataclasses.fields(
                value
            )
        }

    value_dict = getattr(
        value,
        "__dict__",
        None,
    )

    if isinstance(
        value_dict,
        dict,
    ):
        return _safe_external(
            {
                key: item
                for key, item in value_dict.items()
                if not key.startswith("_")
            }
        )

    return repr(value)


def _rag_triad_payload(
    evaluation_run: Any,
) -> Mapping[str, Any] | None:
    accessor = getattr(
        evaluation_run,
        "rag_triad_payload",
        None,
    )

    if callable(accessor):
        payload = accessor()
    else:
        payload = accessor

    if payload is None:
        return None

    external = _safe_external(
        payload
    )

    if isinstance(
        external,
        Mapping,
    ):
        return dict(external)

    return {
        "value": external,
    }


def _normalize_axis_name(
    value: object,
) -> str | None:
    rendered = re.sub(
        r"[^a-z0-9]+",
        "_",
        str(value or "").lower(),
    ).strip("_")

    compact = rendered.replace(
        "_",
        "",
    )

    return (
        _AXIS_ALIASES.get(
            rendered
        )
        or _AXIS_ALIASES.get(
            compact
        )
    )


def _safe_score(
    value: object,
) -> float | None:
    try:
        score = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return None

    if score != score:
        return None

    return score


def extract_rag_triad_axis_scores(
    payload: Mapping[str, Any] | None,
) -> dict[str, float | None]:
    """
    Extrai os três eixos sem depender de apenas um formato
    de serialização do contrato.
    """

    scores: dict[str, float | None] = {
        "answer_relevancy": None,
        "faithfulness": None,
        "contextual_relevancy": None,
    }

    if not payload:
        return scores

    def visit(
        value: Any,
        inherited_name: str | None = None,
    ) -> None:
        if isinstance(
            value,
            Mapping,
        ):
            possible_name = (
                value.get("metric_id")
                or value.get("axis")
                or value.get("name")
                or value.get("id")
                or inherited_name
            )

            normalized_name = (
                _normalize_axis_name(
                    possible_name
                )
            )

            if normalized_name:
                for score_key in (
                    "score",
                    "value",
                    "average_score",
                    "mean_score",
                ):
                    if score_key not in value:
                        continue

                    score = _safe_score(
                        value.get(
                            score_key
                        )
                    )

                    if score is not None:
                        scores[
                            normalized_name
                        ] = score
                        break

            for key, item in value.items():
                normalized_key = (
                    _normalize_axis_name(
                        key
                    )
                )

                if normalized_key:
                    direct_score = (
                        _safe_score(
                            item
                        )
                    )

                    if direct_score is not None:
                        scores[
                            normalized_key
                        ] = direct_score

                    visit(
                        item,
                        normalized_key,
                    )
                else:
                    visit(
                        item,
                        inherited_name,
                    )

        elif isinstance(
            value,
            (
                list,
                tuple,
            ),
        ):
            for item in value:
                visit(
                    item,
                    inherited_name,
                )

    visit(
        payload
    )

    return scores


def _triad_passed(
    payload: Mapping[str, Any] | None,
) -> bool | None:
    if not payload:
        return None

    direct_passed = payload.get(
        "passed"
    )

    if isinstance(
        direct_passed,
        bool,
    ):
        return direct_passed

    status = str(
        payload.get(
            "status",
            "",
        )
        or ""
    ).strip().lower()

    if status in {
        "passed",
        "pass",
        "approved",
        "success",
        "completed_passed",
    }:
        return True

    if status in {
        "failed",
        "fail",
        "rejected",
        "blocked",
        "error",
    }:
        return False

    return None


def _build_recommendation(
    *,
    baseline_payload: Mapping[str, Any] | None,
    candidate_payload: Mapping[str, Any] | None,
    baseline_scores: Mapping[str, float | None],
    candidate_scores: Mapping[str, float | None],
    tolerance: float,
) -> tuple[
    str,
    tuple[str, ...],
    dict[str, float | None],
]:
    deltas: dict[
        str,
        float | None,
    ] = {}

    reasons: list[str] = []

    missing_axes: list[str] = []
    regressed_axes: list[str] = []
    improved_axes: list[str] = []

    for axis_name in (
        "answer_relevancy",
        "faithfulness",
        "contextual_relevancy",
    ):
        baseline_score = baseline_scores.get(
            axis_name
        )

        candidate_score = candidate_scores.get(
            axis_name
        )

        if (
            baseline_score is None
            or candidate_score is None
        ):
            deltas[
                axis_name
            ] = None

            missing_axes.append(
                axis_name
            )

            continue

        delta = (
            candidate_score
            - baseline_score
        )

        deltas[
            axis_name
        ] = round(
            delta,
            6,
        )

        if delta < -tolerance:
            regressed_axes.append(
                axis_name
            )

        elif delta > tolerance:
            improved_axes.append(
                axis_name
            )

    candidate_passed = _triad_passed(
        candidate_payload
    )

    baseline_passed = _triad_passed(
        baseline_payload
    )

    if candidate_passed is False:
        reasons.append(
            "A RAG Triad da Variante B não foi aprovada."
        )

        return (
            "reject_sentence_window",
            tuple(reasons),
            deltas,
        )

    if regressed_axes:
        reasons.append(
            "Regressão superior à tolerância nos eixos: "
            + ", ".join(
                regressed_axes
            )
            + "."
        )

        return (
            "reject_sentence_window",
            tuple(reasons),
            deltas,
        )

    if missing_axes:
        reasons.append(
            "A avaliação não retornou todos os eixos: "
            + ", ".join(
                missing_axes
            )
            + "."
        )

        return (
            "manual_review",
            tuple(reasons),
            deltas,
        )

    if (
        candidate_passed is True
        and baseline_passed is not False
    ):
        if improved_axes:
            reasons.append(
                "A Variante B foi aprovada e melhorou: "
                + ", ".join(
                    improved_axes
                )
                + "."
            )
        else:
            reasons.append(
                "A Variante B foi aprovada sem regressão "
                "relevante nos três eixos."
            )

        return (
            "promote_sentence_window",
            tuple(reasons),
            deltas,
        )

    reasons.append(
        "As métricas foram calculadas, mas o status agregado "
        "não permite promoção automática."
    )

    return (
        "manual_review",
        tuple(reasons),
        deltas,
    )


def evaluate_retrieval_ab_with_rag_triad(
    *,
    case: Any,
    baseline: TriadVariantInput,
    candidate: TriadVariantInput,
    runner: Any | None = None,
    runner_settings: Any | None = None,
    quality_gate_thresholds: Any | None = None,
    external_run: bool = False,
    tolerance: float = 0.005,
    metadata: Mapping[str, Any] | None = None,
    payload_builder: PayloadBuilder | None = None,
    runner_factory: RunnerFactory | None = None,
    comparison_function: ComparisonFunction | None = None,
    quality_gate_function: QualityGateFunction | None = None,
) -> RetrievalABTriadEvaluation:
    """
    Executa as variantes A e B usando a infraestrutura real
    do DeepEval já existente na INNA.

    Nenhuma pontuação é fabricada manualmente.
    """

    if case is None:
        raise ValueError(
            "Um InnaEvaluationCase válido é obrigatório."
        )

    safe_tolerance = max(
        0.0,
        min(
            float(tolerance),
            1.0,
        ),
    )

    baseline_input = _normalize_variant(
        baseline
    )

    candidate_input = _normalize_variant(
        candidate
    )

    if payload_builder is None:
        from src.evaluation.deepeval_integration import (
            build_deepeval_payload,
        )

        payload_builder = (
            build_deepeval_payload
        )

    if runner is None:
        if runner_factory is None:
            from src.evaluation.deepeval_runner import (
                EvaluationRunner,
            )

            runner_factory = (
                EvaluationRunner
            )

        runner = runner_factory()

    shared_metadata = dict(
        metadata or {}
    )

    shared_metadata.update(
        {
            "experiment": (
                "retrieval_ab_sentence_window"
            ),
            "schema_version": 1,
        }
    )

    def execute_variant(
        *,
        name: str,
        variant: TriadVariantInput,
    ) -> TriadVariantEvaluation:
        variant_metadata = dict(
            shared_metadata
        )

        variant_metadata.update(
            dict(
                variant.metadata
            )
        )

        variant_metadata[
            "retrieval_variant"
        ] = name

        payload = payload_builder(
            case,
            actual_output=(
                variant.actual_output
            ),
            context=variant.context,
            retrieval_context=(
                variant.retrieval_context
            ),
            metadata=variant_metadata,
            external_run=external_run,
        )

        evaluation_run = runner.run(
            case,
            payload,
            settings=runner_settings,
            metadata=variant_metadata,
        )

        return TriadVariantEvaluation(
            name=name,
            evaluation_run=(
                evaluation_run
            ),
            rag_triad=_rag_triad_payload(
                evaluation_run
            ),
        )

    baseline_evaluation = execute_variant(
        name="hybrid_baseline",
        variant=baseline_input,
    )

    candidate_evaluation = execute_variant(
        name="hybrid_sentence_window",
        variant=candidate_input,
    )

    if comparison_function is None:
        from src.evaluation.rag_lab_comparison import (
            compare_rag_triad_entries,
        )

        comparison_function = (
            compare_rag_triad_entries
        )

    try:
        comparison = comparison_function(
            baseline_evaluation.evaluation_run,
            candidate_evaluation.evaluation_run,
            tolerance=safe_tolerance,
        )
    except Exception as exc:
        comparison = {
            "status": "comparison_failed",
            "error_type": (
                type(exc).__name__
            ),
            "error_message": str(
                exc
            )[:500],
        }

    quality_gate = None

    if quality_gate_thresholds is not None:
        if quality_gate_function is None:
            from src.evaluation.rag_lab_advanced import (
                evaluate_quality_gate,
            )

            quality_gate_function = (
                evaluate_quality_gate
            )

        try:
            quality_gate = quality_gate_function(
                candidate_evaluation.evaluation_run,
                thresholds=(
                    quality_gate_thresholds
                ),
                baseline_entry=(
                    baseline_evaluation
                    .evaluation_run
                ),
            )
        except Exception as exc:
            quality_gate = {
                "status": "quality_gate_failed",
                "error_type": (
                    type(exc).__name__
                ),
                "error_message": str(
                    exc
                )[:500],
            }

    baseline_scores = (
        extract_rag_triad_axis_scores(
            baseline_evaluation.rag_triad
        )
    )

    candidate_scores = (
        extract_rag_triad_axis_scores(
            candidate_evaluation.rag_triad
        )
    )

    (
        recommendation,
        recommendation_reasons,
        axis_deltas,
    ) = _build_recommendation(
        baseline_payload=(
            baseline_evaluation.rag_triad
        ),
        candidate_payload=(
            candidate_evaluation.rag_triad
        ),
        baseline_scores=baseline_scores,
        candidate_scores=candidate_scores,
        tolerance=safe_tolerance,
    )

    return RetrievalABTriadEvaluation(
        schema_version=1,
        generated_at=datetime.now(
            UTC
        ).isoformat(),
        baseline=baseline_evaluation,
        candidate=candidate_evaluation,
        axis_scores={
            "hybrid_baseline": (
                baseline_scores
            ),
            "hybrid_sentence_window": (
                candidate_scores
            ),
        },
        axis_deltas=axis_deltas,
        comparison=comparison,
        quality_gate=quality_gate,
        recommendation=recommendation,
        recommendation_reasons=(
            recommendation_reasons
        ),
        tolerance=safe_tolerance,
    )


def build_retrieval_ab_triad_report_payload(
    result: RetrievalABTriadEvaluation,
) -> dict[str, Any]:
    """
    Gera relatório sem armazenar respostas ou contextos brutos.
    """

    baseline_run = _safe_external(
        result.baseline.evaluation_run
    )

    candidate_run = _safe_external(
        result.candidate.evaluation_run
    )

    return {
        "schema_version": (
            result.schema_version
        ),
        "generated_at": (
            result.generated_at
        ),
        "experiment": (
            "retrieval_ab_sentence_window"
        ),
        "baseline": {
            "name": (
                result.baseline.name
            ),
            "rag_triad": (
                _safe_external(
                    result.baseline.rag_triad
                )
            ),
            "evaluation_run": (
                baseline_run
            ),
        },
        "candidate": {
            "name": (
                result.candidate.name
            ),
            "rag_triad": (
                _safe_external(
                    result.candidate.rag_triad
                )
            ),
            "evaluation_run": (
                candidate_run
            ),
        },
        "axis_scores": (
            _safe_external(
                result.axis_scores
            )
        ),
        "axis_deltas": (
            _safe_external(
                result.axis_deltas
            )
        ),
        "comparison": (
            _safe_external(
                result.comparison
            )
        ),
        "quality_gate": (
            _safe_external(
                result.quality_gate
            )
        ),
        "recommendation": (
            result.recommendation
        ),
        "recommendation_reasons": list(
            result.recommendation_reasons
        ),
        "tolerance": (
            result.tolerance
        ),
        "privacy": {
            "actual_outputs_stored": False,
            "retrieval_contexts_stored": False,
        },
    }


def _safe_label(
    value: object,
) -> str:
    rendered = re.sub(
        r"[^A-Za-z0-9_-]+",
        "-",
        str(value or ""),
    ).strip("-")

    return rendered or "retrieval-ab-triad"


def _markdown_report(
    payload: Mapping[str, Any],
) -> str:
    axis_scores = payload[
        "axis_scores"
    ]

    axis_deltas = payload[
        "axis_deltas"
    ]

    lines = [
        "# Comparação A/B com RAG Triad",
        "",
        f"- Gerado em: `{payload['generated_at']}`",
        (
            "- Recomendação: `"
            + str(
                payload[
                    "recommendation"
                ]
            )
            + "`"
        ),
        f"- Tolerância: `{payload['tolerance']}`",
        "",
        "## Métricas",
        "",
        "| Eixo | RAG atual | Sentence-Window | Diferença |",
        "|---|---:|---:|---:|",
    ]

    baseline = axis_scores[
        "hybrid_baseline"
    ]

    candidate = axis_scores[
        "hybrid_sentence_window"
    ]

    for axis_name in (
        "answer_relevancy",
        "faithfulness",
        "contextual_relevancy",
    ):
        baseline_score = baseline.get(
            axis_name
        )

        candidate_score = candidate.get(
            axis_name
        )

        delta = axis_deltas.get(
            axis_name
        )

        lines.append(
            "| `"
            + axis_name
            + "` | "
            + (
                f"{baseline_score:.4f}"
                if baseline_score is not None
                else "-"
            )
            + " | "
            + (
                f"{candidate_score:.4f}"
                if candidate_score is not None
                else "-"
            )
            + " | "
            + (
                f"{delta:+.4f}"
                if delta is not None
                else "-"
            )
            + " |"
        )

    lines.extend(
        (
            "",
            "## Motivos da recomendação",
            "",
        )
    )

    for reason in payload[
        "recommendation_reasons"
    ]:
        lines.append(
            "- " + str(reason)
        )

    lines.extend(
        (
            "",
            "## Privacidade",
            "",
            "- Respostas completas não são salvas neste relatório.",
            "- Contextos recuperados completos não são salvos.",
            "- Os resultados e metadados da avaliação são preservados.",
            "",
        )
    )

    return "\n".join(
        lines
    )


def write_retrieval_ab_triad_report(
    result: RetrievalABTriadEvaluation,
    *,
    output_directory: str | Path,
    run_label: str = "week3-retrieval-ab-triad",
) -> dict[str, str]:
    output_path = Path(
        output_directory
    )

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = (
        build_retrieval_ab_triad_report_payload(
            result
        )
    )

    timestamp = datetime.now(
        UTC
    ).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    digest_source = json.dumps(
        {
            "generated_at": (
                payload[
                    "generated_at"
                ]
            ),
            "recommendation": (
                payload[
                    "recommendation"
                ]
            ),
            "axis_scores": (
                payload[
                    "axis_scores"
                ]
            ),
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    digest = hashlib.sha256(
        digest_source.encode(
            "utf-8"
        )
    ).hexdigest()[:12]

    run_id = (
        _safe_label(
            run_label
        )
        + "-"
        + timestamp
        + "-"
        + digest
    )

    payload[
        "run_id"
    ] = run_id

    json_path = (
        output_path
        / f"{run_id}.json"
    )

    markdown_path = (
        output_path
        / f"{run_id}.md"
    )

    history_path = (
        output_path
        / "history.jsonl"
    )

    json_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    markdown_path.write_text(
        _markdown_report(
            payload
        ),
        encoding="utf-8",
    )

    history_record = {
        "run_id": run_id,
        "generated_at": (
            payload[
                "generated_at"
            ]
        ),
        "recommendation": (
            payload[
                "recommendation"
            ]
        ),
        "axis_deltas": (
            payload[
                "axis_deltas"
            ]
        ),
        "json_report": str(
            json_path
        ),
        "markdown_report": str(
            markdown_path
        ),
    }

    with history_path.open(
        "a",
        encoding="utf-8",
    ) as history_file:
        history_file.write(
            json.dumps(
                history_record,
                ensure_ascii=False,
            )
            + "\n"
        )

    return {
        "run_id": run_id,
        "json_path": str(
            json_path
        ),
        "markdown_path": str(
            markdown_path
        ),
        "history_path": str(
            history_path
        ),
    }
