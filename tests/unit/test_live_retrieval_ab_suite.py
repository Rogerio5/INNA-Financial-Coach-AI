from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

from src.evaluation.live_retrieval_ab_suite import (
    LiveSuiteConfiguration,
    LiveVariantExecution,
    _overall_recommendation,
    run_live_retrieval_ab_suite,
    safe_variant_payload,
    temporary_environment,
)


def _fake_variant_executor(
    *,
    question: str,
    language: str,
    top_k: int,
    sentence_window_enabled: bool,
) -> LiveVariantExecution:
    del question
    del language
    del top_k

    return LiveVariantExecution(
        name=(
            "hybrid_sentence_window" if sentence_window_enabled else "hybrid_baseline"
        ),
        sentence_window_enabled=(sentence_window_enabled),
        answer=(
            "SEGREDO_RESPOSTA_B" if sentence_window_enabled else "SEGREDO_RESPOSTA_A"
        ),
        retrieval_context=(
            ("CONTEXTO_SECRETO_B",)
            if sentence_window_enabled
            else ("CONTEXTO_SECRETO_A",)
        ),
        mode=("sentence_window" if sentence_window_enabled else "hybrid"),
        duration_ms=(120.0 if sentence_window_enabled else 100.0),
        source_count=1,
        retrieved_documents=1,
    )


def _fake_pair_evaluator(
    **kwargs,
):
    del kwargs

    baseline_evaluation = SimpleNamespace(
        evaluation_run=(SimpleNamespace(total_estimated_cost=0.01))
    )

    candidate_evaluation = SimpleNamespace(
        evaluation_run=(SimpleNamespace(total_estimated_cost=0.01))
    )

    return SimpleNamespace(
        baseline=baseline_evaluation,
        candidate=candidate_evaluation,
        axis_scores={
            "hybrid_baseline": {
                "answer_relevancy": 0.80,
                "faithfulness": 0.81,
                "contextual_relevancy": 0.79,
            },
            "hybrid_sentence_window": {
                "answer_relevancy": 0.84,
                "faithfulness": 0.85,
                "contextual_relevancy": 0.83,
            },
        },
        axis_deltas={
            "answer_relevancy": 0.04,
            "faithfulness": 0.04,
            "contextual_relevancy": 0.04,
        },
        quality_gate={
            "status": "passed",
            "passed": True,
        },
        recommendation=("promote_sentence_window"),
        recommendation_reasons=("Melhoria sem regressão.",),
    )


def _fake_report_writer(
    result,
    *,
    output_directory,
    run_label,
):
    del result

    output_path = Path(output_directory)

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = output_path / f"{run_label}.json"

    markdown_path = output_path / f"{run_label}.md"

    history_path = output_path / "history.jsonl"

    json_path.write_text(
        "{}",
        encoding="utf-8",
    )

    markdown_path.write_text(
        "# test",
        encoding="utf-8",
    )

    history_path.write_text(
        "{}\n",
        encoding="utf-8",
    )

    return {
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "history_path": str(history_path),
    }


def test_temporary_environment_restores_value() -> None:
    os.environ["INNA_TEST_TEMPORARY_ENV"] = "original"

    with temporary_environment({"INNA_TEST_TEMPORARY_ENV": ("temporary")}):
        assert os.environ["INNA_TEST_TEMPORARY_ENV"] == "temporary"

    assert os.environ["INNA_TEST_TEMPORARY_ENV"] == "original"


def test_safe_variant_does_not_include_raw_data() -> None:
    variant = _fake_variant_executor(
        question="Pergunta",
        language="pt",
        top_k=4,
        sentence_window_enabled=False,
    )

    payload = safe_variant_payload(variant)

    serialized = json.dumps(
        payload,
        ensure_ascii=False,
    )

    assert "SEGREDO_RESPOSTA_A" not in serialized
    assert "CONTEXTO_SECRETO_A" not in serialized
    assert payload["raw_answer_stored"] is False


def test_overall_rejects_failed_quality_gate() -> None:
    recommendation, reasons = _overall_recommendation(
        completed_cases=[
            {
                "recommendation": ("promote_sentence_window"),
                "quality_gate_passed": False,
                "latency_delta_ms": 10.0,
            }
        ],
        failed_case_count=0,
        maximum_median_latency_regression_ms=1000,
    )

    assert recommendation == ("reject_sentence_window")

    assert reasons


