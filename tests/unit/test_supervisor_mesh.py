from __future__ import annotations

import pytest

from src.agents.supervisor_mesh import (
    SUPERVISOR_MESH_SCHEMA_VERSION,
    plan_supervisor_mesh,
)
from src.agents.team_hierarchy import (
    TeamHierarchyError,
)


def test_single_domain_does_not_activate_mesh():
    plan = plan_supervisor_mesh(
        source_team="financial_team",
        requested_teams=[
            "financial_team",
        ],
        max_supervisors=1,
        multi_domain=False,
    )

    assert plan.active is False
    assert plan.status == "inactive"
    assert plan.participant_teams == (
        "financial_team",
    )
    assert (
        plan.reason
        == "supervisor_mesh_not_required"
    )


def test_financial_and_knowledge_plan_registered_supervisors():
    plan = plan_supervisor_mesh(
        source_team="financial_team",
        requested_teams=[
            "knowledge_team",
        ],
        max_supervisors=3,
        multi_domain=True,
    )

    assert plan.active is True
    assert plan.status == "planned"

    assert plan.participant_teams == (
        "financial_team",
        "knowledge_team",
    )

    assert plan.participant_supervisors == (
        "financial_team_supervisor",
        "knowledge_team_supervisor",
    )


def test_duplicate_teams_are_deduplicated():
    plan = plan_supervisor_mesh(
        source_team="financial_team",
        requested_teams=[
            "knowledge_team",
            "knowledge_team",
            "financial_team",
        ],
        max_supervisors=3,
        multi_domain=True,
    )

    assert plan.participant_teams == (
        "financial_team",
        "knowledge_team",
    )


def test_multi_domain_requires_two_supervisor_slots():
    plan = plan_supervisor_mesh(
        source_team="financial_team",
        requested_teams=[
            "knowledge_team",
        ],
        max_supervisors=1,
        multi_domain=True,
    )

    assert plan.active is False
    assert plan.status == "blocked"

    assert (
        plan.reason
        == "supervisor_mesh_budget_insufficient"
    )


def test_complex_budget_supports_three_supervisors():
    plan = plan_supervisor_mesh(
        source_team="financial_team",
        requested_teams=[
            "knowledge_team",
            "support_team",
        ],
        max_supervisors=3,
        multi_domain=True,
    )

    assert plan.active is True

    assert plan.participant_teams == (
        "financial_team",
        "knowledge_team",
        "support_team",
    )

    assert len(
        plan.participant_supervisors
    ) == 3


def test_mesh_fails_closed_when_domains_exceed_budget():
    plan = plan_supervisor_mesh(
        source_team="financial_team",
        requested_teams=[
            "knowledge_team",
            "support_team",
        ],
        max_supervisors=2,
        multi_domain=True,
    )

    assert plan.active is False
    assert plan.status == "blocked"

    assert (
        plan.reason
        == "supervisor_mesh_budget_exceeded"
    )


def test_unknown_team_is_rejected_by_registry():
    with pytest.raises(
        TeamHierarchyError
    ):
        plan_supervisor_mesh(
            source_team="financial_team",
            requested_teams=[
                "unknown_team",  # type: ignore[list-item]
            ],
            max_supervisors=3,
            multi_domain=True,
        )


def test_schema_version_is_stable():
    plan = plan_supervisor_mesh(
        source_team="support_team",
        requested_teams=[],
        max_supervisors=1,
        multi_domain=False,
    )

    assert (
        plan.schema_version
        == SUPERVISOR_MESH_SCHEMA_VERSION
        == "1.0.0"
    )



def test_multi_domain_without_participants_is_blocked():
    plan = plan_supervisor_mesh(
        source_team="financial_team",
        requested_teams=[],
        max_supervisors=3,
        multi_domain=True,
    )

    assert plan.active is False
    assert plan.status == "blocked"
    assert (
        plan.reason
        == "supervisor_mesh_participants_unresolved"
    )
