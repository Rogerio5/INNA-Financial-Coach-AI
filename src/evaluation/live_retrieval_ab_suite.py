from __future__ import annotations

import dataclasses
import enum
import hashlib
import json
import os
import statistics
from collections.abc import Callable, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from time import perf_counter
from typing import Any


@dataclass(frozen=True)
class LiveVariantExecution:
    """
    Resultado mantido em memória de uma variante do RAG.

    answer e retrieval_context nunca entram no relatório
    consolidado.
    """

    name: str
    sentence_window_enabled: bool

    answer: str
    retrieval_context: tuple[str, ...]

    mode: str
    duration_ms: float

    source_count: int
    retrieved_documents: int


@dataclass(frozen=True)
class LiveSuiteConfiguration:
    top_k: int = 4
    language: str = "pt"

    tolerance: float = 0.005

    maximum_total_cost_per_variant: float = 0.10

    maximum_median_latency_regression_ms: float = 1000.0

    fail_fast: bool = True


VariantExecutor = Callable[
    ...,
    LiveVariantExecution,
]

PairEvaluator = Callable[..., Any]
PairReportWriter = Callable[..., Mapping[str, str]]


def _sha256(
    value: str,
) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _safe_external(
    value: Any,
) -> Any:
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
        return {str(key): _safe_external(item) for key, item in value.items()}

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
            frozenset,
        ),
    ):
        return [_safe_external(item) for item in value]

    model_dump = getattr(
        value,
        "model_dump",
        None,
    )

    if callable(model_dump):
        return _safe_external(model_dump(mode="json"))

    if dataclasses.is_dataclass(value) and not isinstance(
        value,
        type,
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
            for field_definition in dataclasses.fields(value)
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
            {key: item for key, item in value_dict.items() if not key.startswith("_")}
        )

    return repr(value)


@contextmanager
def temporary_environment(
    updates: Mapping[str, str],
):
    """
    Aplica variáveis somente durante uma execução e depois
    restaura exatamente o estado anterior.
    """

    missing = object()

    previous: dict[
        str,
        object,
    ] = {}

    for name, value in updates.items():
        previous[name] = os.environ.get(
            name,
            missing,
        )

        os.environ[name] = str(value)

    try:
        yield

    finally:
        for name, previous_value in previous.items():
            if previous_value is missing:
                os.environ.pop(
                    name,
                    None,
                )

            else:
                os.environ[name] = str(previous_value)


def _resolve_enum_member(
    enum_type: type[enum.Enum],
    preferred_values: Sequence[str],
) -> enum.Enum:
    preferred = {str(value).strip().lower() for value in preferred_values}

    for member in enum_type:
        tokens = {
            str(member.name).strip().lower(),
            str(member.value).strip().lower(),
        }

        if tokens & preferred:
            return member

    available = ", ".join(
        (str(member.name) + "=" + str(member.value)) for member in enum_type
    )

    raise RuntimeError(f"Valor de enum não localizado. Disponíveis: {available}")


def _public_privacy_level():
    from src.evaluation.contracts import (
        PrivacyLevel,
    )

    preferred = (
        "public",
        "external",
        "internal",
    )

    try:
        return _resolve_enum_member(
            PrivacyLevel,
            preferred,
        )

    except RuntimeError:
        return next(iter(PrivacyLevel))


def build_live_evaluation_case(
    *,
    question: str,
    index: int,
):
    """
    Cria um caso próprio para avaliação externa.

    As perguntas utilizadas são genéricas e educacionais.
    """

    from src.evaluation.contracts import (
        InnaEvaluationCase,
    )

    rendered_question = str(question or "").strip()

    if len(rendered_question) < 3:
        raise ValueError("Pergunta inválida.")

    question_digest = _sha256(rendered_question)[:12]

    return InnaEvaluationCase(
        case_id=(f"week3-live-rag-ab-{index:03d}-{question_digest}"),
        input_text=rendered_question,
        case_version="1.0.0",
        dataset_name=("week3-live-rag-ab"),
        dataset_version="1.0.0",
        description=(
            "Comparação real entre o RAG híbrido atual e Sentence-Window Retrieval."
        ),
        category=("rag"),
        tags=(
            "week3",
            "rag",
            "sentence-window",
            "ab-test",
            "live-evaluation",
        ),
        language="pt",
        currency="BRL",
        privacy_level=(_public_privacy_level()),
        external_evaluation_allowed=True,
        minimum_retrieved_documents=1,
        metadata={
            "experiment": ("week3_live_retrieval_ab"),
            "question_sha256": (_sha256(rendered_question)),
            "question_index": index,
            "raw_outputs_persisted": False,
            "raw_contexts_persisted": False,
            "synthetic": True,
            "external_safe": True,
        },
    )


