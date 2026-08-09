"""
Testes da Fase 4:
Sufficiency Check do Agentic RAG.
"""

from __future__ import annotations

import pytest

from src.agentic_rag import (
    EvidenceCollectionResult,
    EvidenceCollectionStatus,
    EvidenceGapType,
    EvidenceItem,
    ResearchSource,
    SufficiencyDecision,
    SufficiencyEvaluator,
    assess_evidence_sufficiency,
    assessment_to_audit_payload,
    content_sha256,
    create_research_plan,
)


def _simple_plan():
    return create_research_plan("O que é uma reserva de emergência?")


def _complex_plan():
    return create_research_plan(
        "Compare reserva de emergência e dívidas, "
        "explique os riscos e crie um plano completo."
    )


def _history_plan():
    return create_research_plan(
        (
            "Compare minha evolução financeira com "
            "meus diagnósticos anteriores e explique "
            "os riscos atuais."
        ),
        user_id="trusted-user-test",
    )


def _collection(
    step,
    *,
    relevance: float = 0.90,
    references: bool = True,
    status=(EvidenceCollectionStatus.COLLECTED),
    warnings: list[str] | None = None,
):
    evidence = []

    if status == EvidenceCollectionStatus.COLLECTED:
        content = "Evidência verificada relacionada à " + step.question

        item_references = (
            [(f"{step.source.value}:{step.step_id}")] if references else []
        )

        evidence = [
            EvidenceItem(
                evidence_id=(f"ev_phase4_{step.step_id}_{int(relevance * 1000):04d}"),
                step_id=step.step_id,
                source=step.source,
                tool_name=step.tool_name,
                query=step.question,
                content=content,
                references=item_references,
                relevance_score=relevance,
                content_sha256=(content_sha256(content)),
                sensitive=(step.source == ResearchSource.FINANCIAL_HISTORY),
            )
        ]

    raw_item_count = len(evidence) if evidence else 0

    return EvidenceCollectionResult(
        step=step,
        status=status,
        evidence=evidence,
        tool_answer="",
        source_schema="phase4_test",
        output_sha256=content_sha256(step.step_id + status.value + str(relevance)),
        raw_item_count=raw_item_count,
        selected_count=len(evidence),
        discarded_count=0,
        warnings=warnings or [],
        metadata={
            "test_fixture": True,
        },
    )


def test_simple_research_is_sufficient():
    plan = _simple_plan()

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=[_collection(plan.subqueries[0])],
        round_number=1,
    )

    assert assessment.sufficient is True
    assert assessment.decision == SufficiencyDecision.SUFFICIENT
    assert assessment.retry_recommended is False
    assert assessment.score >= (assessment.threshold)
    assert assessment.required_step_completion == 1.0
    assert assessment.source_coverage == 1.0


def test_complete_complex_research_is_sufficient():
    plan = _complex_plan()

    collections = [
        _collection(
            step,
            relevance=0.85,
        )
        for step in plan.subqueries
    ]

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=collections,
        round_number=1,
    )

    assert assessment.sufficient is True
    assert assessment.evidence_count == len(plan.subqueries)
    assert assessment.completed_required_steps == assessment.total_required_steps


def test_missing_required_step_requests_retry():
    plan = _complex_plan()

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=[_collection(plan.subqueries[0])],
        round_number=1,
    )

    assert assessment.sufficient is False
    assert assessment.decision == SufficiencyDecision.NEEDS_MORE_RESEARCH
    assert assessment.retry_recommended is True
    assert EvidenceGapType.REQUIRED_STEP_MISSING in {
        gap.gap_type for gap in assessment.gaps
    }
    assert assessment.next_queries


def test_empty_required_collection_is_detected():
    plan = _complex_plan()

    collections = [
        _collection(plan.subqueries[0]),
        _collection(
            plan.subqueries[1],
            status=(EvidenceCollectionStatus.EMPTY),
        ),
    ]

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=collections,
        round_number=1,
    )

    gap_types = {gap.gap_type for gap in assessment.gaps}

    assert assessment.sufficient is False
    assert EvidenceGapType.EMPTY_COLLECTION in gap_types