def test_live_suite_with_fakes_creates_reports(
    tmp_path: Path,
) -> None:
    result = run_live_retrieval_ab_suite(
        questions=[
            "Como criar uma reserva financeira?",
            "Como organizar meu orçamento?",
        ],
        output_directory=tmp_path,
        configuration=(LiveSuiteConfiguration(fail_fast=True)),
        variant_executor=(_fake_variant_executor),
        pair_evaluator=(_fake_pair_evaluator),
        pair_report_writer=(_fake_report_writer),
        runner=object(),
        runner_settings=object(),
        quality_gate_thresholds=object(),
    )

    payload = result["payload"]

    assert payload["completed_count"] == 2

    assert payload["failed_count"] == 0

    assert payload["recommendation"] == "promote_sentence_window"

    assert Path(result["json_path"]).is_file()

    assert Path(result["markdown_path"]).is_file()

    assert Path(result["history_path"]).is_file()


def test_suite_report_does_not_store_answers_or_contexts(
    tmp_path: Path,
) -> None:
    result = run_live_retrieval_ab_suite(
        questions=[
            "Pergunta pública de teste",
        ],
        output_directory=tmp_path,
        variant_executor=(_fake_variant_executor),
        pair_evaluator=(_fake_pair_evaluator),
        pair_report_writer=(_fake_report_writer),
        runner=object(),
        runner_settings=object(),
        quality_gate_thresholds=object(),
    )

    serialized = Path(result["json_path"]).read_text(
        encoding="utf-8",
    )

    assert "SEGREDO_RESPOSTA_A" not in serialized
    assert "SEGREDO_RESPOSTA_B" not in serialized
    assert "CONTEXTO_SECRETO_A" not in serialized
    assert "CONTEXTO_SECRETO_B" not in serialized


def test_live_safe_external_serializes_mappingproxy() -> None:
    """
    Protege também o relatório consolidado da suíte live.
    """

    from dataclasses import dataclass
    from types import MappingProxyType

    from src.evaluation.live_retrieval_ab_suite import (
        _safe_external,
    )

    @dataclass(frozen=True)
    class MappingProxyQualityGate:
        metadata: object
        passed: bool

    quality_gate = MappingProxyQualityGate(
        metadata=MappingProxyType(
            {
                "threshold": 0.70,
                "source": "rag-triad",
            }
        ),
        passed=True,
    )

    serialized = _safe_external(quality_gate)

    assert serialized == {
        "metadata": {
            "threshold": 0.70,
            "source": "rag-triad",
        },
        "passed": True,
    }


def test_quality_gate_fallback_uses_axis_scores() -> None:
    from types import SimpleNamespace

    from src.evaluation.live_retrieval_ab_suite import (
        _quality_gate_from_axis_scores,
    )

    gate = _quality_gate_from_axis_scores(
        axis_scores={
            "hybrid_baseline": {
                "answer_relevancy": 1.0,
                "faithfulness": 1.0,
                "contextual_relevancy": (0.3142857142857143),
            },
            "hybrid_sentence_window": {
                "answer_relevancy": 1.0,
                "faithfulness": 1.0,
                "contextual_relevancy": 0.8125,
            },
        },
        axis_deltas={
            "answer_relevancy": 0.0,
            "faithfulness": 0.0,
            "contextual_relevancy": 0.498214,
        },
        thresholds=SimpleNamespace(
            answer_relevancy=0.7,
            faithfulness=0.7,
            contextual_relevancy=0.7,
            aggregate_score=0.7,
            maximum_regression=0.05,
        ),
    )

    assert gate["complete"] is True
    assert gate["passed"] is True
    assert gate["failed_keys"] == []
    assert gate["unavailable_keys"] == []

    checks = {item["key"]: item for item in gate["checks"]}

    assert checks["answer-relevancy"]["score"] == 1.0

    assert checks["faithfulness"]["score"] == 1.0

    assert checks["contextual-relevancy"]["score"] == 0.8125

    assert checks["rag-triad-average"]["passed"] is True

    assert checks["maximum-regression"]["passed"] is True