def execute_rag_variant(
    *,
    question: str,
    language: str,
    top_k: int,
    sentence_window_enabled: bool,
) -> LiveVariantExecution:
    """
    Executa a ferramenta RAG real da INNA.

    O feature flag é temporário e restaurado após a chamada.
    """

    from src.agent_tools.rag_tools import (
        consultar_rag_inna,
    )

    variant_name = (
        "hybrid_sentence_window" if sentence_window_enabled else "hybrid_baseline"
    )

    started_at = perf_counter()

    with temporary_environment(
        {
            "INNA_RAG_SENTENCE_WINDOW_ENABLED": (
                "true" if sentence_window_enabled else "false"
            )
        }
    ):
        result = consultar_rag_inna(
            pergunta=question,
            idioma=language,
            top_k=top_k,
        )

    elapsed_ms = (perf_counter() - started_at) * 1000

    if not bool(
        getattr(
            result,
            "ok",
            False,
        )
    ):
        error_message = str(
            getattr(
                result,
                "error",
                "",
            )
            or "Falha controlada no RAG."
        )

        raise RuntimeError(variant_name + ": " + error_message)

    answer = str(
        getattr(
            result,
            "answer",
            "",
        )
        or ""
    ).strip()

    if not answer:
        raise RuntimeError(variant_name + " não retornou resposta.")

    raw_context = getattr(
        result,
        "retrieval_context",
        (),
    )

    retrieval_context = tuple(
        str(item).strip() for item in (raw_context or ()) if str(item).strip()
    )

    if not retrieval_context:
        raise RuntimeError(variant_name + " não retornou contexto recuperado.")

    sources = (
        getattr(
            result,
            "sources",
            (),
        )
        or ()
    )

    result_duration = getattr(
        result,
        "duration_ms",
        None,
    )

    try:
        normalized_duration = float(result_duration)
    except (
        TypeError,
        ValueError,
    ):
        normalized_duration = elapsed_ms

    return LiveVariantExecution(
        name=variant_name,
        sentence_window_enabled=(sentence_window_enabled),
        answer=answer,
        retrieval_context=(retrieval_context),
        mode=str(
            getattr(
                result,
                "mode",
                "",
            )
            or ""
        ),
        duration_ms=round(
            normalized_duration,
            3,
        ),
        source_count=len(sources),
        retrieved_documents=int(
            getattr(
                result,
                "retrieved_documents",
                len(retrieval_context),
            )
            or 0
        ),
    )


def safe_variant_payload(
    variant: LiveVariantExecution,
) -> dict[str, Any]:
    """
    Serialização segura: apenas hashes e medidas.
    """

    combined_context = "\n".join(variant.retrieval_context)

    return {
        "name": variant.name,
        "sentence_window_enabled": (variant.sentence_window_enabled),
        "mode": variant.mode,
        "duration_ms": (variant.duration_ms),
        "source_count": (variant.source_count),
        "retrieved_documents": (variant.retrieved_documents),
        "answer_characters": len(variant.answer),
        "answer_sha256": _sha256(variant.answer),
        "context_count": len(variant.retrieval_context),
        "context_characters": sum(len(item) for item in variant.retrieval_context),
        "context_sha256": _sha256(combined_context),
        "raw_answer_stored": False,
        "raw_context_stored": False,
    }