def test_rejected_collection_is_critical_gap():
    plan = _complex_plan()

    collections = [
        _collection(plan.subqueries[0]),
        _collection(
            plan.subqueries[1],
            status=(EvidenceCollectionStatus.REJECTED),
            warnings=["inconsistent_history_output"],
        ),
    ]

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=collections,
        round_number=1,
    )

    gap_types = {gap.gap_type for gap in assessment.gaps}

    assert assessment.sufficient is False
    assert EvidenceGapType.REJECTED_COLLECTION in gap_types
    assert assessment.collection_quality < 1.0


def test_missing_references_blocks_completion():
    plan = _simple_plan()

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=[
            _collection(
                plan.subqueries[0],
                references=False,
            )
        ],
        round_number=1,
    )

    assert assessment.sufficient is False
    assert assessment.reference_coverage == 0.0
    assert EvidenceGapType.MISSING_REFERENCES in {
        gap.gap_type for gap in assessment.gaps
    }


def test_low_relevance_blocks_completion():
    plan = _simple_plan()

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=[
            _collection(
                plan.subqueries[0],
                relevance=0.01,
            )
        ],
        round_number=1,
    )

    assert assessment.sufficient is False
    assert EvidenceGapType.LOW_RELEVANCE in {gap.gap_type for gap in assessment.gaps}


def test_max_round_prevents_new_retry():
    plan = _complex_plan()

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=[],
        round_number=plan.max_rounds,
    )

    assert assessment.sufficient is False
    assert assessment.retry_recommended is False
    assert assessment.decision == SufficiencyDecision.INSUFFICIENT


def test_explicit_threshold_is_respected():
    plan = _complex_plan()

    collections = [
        _collection(
            step,
            relevance=0.80,
        )
        for step in plan.subqueries
    ]

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=collections,
        round_number=1,
        threshold=0.99,
    )

    assert assessment.threshold == 0.99
    assert assessment.sufficient is False
    assert assessment.retry_recommended is True


def test_audit_payload_does_not_expose_content():
    plan = _complex_plan()

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=[_collection(step) for step in plan.subqueries],
        round_number=1,
    )

    audit = assessment_to_audit_payload(assessment)
    serialized = repr(audit)

    assert plan.original_question not in serialized
    assert "next_queries" not in audit
    assert audit["content_logged"] is False
    assert audit["decision"] == "sufficient"


def test_personal_history_source_is_measured():
    plan = _history_plan()

    collections = [_collection(step) for step in plan.subqueries]

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=collections,
        round_number=1,
    )

    assert assessment.sufficient is True
    assert ResearchSource.FINANCIAL_HISTORY in assessment.covered_sources
    assert assessment.source_coverage == 1.0


def test_evaluator_facade_uses_same_contract():
    plan = _simple_plan()

    evaluator = SufficiencyEvaluator()

    assessment = evaluator.evaluate(
        question=plan.original_question,
        plan=plan,
        collections=[_collection(plan.subqueries[0])],
        round_number=1,
    )

    assert assessment.sufficient is True
    assert assessment.metrics["sufficiency_version"] == "4.0.0"


def test_later_success_recovers_previous_failure():
    plan = _simple_plan()
    step = plan.subqueries[0]

    collections = [
        _collection(
            step,
            status=(EvidenceCollectionStatus.REJECTED),
        ),
        _collection(
            step,
            relevance=0.90,
        ),
    ]

    assessment = assess_evidence_sufficiency(
        question=plan.original_question,
        plan=plan,
        collections=collections,
        round_number=1,
    )

    assert assessment.sufficient is True
    assert assessment.metrics["unresolved_rejected_required"] is False


def test_unplanned_collection_is_rejected():
    plan = _simple_plan()

    foreign_plan = create_research_plan("Como controlar gastos variáveis?")

    foreign_collection = _collection(foreign_plan.subqueries[0])

    with pytest.raises(
        ValueError,
        match="não pertencem ao plano",
    ):
        assess_evidence_sufficiency(
            question=plan.original_question,
            plan=plan,
            collections=[foreign_collection],
            round_number=1,
        )


def test_invalid_round_is_rejected():
    plan = _complex_plan()

    with pytest.raises(
        ValueError,
        match="round_number",
    ):
        assess_evidence_sufficiency(
            question=plan.original_question,
            plan=plan,
            collections=[],
            round_number=4,
        )
