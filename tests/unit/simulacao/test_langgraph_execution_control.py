from __future__ import annotations

import pytest
from langgraph.errors import (
    GraphRecursionError,
)

from src.agents.graph import (
    DEFAULT_LANGGRAPH_RECURSION_LIMIT,
    LangGraphExecutionLimitError,
    _criar_config_execucao,
    _invocar_grafo_seguro,
)


class FakeSuccessfulGraph:
    def __init__(self):
        self.calls = []

    def invoke(
        self,
        state,
        config=None,
    ):
        self.calls.append(
            {
                "state": state,
                "config": config,
            }
        )

        return {
            **state,
            "response": "ok",
        }


class FakeRecursiveGraph:
    def invoke(
        self,
        state,
        config=None,
    ):
        raise GraphRecursionError(
            "recursion limit reached"
        )


def test_default_recursion_limit_is_positive():
    assert (
        DEFAULT_LANGGRAPH_RECURSION_LIMIT
        == 25
    )


def test_execution_config_without_thread():
    config = _criar_config_execucao()

    assert config == {
        "recursion_limit": 25,
    }

    assert "configurable" not in config


def test_execution_config_preserves_thread_id():
    config = _criar_config_execucao(
        thread_id="conversation-123",
    )

    assert config == {
        "recursion_limit": 25,
        "configurable": {
            "thread_id": "conversation-123",
        },
    }


def test_execution_config_normalizes_thread_id():
    config = _criar_config_execucao(
        thread_id="  conversation-123  ",
    )

    assert config[
        "configurable"
    ]["thread_id"] == (
        "conversation-123"
    )


def test_safe_invocation_passes_config():
    graph = FakeSuccessfulGraph()

    state = {
        "thread_id": "thread-1",
        "user_message": "Olá",
    }

    config = _criar_config_execucao(
        thread_id="thread-1",
    )

    result = _invocar_grafo_seguro(
        graph,
        state,
        config=config,
    )

    assert result["response"] == "ok"

    assert graph.calls == [
        {
            "state": state,
            "config": config,
        }
    ]


def test_recursion_error_becomes_domain_error():
    graph = FakeRecursiveGraph()

    state = {
        "thread_id": "thread-limit",
        "user_message": "Teste",
    }

    config = _criar_config_execucao(
        thread_id="thread-limit",
    )

    with pytest.raises(
        LangGraphExecutionLimitError,
        match=(
            "excedeu o limite máximo "
            "de passos"
        ),
    ) as captured:
        _invocar_grafo_seguro(
            graph,
            state,
            config=config,
        )

    assert isinstance(
        captured.value.__cause__,
        GraphRecursionError,
    )


def test_recursion_failure_does_not_return_partial_state():
    graph = FakeRecursiveGraph()

    with pytest.raises(
        LangGraphExecutionLimitError
    ):
        _invocar_grafo_seguro(
            graph,
            {
                "user_message": "Teste",
                "response": "parcial",
            },
            config={
                "recursion_limit": 25,
            },
        )