def _build_real_runner_bundle(
    *,
    maximum_total_cost: float,
):
    from src.evaluation.deepeval_integration import (
        DeepEvalSettings,
    )
    from src.evaluation.deepeval_live_executors import (
        build_default_deepeval_live_executors,
    )
    from src.evaluation.deepeval_metrics import (
        build_default_metric_registry,
    )
    from src.evaluation.deepeval_runner import (
        EvaluationRunMode,
        EvaluationRunner,
        EvaluationRunnerSettings,
    )
    from src.evaluation.deterministic_executors import (
        build_default_deterministic_executors,
    )
    from src.evaluation.rag_lab_advanced import (
        QualityGateThresholds,
    )

    live_mode = _resolve_enum_member(
        EvaluationRunMode,
        (
            "live",
            "live-run",
            "official",
            "full",
        ),
    )

    registry = build_default_metric_registry()

    profile = registry.profile_for_category("rag")

    required_triad_metrics = {
        "answer-relevancy",
        "faithfulness",
        "contextual-relevancy",
    }

    missing_profile_metrics = required_triad_metrics - set(profile.metric_ids)

    if missing_profile_metrics:
        raise RuntimeError(
            "O rag-profile não contém: " + ", ".join(sorted(missing_profile_metrics))
        )

    executors = dict(build_default_deterministic_executors())

    executors.update(dict(build_default_deepeval_live_executors()))

    missing_executors = set(profile.metric_ids) - set(executors)

    if missing_executors:
        raise RuntimeError(
            "Executores ausentes: " + ", ".join(sorted(missing_executors))
        )

    runner = EvaluationRunner(
        registry=registry,
        deepeval_settings=(
            DeepEvalSettings(
                enabled=True,
                live_enabled=True,
                external_only=True,
            )
        ),
        executors=executors,
    )

    settings = EvaluationRunnerSettings(
        mode=live_mode,
        continue_on_metric_error=True,
        include_live_metrics=True,
        external_run=True,
        maximum_total_cost=max(
            0.01,
            float(maximum_total_cost),
        ),
    )

    return (
        runner,
        settings,
        QualityGateThresholds(),
    )


def _gate_passed(
    value: Any,
) -> bool | None:
    external = _safe_external(value)

    def visit(
        current: Any,
    ) -> bool | None:
        if isinstance(
            current,
            Mapping,
        ):
            direct = current.get("passed")

            if isinstance(
                direct,
                bool,
            ):
                return direct

            status = (
                str(
                    current.get(
                        "status",
                        "",
                    )
                    or ""
                )
                .strip()
                .lower()
            )

            if status in {
                "passed",
                "pass",
                "approved",
                "success",
            }:
                return True

            if status in {
                "failed",
                "fail",
                "rejected",
                "blocked",
                "error",
                "quality_gate_failed",
            }:
                return False

            for item in current.values():
                nested = visit(item)

                if nested is not None:
                    return nested

        elif isinstance(
            current,
            list,
        ):
            results = [visit(item) for item in current]

            known = [item for item in results if item is not None]

            if False in known:
                return False

            if known and all(item is True for item in known):
                return True

        return None

    return visit(external)


