from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.evaluation.retrieval_ab_triad import (
    TriadVariantInput,
    build_retrieval_ab_triad_report_payload,
    evaluate_retrieval_ab_with_rag_triad,
    extract_rag_triad_axis_scores,
    write_retrieval_ab_triad_report,
)


@dataclass
class FakeRun:
    name: str
    triad: dict[str, Any]

    def rag_triad_payload(
        self,
    ) -> dict[str, Any]:
        return self.triad


class FakeRunner:
    def __init__(
        self,
        triads: list[dict[str, Any]],
    ) -> None:
        self.triads = list(triads)

        self.calls: list[dict[str, Any]] = []

    def run(
        self,
        case,
        payload,
        *,
        settings=None,
        metadata=None,
    ):
        self.calls.append(
            {
                "case": case,
                "payload": payload,
                "settings": settings,
                "metadata": metadata,
            }
        )

        triad = self.triads.pop(0)

        return FakeRun(
            name=str(metadata["retrieval_variant"]),
            triad=triad,
        )


def fake_payload_builder(
    case,
    *,
    actual_output,
    context=None,
    retrieval_context=None,
    metadata=None,
    external_run=False,
):
    return {
        "case": case,
        "actual_output": actual_output,
        "context": tuple(context or ()),
        "retrieval_context": tuple(retrieval_context or ()),
        "metadata": dict(metadata or {}),
        "external_run": external_run,
    }


def triad(
    *,
    answer: float,
    faithfulness: float,
    context: float,
    passed: bool = True,
):
    return {
        "status": ("passed" if passed else "failed"),
        "passed": passed,
        "axes": [
            {
                "metric_id": ("answer_relevancy"),
                "score": answer,
            },
            {
                "metric_id": ("faithfulness"),
                "score": faithfulness,
            },
            {
                "metric_id": ("contextual_relevancy"),
                "score": context,
            },
        ],
    }


def test_extracts_three_rag_triad_axes() -> None:
    scores = extract_rag_triad_axis_scores(
        triad(
            answer=0.91,
            faithfulness=0.93,
            context=0.89,
        )
    )

    assert scores == {
        "answer_relevancy": 0.91,
        "faithfulness": 0.93,
        "contextual_relevancy": 0.89,
    }


def test_executes_baseline_and_candidate() -> None:
    runner = FakeRunner(
        [
            triad(
                answer=0.80,
                faithfulness=0.82,
                context=0.79,
            ),
            triad(
                answer=0.84,
                faithfulness=0.85,
                context=0.83,
            ),
        ]
    )

    result = evaluate_retrieval_ab_with_rag_triad(
        case=object(),
        baseline=TriadVariantInput(
            actual_output="Resposta A",
            retrieval_context=("Contexto A",),
        ),
        candidate=TriadVariantInput(
            actual_output="Resposta B",
            retrieval_context=("Contexto B",),
        ),
        runner=runner,
        payload_builder=(fake_payload_builder),
        comparison_function=(
            lambda baseline, candidate, tolerance: {
                "tolerance": tolerance,
            }
        ),
    )

    assert len(runner.calls) == 2

    assert runner.calls[0]["metadata"]["retrieval_variant"] == "hybrid_baseline"

    assert runner.calls[1]["metadata"]["retrieval_variant"] == "hybrid_sentence_window"

    assert result.recommendation == ("promote_sentence_window")


def test_rejects_candidate_with_axis_regression() -> None:
    runner = FakeRunner(
        [
            triad(
                answer=0.90,
                faithfulness=0.90,
                context=0.90,
            ),
            triad(
                answer=0.90,
                faithfulness=0.70,
                context=0.90,
            ),
        ]
    )

    result = evaluate_retrieval_ab_with_rag_triad(
        case=object(),
        baseline=TriadVariantInput(
            actual_output="Resposta A",
        ),
        candidate=TriadVariantInput(
            actual_output="Resposta B",
        ),
        runner=runner,
        payload_builder=(fake_payload_builder),
        comparison_function=(lambda *args, **kwargs: {}),
        tolerance=0.01,
    )

    assert result.recommendation == ("reject_sentence_window")

    assert result.axis_deltas["faithfulness"] == -0.2


