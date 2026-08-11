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


def test_structured_workflow_payload_preserves_formal_rag_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(runtime.FEATURE_FLAG, "true")

    calls: list[str] = []

    formal_payload = {
        "resposta": "Resposta do Formal RAG.",
        "fontes": [{"documento": "reserva"}],
        "modo": "rag_hibrido_grafo_estruturado_3072_rrf",
        "trace_id": "trace-li6c2",
        "retrieval_trace": {
            "total_time_ms": 12,
        },
    }

    def fake_consultar_rag_inna(
        pergunta: str,
        *,
        idioma: str = "pt",
        top_k: int = 2,
    ):
        calls.append(
            {
                "pergunta": pergunta,
                "idioma": idioma,
                "top_k": top_k,
            }
        )
        return formal_payload

    monkeypatch.setattr(
        runtime.rag_tools,
        "consultar_rag_inna",
        fake_consultar_rag_inna,
    )

    class FakeFunctionTool:
        @classmethod
        def from_defaults(
            cls,
            *,
            fn,
            name,
            description,
        ):
            return {
                "fn": fn,
                "name": name,
                "description": description,
            }

    class FakeFunctionAgent:
        def __init__(self, **kwargs):
            self.name = kwargs["name"]
            self.tools = kwargs.get("tools", [])

    class FakeRouterAgent:
        name = runtime.ROUTER_AGENT_NAME

    class FakeAgentWorkflow:
        def __init__(
            self,
            *,
            agents,
            root_agent,
            timeout,
        ) -> None:
            assert root_agent == runtime.ROUTER_AGENT_NAME
            assert timeout == 120.0
            self.research_agent = agents[1]

        async def run(self, *, user_msg: str):
            tool = self.research_agent.tools[0]
            serialized = tool["fn"](user_msg)
            assert isinstance(serialized, str)
            return "Resposta sintetizada pelo AgentWorkflow."

    monkeypatch.setattr(
        runtime,
        "FunctionTool",
        FakeFunctionTool,
    )
    monkeypatch.setattr(
        runtime,
        "FunctionAgent",
        FakeFunctionAgent,
    )
    monkeypatch.setattr(
        runtime,
        "criar_llamaindex_router_agent",
        lambda *, llm=None: FakeRouterAgent(),
    )
    monkeypatch.setattr(
        runtime,
        "AgentWorkflow",
        FakeAgentWorkflow,
    )

    result = asyncio.run(
        runtime.executar_llamaindex_agent_workflow_payload(
            "O que e reserva de emergencia?",
            idioma="pt-BR",
            top_k=7,
            llm=object(),
        )
    )

    assert calls == [
        {
            "pergunta": "O que e reserva de emergencia?",
            "idioma": "pt-BR",
            "top_k": 7,
        }
    ]
    assert result["resposta"] == (
        "Resposta sintetizada pelo AgentWorkflow."
    )
    assert result["fontes"] == formal_payload["fontes"]
    assert result["modo"] == formal_payload["modo"]
    assert result["trace_id"] == "trace-li6c2"
    assert result["retrieval_trace"] == {
        "total_time_ms": 12
    }

    metadata = result["llamaindex_agentic_rag"]

    assert metadata["enabled"] is True
    assert metadata["executed"] is True
    assert metadata["fallback_used"] is False
    assert metadata["runtime"] == "agent_workflow"
    assert metadata["router_agent"] == (
        runtime.ROUTER_AGENT_NAME
    )
    assert metadata["research_agent"] == (
        runtime.RESEARCH_AGENT_NAME
    )