def _estimated_cost(
    evaluation: Any,
) -> float:
    run = getattr(
        evaluation,
        "evaluation_run",
        None,
    )

    try:
        return float(
            getattr(
                run,
                "total_estimated_cost",
                0.0,
            )
            or 0.0
        )
    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def _quality_gate_from_axis_scores(
    *,
    axis_scores: Any,
    axis_deltas: Any,
    thresholds: Any,
) -> dict[str, Any]:
    """
    Calcula o Quality Gate diretamente dos scores A/B
    quando o gate retornado pela camada anterior estiver
    incompleto.
    """

    safe_scores = _safe_external(axis_scores)

    safe_deltas = _safe_external(axis_deltas)

    if not isinstance(
        safe_scores,
        Mapping,
    ):
        safe_scores = {}

    if not isinstance(
        safe_deltas,
        Mapping,
    ):
        safe_deltas = {}

    candidate = safe_scores.get(
        "hybrid_sentence_window",
        {},
    )

    if not isinstance(
        candidate,
        Mapping,
    ):
        candidate = {}

    metric_configuration = (
        (
            "answer-relevancy",
            "answer_relevancy",
            float(
                getattr(
                    thresholds,
                    "answer_relevancy",
                    0.7,
                )
            ),
        ),
        (
            "faithfulness",
            "faithfulness",
            float(
                getattr(
                    thresholds,
                    "faithfulness",
                    0.7,
                )
            ),
        ),
        (
            "contextual-relevancy",
            "contextual_relevancy",
            float(
                getattr(
                    thresholds,
                    "contextual_relevancy",
                    0.7,
                )
            ),
        ),
    )

    checks: list[dict[str, Any]] = []
    metric_scores: list[float] = []
    unavailable_keys: list[str] = []
    failed_keys: list[str] = []

    for (
        output_key,
        source_key,
        threshold,
    ) in metric_configuration:
        raw_score = candidate.get(source_key)

        try:
            score = float(raw_score)
        except (
            TypeError,
            ValueError,
        ):
            score = None

        if score is None:
            passed = None

            unavailable_keys.append(output_key)

            reason = "Score não registrado nesta execução."

        else:
            passed = score >= threshold

            metric_scores.append(score)

            if not passed:
                failed_keys.append(output_key)

            reason = "Score aprovado." if passed else "Score abaixo do limite."

        checks.append(
            {
                "key": output_key,
                "score": score,
                "threshold": threshold,
                "passed": passed,
                "reason": reason,
            }
        )

    aggregate_threshold = float(
        getattr(
            thresholds,
            "aggregate_score",
            0.7,
        )
    )

    aggregate_score = (
        sum(metric_scores) / len(metric_scores) if len(metric_scores) == 3 else None
    )

    aggregate_passed = (
        aggregate_score >= aggregate_threshold if aggregate_score is not None else None
    )

    if aggregate_passed is None:
        unavailable_keys.append("rag-triad-average")

        aggregate_reason = "Média indisponível por métricas ausentes."

    elif aggregate_passed:
        aggregate_reason = "Média da RAG Triad aprovada."

    else:
        failed_keys.append("rag-triad-average")

        aggregate_reason = "Média da RAG Triad abaixo do limite."

    checks.append(
        {
            "key": "rag-triad-average",
            "score": aggregate_score,
            "threshold": aggregate_threshold,
            "passed": aggregate_passed,
            "reason": aggregate_reason,
        }
    )

    maximum_regression = float(
        getattr(
            thresholds,
            "maximum_regression",
            0.05,
        )
    )

    regression_values: list[float] = []

    for source_key in (
        "answer_relevancy",
        "faithfulness",
        "contextual_relevancy",
    ):
        raw_delta = safe_deltas.get(source_key)

        try:
            regression_values.append(float(raw_delta))
        except (
            TypeError,
            ValueError,
        ):
            pass

    worst_delta = min(regression_values) if len(regression_values) == 3 else None

    regression_passed = (
        worst_delta >= -maximum_regression if worst_delta is not None else None
    )

    if regression_passed is None:
        unavailable_keys.append("maximum-regression")

        regression_reason = "Comparação de regressão indisponível."

    elif regression_passed:
        regression_reason = "Nenhuma regressão superou o limite."

    else:
        failed_keys.append("maximum-regression")

        regression_reason = "Ao menos uma regressão superou o limite."

    checks.append(
        {
            "key": "maximum-regression",
            "score": worst_delta,
            "threshold": maximum_regression,
            "passed": regression_passed,
            "reason": regression_reason,
        }
    )

    complete = not unavailable_keys

    passed = all(check.get("passed") is True for check in checks) if complete else None

    return {
        "run_reference": "axis_scores_fallback",
        "passed": passed,
        "complete": complete,
        "checks": checks,
        "failed_keys": failed_keys,
        "unavailable_keys": unavailable_keys,
    }


def _overall_recommendation(
    *,
    completed_cases: Sequence[Mapping[str, Any]],
    failed_case_count: int,
    maximum_median_latency_regression_ms: float,
) -> tuple[str, list[str]]:
    reasons: list[str] = []

    if failed_case_count:
        reasons.append("Existem casos que não concluíram a avaliação.")

        return (
            "manual_review",
            reasons,
        )

    recommendations = [
        str(
            item.get(
                "recommendation",
                "",
            )
        )
        for item in completed_cases
    ]

    gate_results = [item.get("quality_gate_passed") for item in completed_cases]

    if any(
        recommendation == "reject_sentence_window" for recommendation in recommendations
    ):
        reasons.append("Ao menos um caso apresentou regressão na RAG Triad.")

        return (
            "reject_sentence_window",
            reasons,
        )

    if False in gate_results:
        reasons.append("Ao menos um caso foi reprovado pelo Quality Gate.")

        return (
            "reject_sentence_window",
            reasons,
        )

    latency_deltas = [
        float(
            item.get(
                "latency_delta_ms",
                0.0,
            )
        )
        for item in completed_cases
    ]

    median_latency_delta = statistics.median(latency_deltas) if latency_deltas else 0.0

    if median_latency_delta > maximum_median_latency_regression_ms:
        reasons.append(
            "A mediana da regressão de latência superou o limite configurado."
        )

        return (
            "manual_review",
            reasons,
        )

    if None in gate_results:
        reasons.append(
            "O Quality Gate não retornou decisão completa para todos os casos."
        )

        return (
            "manual_review",
            reasons,
        )

    if all(
        recommendation == "promote_sentence_window"
        for recommendation in recommendations
    ):
        reasons.append(
            "Todos os casos foram aprovados sem regressão relevante na RAG Triad."
        )

        reasons.append("Todos os Quality Gates foram aprovados.")

        reasons.append("A regressão mediana de latência permaneceu dentro do limite.")

        return (
            "promote_sentence_window",
            reasons,
        )

    reasons.append("Os resultados não permitem promoção automática.")

    return (
        "manual_review",
        reasons,
    )


