from __future__ import annotations

from contextlib import contextmanager

import pytest

import src.agents.graph as module
from src.agents.graph import (
    retomar_revisao_humana_persistente,
)


class FakeGraph:
    def __init__(self):
        self.command = None
        self.config = None

    def invoke(
        self,
        command,
        *,
        config,
    ):
        self.command = command
        self.config = config

        return {
            "human_review_status": "approved",
            "human_review_required": False,
        }


@contextmanager
def fake_checkpointer_context():
    yield object()


def test_resume_invokes_command_with_same_thread(
    monkeypatch,
):
    graph = FakeGraph()

    monkeypatch.setattr(
        module,
        "abrir_checkpointer_postgres",
        fake_checkpointer_context,
    )

    monkeypatch.setattr(
        module,
        "criar_grafo_inna",
        lambda **kwargs: graph,
    )

    result = retomar_revisao_humana_persistente(
        thread_id="thread-resume-001",
        decisao={
            "action": "approve",
            "reviewer_id": "user-001",
        },
    )

    assert result["human_review_status"] == "approved"

    assert graph.command.resume == {
        "action": "approve",
        "reviewer_id": "user-001",
    }

    assert graph.config["configurable"]["thread_id"] == "thread-resume-001"


@pytest.mark.parametrize(
    "thread_id",
    [
        "",
        " ",
        None,
    ],
)
def test_resume_requires_thread_id(
    thread_id,
):
    with pytest.raises(
        ValueError,
        match="thread_id",
    ):
        retomar_revisao_humana_persistente(
            thread_id=thread_id,
            decisao={
                "action": "approve",
                "reviewer_id": "user-001",
            },
        )


def test_resume_rejects_long_thread_id():
    with pytest.raises(
        ValueError,
        match="255",
    ):
        retomar_revisao_humana_persistente(
            thread_id="x" * 256,
            decisao={
                "action": "approve",
                "reviewer_id": "user-001",
            },
        )


@pytest.mark.parametrize(
    "decision",
    [
        None,
        "approve",
        ["approve"],
    ],
)
def test_resume_requires_mapping(
    decision,
):
    with pytest.raises(
        TypeError,
        match="Mapping",
    ):
        retomar_revisao_humana_persistente(
            thread_id="thread-resume",
            decisao=decision,
        )


def test_resume_rejects_empty_decision():
    with pytest.raises(
        ValueError,
        match="não pode ser vazia",
    ):
        retomar_revisao_humana_persistente(
            thread_id="thread-resume",
            decisao={},
        )