def test_structured_workflow_payload_rejects_missing_formal_rag_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(runtime.FEATURE_FLAG, "true")

    monkeypatch.setattr(
        runtime.rag_tools,
        "consultar_rag_inna",
        lambda _pergunta, **_kwargs: (
            "resultado sem payload estruturado"
        ),
    )

    class FakeFunctionTool:
        @classmethod
        def from_defaults(
            cls,
            *,
            fn,
            name,
            description,
        ):
            return {
                "fn": fn,
                "name": name,
                "description": description,
            }

    class FakeFunctionAgent:
        def __init__(self, **kwargs):
            self.name = kwargs["name"]
            self.tools = kwargs.get("tools", [])

    class FakeRouterAgent:
        name = runtime.ROUTER_AGENT_NAME

    class FakeAgentWorkflow:
        def __init__(
            self,
            *,
            agents,
            root_agent,
            timeout,
        ) -> None:
            self.research_agent = agents[1]

        async def run(self, *, user_msg: str):
            tool = self.research_agent.tools[0]
            tool["fn"](user_msg)
            return "Resposta sem payload."

    monkeypatch.setattr(
        runtime,
        "FunctionTool",
        FakeFunctionTool,
    )
    monkeypatch.setattr(
        runtime,
        "FunctionAgent",
        FakeFunctionAgent,
    )
    monkeypatch.setattr(
        runtime,
        "criar_llamaindex_router_agent",
        lambda *, llm=None: FakeRouterAgent(),
    )
    monkeypatch.setattr(
        runtime,
        "AgentWorkflow",
        FakeAgentWorkflow,
    )

    with pytest.raises(
        RuntimeError,
        match="nao retornou payload Formal RAG",
    ):
        asyncio.run(
            runtime.executar_llamaindex_agent_workflow_payload(
                "Pergunta sem payload",
                llm=object(),
            )
        )

def test_structured_workflow_payload_uses_raw_result_as_api_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(runtime.FEATURE_FLAG, "true")

    raw_result = {
        "resposta": "Resposta antiga.",
        "fontes": [{"documento": "doc-graph", "origem_busca": ["grafo"], "rrf_contribution_grafo": 0.1, "graph_retrieval": True}],
        "modo": "rag_hibrido_grafo_estruturado_3072_rrf",
        "trace_id": "trace-raw",
        "retrieval_trace": {"total_time_ms": 20},
    }

    formal_result = runtime.rag_tools.RagToolResult(
        ok=True, question="Pergunta", language="pt",
        answer="Resposta formal", sources=["doc-graph"],
        mode="rag", retrieved_documents=1, duration_ms=10,
        retrieval_context=["contexto"], raw_result=raw_result,
    )

    def fake_consultar_rag_inna(pergunta: str, *, idioma: str = "pt", top_k: int = 2):
        assert pergunta == "Pergunta"
        assert idioma == "pt-BR"
        assert top_k == 4
        return formal_result

    monkeypatch.setattr(runtime.rag_tools, "consultar_rag_inna", fake_consultar_rag_inna)

    class FakeFunctionTool:
        @classmethod
        def from_defaults(cls, *, fn, name, description):
            return {"fn": fn, "name": name, "description": description}

    class FakeFunctionAgent:
        def __init__(self, **kwargs):
            self.name = kwargs["name"]
            self.tools = kwargs.get("tools", [])

    class FakeRouterAgent:
        name = runtime.ROUTER_AGENT_NAME

    class FakeAgentWorkflow:
        def __init__(self, *, agents, root_agent, timeout) -> None:
            self.research_agent = agents[1]

        async def run(self, *, user_msg: str):
            tool = self.research_agent.tools[0]
            tool["fn"](user_msg)
            return "Resposta final do AgentWorkflow."

    monkeypatch.setattr(runtime, "FunctionTool", FakeFunctionTool)
    monkeypatch.setattr(runtime, "FunctionAgent", FakeFunctionAgent)
    monkeypatch.setattr(runtime, "criar_llamaindex_router_agent", lambda *, llm=None: FakeRouterAgent())
    monkeypatch.setattr(runtime, "AgentWorkflow", FakeAgentWorkflow)

    result = asyncio.run(
        runtime.executar_llamaindex_agent_workflow_payload(
            "Pergunta", idioma="pt-BR", top_k=4, llm=object(),
        )
    )

    assert result["resposta"] == "Resposta final do AgentWorkflow."
    assert result["fontes"] == raw_result["fontes"]
    assert result["modo"] == raw_result["modo"]
    assert result["trace_id"] == "trace-raw"
    assert result["retrieval_trace"] == {"total_time_ms": 20}
    assert "raw_result" not in result