def _markdown_report(
    payload: Mapping[str, Any],
) -> str:
    lines = [
        "# Experimento ao vivo — RAG atual vs Sentence-Window",
        "",
        f"- Execução: `{payload['run_id']}`",
        f"- Gerado em: `{payload['generated_at']}`",
        ("- Recomendação final: `" + str(payload["recommendation"]) + "`"),
        "",
        "## Casos",
        "",
        "| Caso | Status | Answer Relevancy Δ | Faithfulness Δ | Contextual Relevancy Δ | Latência Δ | Quality Gate | Recomendação |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]

    for case in payload["cases"]:
        if case.get("status") != "completed":
            lines.append(
                "| `"
                + str(
                    case.get(
                        "case_id",
                        "unknown",
                    )
                )
                + "` | failed | - | - | - | - | - | manual_review |"
            )

            continue

        deltas = case.get(
            "axis_deltas",
            {},
        )

        def score(
            name: str,
            *,
            _bound_deltas: Mapping[str, Any] = deltas,
        ) -> str:
            value = _bound_deltas.get(name)

            if value is None:
                return "-"

            return f"{float(value):+.4f}"

        gate = case.get("quality_gate_passed")

        lines.append(
            "| `"
            + str(case["case_id"])
            + "` | completed | "
            + score("answer_relevancy")
            + " | "
            + score("faithfulness")
            + " | "
            + score("contextual_relevancy")
            + " | "
            + (f"{float(case['latency_delta_ms']):+.2f} ms")
            + " | "
            + str(gate)
            + " | `"
            + str(case["recommendation"])
            + "` |"
        )

    lines.extend(
        (
            "",
            "## Motivos da recomendação final",
            "",
        )
    )

    for reason in payload["recommendation_reasons"]:
        lines.append("- " + str(reason))

    lines.extend(
        (
            "",
            "## Privacidade",
            "",
            "- Respostas brutas não foram salvas.",
            "- Contextos brutos não foram salvos.",
            "- Foram preservados somente hashes, tamanhos, métricas e metadados técnicos.",
            "",
            "## Controle financeiro",
            "",
            (
                "- Custo estimado registrado: `"
                + str(payload["total_estimated_cost"])
                + "`."
            ),
            (
                "- Limite por variante: `"
                + str(payload["configuration"]["maximum_total_cost_per_variant"])
                + "`."
            ),
            "",
        )
    )

    return "\n".join(lines)


def run_live_retrieval_ab_suite(
    *,
    questions: Sequence[str],
    output_directory: str | Path,
    configuration: (LiveSuiteConfiguration | None) = None,
    variant_executor: (VariantExecutor | None) = None,
    pair_evaluator: (PairEvaluator | None) = None,
    pair_report_writer: (PairReportWriter | None) = None,
    runner: Any | None = None,
    runner_settings: Any | None = None,
    quality_gate_thresholds: Any | None = None,
) -> dict[str, Any]:
    """
    Executa a suíte real e gera evidências versionadas.
    """

    config = configuration or LiveSuiteConfiguration()

    normalized_questions: list[str] = []

    for question in questions:
        rendered = str(question or "").strip()

        if len(rendered) >= 3 and rendered not in normalized_questions:
            normalized_questions.append(rendered)

    if not normalized_questions:
        raise ValueError("Nenhuma pergunta válida foi fornecida.")

    safe_top_k = max(
        1,
        min(
            int(config.top_k),
            20,
        ),
    )

    output_path = Path(output_directory)

    pair_output_path = output_path / "pairs"

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    pair_output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    if variant_executor is None:
        variant_executor = execute_rag_variant

    if pair_evaluator is None:
        from src.evaluation.retrieval_ab_triad import (
            evaluate_retrieval_ab_with_rag_triad,
        )

        pair_evaluator = evaluate_retrieval_ab_with_rag_triad

    if pair_report_writer is None:
        from src.evaluation.retrieval_ab_triad import (
            write_retrieval_ab_triad_report,
        )

        pair_report_writer = write_retrieval_ab_triad_report

    if runner is None:
        (
            runner,
            runner_settings,
            quality_gate_thresholds,
        ) = _build_real_runner_bundle(
            maximum_total_cost=(config.maximum_total_cost_per_variant)
        )

    from src.evaluation.retrieval_ab_triad import (
        TriadVariantInput,
    )

    generated_at = datetime.now(UTC)

    run_id = (
        "week3-live-rag-ab-"
        + generated_at.strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + _sha256("\n".join(normalized_questions))[:10]
    )

    cases: list[dict[str, Any]] = []

    total_estimated_cost = 0.0

    for index, question in enumerate(
        normalized_questions,
        start=1,
    ):
        case = build_live_evaluation_case(
            question=question,
            index=index,
        )

        try:
            # Alterna a ordem de geração para reduzir
            # distorção de cold start.
            generation_order = (
                (
                    True,
                    False,
                )
                if index % 2 == 0
                else (
                    False,
                    True,
                )
            )

            executions: dict[
                bool,
                LiveVariantExecution,
            ] = {}

            for enabled in generation_order:
                executions[enabled] = variant_executor(
                    question=question,
                    language=(config.language),
                    top_k=safe_top_k,
                    sentence_window_enabled=(enabled),
                )

            baseline = executions[False]

            candidate = executions[True]

            pair_result = pair_evaluator(
                case=case,
                baseline=TriadVariantInput(
                    actual_output=(baseline.answer),
                    context=(baseline.retrieval_context),
                    retrieval_context=(baseline.retrieval_context),
                    metadata={
                        "variant": (baseline.name),
                        "answer_sha256": (_sha256(baseline.answer)),
                        "context_sha256": (
                            _sha256("\n".join(baseline.retrieval_context))
                        ),
                    },
                ),
                candidate=TriadVariantInput(
                    actual_output=(candidate.answer),
                    context=(candidate.retrieval_context),
                    retrieval_context=(candidate.retrieval_context),
                    metadata={
                        "variant": (candidate.name),
                        "answer_sha256": (_sha256(candidate.answer)),
                        "context_sha256": (
                            _sha256("\n".join(candidate.retrieval_context))
                        ),
                    },
                ),
                runner=runner,
                runner_settings=(runner_settings),
                quality_gate_thresholds=(quality_gate_thresholds),
                external_run=True,
                tolerance=(config.tolerance),
                metadata={
                    "suite_run_id": run_id,
                    "case_index": index,
                    "question_sha256": (_sha256(question)),
                    "generation_order": [
                        ("hybrid_sentence_window" if enabled else "hybrid_baseline")
                        for enabled in generation_order
                    ],
                },
            )

            pair_reports = pair_report_writer(
                pair_result,
                output_directory=(pair_output_path),
                run_label=(f"case-{index:03d}"),
            )

            baseline_cost = _estimated_cost(pair_result.baseline)

            candidate_cost = _estimated_cost(pair_result.candidate)

            case_cost = baseline_cost + candidate_cost

            total_estimated_cost += case_cost

            effective_quality_gate = _safe_external(pair_result.quality_gate)

            gate_passed = _gate_passed(effective_quality_gate)

            if gate_passed is None:
                effective_quality_gate = _quality_gate_from_axis_scores(
                    axis_scores=(pair_result.axis_scores),
                    axis_deltas=(pair_result.axis_deltas),
                    thresholds=(quality_gate_thresholds),
                )

                gate_passed = effective_quality_gate.get("passed")

            effective_recommendation = pair_result.recommendation

            effective_recommendation_reasons = list(pair_result.recommendation_reasons)

            if gate_passed is True:
                effective_recommendation = "promote_sentence_window"

                effective_recommendation_reasons = [
                    ("O Sentence-Window atingiu os limites da RAG Triad."),
                    ("Nenhuma regressão superou o limite configurado."),
                ]

            elif gate_passed is False:
                effective_recommendation = "reject_sentence_window"

                effective_recommendation_reasons = [
                    ("O Sentence-Window não atingiu todos os limites do Quality Gate.")
                ]

            cases.append(
                {
                    "case_id": (case.case_id),
                    "question": question,
                    "question_sha256": (_sha256(question)),
                    "status": "completed",
                    "generation_order": [
                        ("hybrid_sentence_window" if enabled else "hybrid_baseline")
                        for enabled in generation_order
                    ],
                    "baseline": (safe_variant_payload(baseline)),
                    "candidate": (safe_variant_payload(candidate)),
                    "latency_delta_ms": round(
                        candidate.duration_ms - baseline.duration_ms,
                        3,
                    ),
                    "context_character_delta": (
                        sum(len(item) for item in candidate.retrieval_context)
                        - sum(len(item) for item in baseline.retrieval_context)
                    ),
                    "axis_scores": (_safe_external(pair_result.axis_scores)),
                    "axis_deltas": (_safe_external(pair_result.axis_deltas)),
                    "quality_gate": (effective_quality_gate),
                    "quality_gate_passed": (gate_passed),
                    "recommendation": (effective_recommendation),
                    "recommendation_reasons": (effective_recommendation_reasons),
                    "estimated_cost": round(
                        case_cost,
                        8,
                    ),
                    "pair_reports": (_safe_external(pair_reports)),
                    "raw_outputs_stored": False,
                    "raw_contexts_stored": False,
                }
            )

        except Exception as exc:
            cases.append(
                {
                    "case_id": (case.case_id),
                    "question": question,
                    "question_sha256": (_sha256(question)),
                    "status": "failed",
                    "error_type": (type(exc).__name__),
                    "error_message": str(exc)[:1000],
                    "raw_outputs_stored": False,
                    "raw_contexts_stored": False,
                }
            )

            if config.fail_fast:
                raise

    completed_cases = [item for item in cases if item.get("status") == "completed"]

    failed_cases = [item for item in cases if item.get("status") != "completed"]

    recommendation, reasons = _overall_recommendation(
        completed_cases=(completed_cases),
        failed_case_count=len(failed_cases),
        maximum_median_latency_regression_ms=(
            config.maximum_median_latency_regression_ms
        ),
    )

    latency_deltas = [float(item["latency_delta_ms"]) for item in completed_cases]

    context_deltas = [int(item["context_character_delta"]) for item in completed_cases]

    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_id,
        "generated_at": (generated_at.isoformat()),
        "experiment": ("week3_live_retrieval_ab"),
        "configuration": {
            "top_k": safe_top_k,
            "language": (config.language),
            "tolerance": (config.tolerance),
            "maximum_total_cost_per_variant": (config.maximum_total_cost_per_variant),
            "maximum_median_latency_regression_ms": (
                config.maximum_median_latency_regression_ms
            ),
        },
        "question_count": len(normalized_questions),
        "completed_count": len(completed_cases),
        "failed_count": len(failed_cases),
        "recommendation": (recommendation),
        "recommendation_reasons": (reasons),
        "median_latency_delta_ms": (
            round(
                statistics.median(latency_deltas),
                3,
            )
            if latency_deltas
            else None
        ),
        "average_latency_delta_ms": (
            round(
                statistics.mean(latency_deltas),
                3,
            )
            if latency_deltas
            else None
        ),
        "average_context_character_delta": (
            round(
                statistics.mean(context_deltas),
                3,
            )
            if context_deltas
            else None
        ),
        "total_estimated_cost": round(
            total_estimated_cost,
            8,
        ),
        "cases": cases,
        "privacy": {
            "raw_outputs_stored": False,
            "raw_contexts_stored": False,
            "hash_algorithm": "SHA-256",
        },
    }

    json_path = output_path / f"{run_id}.json"

    markdown_path = output_path / f"{run_id}.md"

    history_path = output_path / "history.jsonl"

    json_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    markdown_path.write_text(
        _markdown_report(payload),
        encoding="utf-8",
    )

    history_record = {
        "run_id": run_id,
        "generated_at": (payload["generated_at"]),
        "completed_count": (payload["completed_count"]),
        "failed_count": (payload["failed_count"]),
        "recommendation": (payload["recommendation"]),
        "median_latency_delta_ms": (payload["median_latency_delta_ms"]),
        "total_estimated_cost": (payload["total_estimated_cost"]),
        "json_report": str(json_path),
        "markdown_report": str(markdown_path),
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
        "payload": payload,
        "run_id": run_id,
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "history_path": str(history_path),
    }