def test_requires_complete_actual_output() -> None:
    runner = FakeRunner([])

    try:
        evaluate_retrieval_ab_with_rag_triad(
            case=object(),
            baseline=TriadVariantInput(
                actual_output="",
            ),
            candidate=TriadVariantInput(
                actual_output="Resposta B",
            ),
            runner=runner,
            payload_builder=(fake_payload_builder),
        )
    except ValueError as exc:
        assert "actual_output" in str(exc)
    else:
        raise AssertionError("ValueError esperado.")


def test_report_does_not_store_raw_inputs() -> None:
    runner = FakeRunner(
        [
            triad(
                answer=0.80,
                faithfulness=0.80,
                context=0.80,
            ),
            triad(
                answer=0.81,
                faithfulness=0.81,
                context=0.81,
            ),
        ]
    )

    result = evaluate_retrieval_ab_with_rag_triad(
        case=object(),
        baseline=TriadVariantInput(
            actual_output=("SEGREDO_BASELINE"),
            retrieval_context=("CONTEXTO_SECRETO_A",),
        ),
        candidate=TriadVariantInput(
            actual_output=("SEGREDO_CANDIDATE"),
            retrieval_context=("CONTEXTO_SECRETO_B",),
        ),
        runner=runner,
        payload_builder=(fake_payload_builder),
        comparison_function=(lambda *args, **kwargs: {}),
    )

    payload = build_retrieval_ab_triad_report_payload(result)

    serialized = json.dumps(
        payload,
        ensure_ascii=False,
    )

    assert "SEGREDO_BASELINE" not in serialized
    assert "SEGREDO_CANDIDATE" not in serialized
    assert "CONTEXTO_SECRETO_A" not in serialized
    assert "CONTEXTO_SECRETO_B" not in serialized


def test_writes_versioned_reports_and_history(
    tmp_path: Path,
) -> None:
    runner = FakeRunner(
        [
            triad(
                answer=0.80,
                faithfulness=0.82,
                context=0.81,
            ),
            triad(
                answer=0.84,
                faithfulness=0.85,
                context=0.83,
            ),
        ]
    )

    result = evaluate_retrieval_ab_with_rag_triad(
        case=object(),
        baseline=TriadVariantInput(
            actual_output="Resposta A",
        ),
        candidate=TriadVariantInput(
            actual_output="Resposta B",
        ),
        runner=runner,
        payload_builder=(fake_payload_builder),
        comparison_function=(lambda *args, **kwargs: {}),
    )

    reports = write_retrieval_ab_triad_report(
        result,
        output_directory=tmp_path,
        run_label="unit-test",
    )

    assert Path(reports["json_path"]).is_file()

    assert Path(reports["markdown_path"]).is_file()

    history_path = Path(reports["history_path"])

    assert history_path.is_file()

    history = json.loads(
        history_path.read_text(
            encoding="utf-8",
        ).splitlines()[0]
    )

    assert history["recommendation"] == "promote_sentence_window"


def test_safe_external_serializes_mappingproxy_inside_dataclass() -> None:
    """
    Garante que metadados imutáveis do runner não sejam
    enviados para dataclasses.asdict/deepcopy.
    """

    from types import MappingProxyType

    from src.evaluation.retrieval_ab_triad import (
        _safe_external,
    )

    @dataclass(frozen=True)
    class MappingProxyEvaluationRun:
        metadata: object
        metric_results: tuple[object, ...] = ()

    evaluation_run = MappingProxyEvaluationRun(
        metadata=MappingProxyType(
            {
                "synthetic": True,
                "external_safe": True,
                "variant": "hybrid_baseline",
            }
        )
    )

    serialized = _safe_external(evaluation_run)

    assert serialized == {
        "metadata": {
            "synthetic": True,
            "external_safe": True,
            "variant": "hybrid_baseline",
        },
        "metric_results": [],
    }
