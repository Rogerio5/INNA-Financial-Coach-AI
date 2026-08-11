from __future__ import annotations

import asyncio

import pytest
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.llms import MockLLM

from src.services import llamaindex_agentic_rag as runtime


def test_feature_flag_defaults_to_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(runtime.FEATURE_FLAG, raising=False)

    assert runtime.llamaindex_agentic_rag_enabled() is False


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("true", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("0", False),
        ("off", False),
    ],
)
def test_feature_flag_parsing(
    monkeypatch: pytest.MonkeyPatch,
    raw_value: str,
    expected: bool,
) -> None:
    monkeypatch.setenv(runtime.FEATURE_FLAG, raw_value)

    assert runtime.llamaindex_agentic_rag_enabled() is expected


def test_function_tool_calls_existing_formal_rag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def fake_consultar_rag(pergunta: str) -> dict[str, object]:
        calls.append(pergunta)
        return {
            "answer": "Reserva de emergencia e uma protecao financeira.",
            "source": "inna-test",
        }

    monkeypatch.setattr(
        runtime.rag_tools,
        "consultar_rag_inna",
        fake_consultar_rag,
    )

    tool = runtime.criar_llamaindex_rag_tool()
    output = tool.call(
        pergunta="O que e reserva de emergencia?"
    )

    assert calls == ["O que e reserva de emergencia?"]
    assert runtime.TOOL_NAME == tool.metadata.name
    assert "Reserva de emergencia" in str(output)


def test_function_agent_builds_with_offline_mock_llm() -> None:
    llm = MockLLM(max_tokens=32)

    agent = runtime.criar_llamaindex_rag_agent(llm=llm)

    assert isinstance(agent, FunctionAgent)
    assert agent.name == "INNAKnowledgeResearchAgent"


def test_runtime_gateway_blocks_when_feature_flag_is_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(runtime.FEATURE_FLAG, "false")

    with pytest.raises(
        RuntimeError,
        match="desabilitado por feature flag",
    ):
        asyncio.run(
            runtime.executar_llamaindex_agentic_rag(
                "Pergunta que nao deve executar."
            )
        )

def test_router_agent_builds_with_mock_llm() -> None:
    llm = MockLLM(max_tokens=32)

    router = runtime.criar_llamaindex_router_agent(
        llm=llm,
    )

    assert isinstance(router, FunctionAgent)
    assert router.name == runtime.ROUTER_AGENT_NAME
    assert router.can_handoff_to == [
        runtime.RESEARCH_AGENT_NAME
    ]


def test_research_agent_disables_reverse_handoff() -> None:
    llm = MockLLM(max_tokens=32)

    research = runtime.criar_llamaindex_rag_agent(
        llm=llm,
    )

    assert research.name == runtime.RESEARCH_AGENT_NAME
    assert research.can_handoff_to == []


def test_agent_workflow_wires_router_to_research() -> None:
    llm = MockLLM(max_tokens=32)

    workflow = runtime.criar_llamaindex_agent_workflow(
        llm=llm,
    )

    assert workflow.root_agent == runtime.ROUTER_AGENT_NAME
    assert set(workflow.agents) == {
        runtime.ROUTER_AGENT_NAME,
        runtime.RESEARCH_AGENT_NAME,
    }
    assert (
        workflow.agents[
            runtime.ROUTER_AGENT_NAME
        ].can_handoff_to
        == [runtime.RESEARCH_AGENT_NAME]
    )
    assert (
        workflow.agents[
            runtime.RESEARCH_AGENT_NAME
        ].can_handoff_to
        == []
    )

def test_multi_agent_gateway_blocks_when_feature_flag_is_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(runtime.FEATURE_FLAG, "false")

    with pytest.raises(
        RuntimeError,
        match="desabilitado por feature flag",
    ):
        asyncio.run(
            runtime.executar_llamaindex_agent_workflow(
                "Pergunta que nao deve executar.",
                llm=MockLLM(max_tokens=32),
            )
        )
