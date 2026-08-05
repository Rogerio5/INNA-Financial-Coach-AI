from __future__ import annotations

import pytest

from src.agents.task_completion import (
    evaluate_task_completion,
)


def test_task_is_completed_when_all_requirements_exist():
    result = evaluate_task_completion(
        requirements=[
            "financial_diagnosis",
            "risk_classification",
            "response_generation",
        ],
        completed=[
            "financial_diagnosis",
            "risk_classification",
            "response_generation",
        ],
    )

    assert result["task_status"] == "completed"
    assert result["missing_requirements"] == []
    assert result["task_completion_score"] == 1.0


def test_task_is_partially_completed():
    result = evaluate_task_completion(
        requirements=[
            "financial_diagnosis",
            "risk_classification",
            "report_generation",
        ],
        completed=[
            "financial_diagnosis",
            "risk_classification",
        ],
    )

    assert result["task_status"] == "partially_completed"

    assert result["missing_requirements"] == ["report_generation"]

    assert result["task_completion_score"] == pytest.approx(
        2 / 3,
        abs=0.0001,
    )


def test_task_waits_for_user_input():
    result = evaluate_task_completion(
        requirements=[
            "income",
            "fixed_expenses",
        ],
        completed=[
            "income",
        ],
        needs_user_input=True,
        block_reason=("Os gastos fixos ainda não foram informados."),
    )

    assert result["task_status"] == "needs_user_input"

    assert result["missing_requirements"] == ["fixed_expenses"]

    assert "gastos fixos" in result["task_block_reason"].lower()


def test_blocked_state_has_priority_over_partial():
    result = evaluate_task_completion(
        requirements=[
            "financial_diagnosis",
            "report_generation",
        ],
        completed=[
            "financial_diagnosis",
        ],
        blocked=True,
        block_reason=("A ferramenta de relatório está indisponível."),
    )

    assert result["task_status"] == "blocked"


def test_failed_state_has_priority():
    result = evaluate_task_completion(
        requirements=[
            "financial_diagnosis",
        ],
        completed=[],
        failed=True,
    )

    assert result["task_status"] == "failed"
    assert result["task_block_reason"]


def test_cancelled_state_has_highest_priority():
    result = evaluate_task_completion(
        requirements=[
            "financial_diagnosis",
        ],
        completed=[
            "financial_diagnosis",
        ],
        cancelled=True,
        block_reason=("Operação cancelada pelo usuário."),
    )

    assert result["task_status"] == "cancelled"


def test_unknown_completed_requirement_is_discarded():
    result = evaluate_task_completion(
        requirements=[
            "financial_diagnosis",
        ],
        completed=[
            "financial_diagnosis",
            "unknown_requirement",
        ],
    )

    assert result["completed_requirements"] == ["financial_diagnosis"]


def test_duplicate_requirements_are_normalized():
    result = evaluate_task_completion(
        requirements=[
            "financial_diagnosis",
            "financial_diagnosis",
            "risk_classification",
        ],
        completed=[
            "financial_diagnosis",
        ],
    )

    assert result["task_requirements"] == [
        "financial_diagnosis",
        "risk_classification",
    ]

    assert result["task_completion_score"] == 0.5


def test_empty_task_is_considered_completed():
    result = evaluate_task_completion(
        requirements=[],
        completed=[],
    )

    assert result["task_status"] == "completed"
    assert result["task_completion_score"] == 0.0


def test_evidence_is_preserved():
    result = evaluate_task_completion(
        requirements=[
            "financial_diagnosis",
        ],
        completed=[
            "financial_diagnosis",
        ],
        evidence={
            "agent": "financial_agent",
            "tool": ("calcular_diagnostico_financeiro"),
        },
    )

    assert result["task_completion_evidence"]["agent"] == "financial_agent"
