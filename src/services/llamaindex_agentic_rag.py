"""LlamaIndex Agentic RAG runtime adapter for INNA."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any

from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.google_genai import GoogleGenAI

from src.agent_tools import rag_tools

FEATURE_FLAG = "INNA_LLAMAINDEX_AGENTIC_RAG_ENABLED"
TOOL_NAME = "consultar_rag_inna"
ROUTER_AGENT_NAME = "INNARouterAgent"
RESEARCH_AGENT_NAME = "INNAKnowledgeResearchAgent"


def llamaindex_agentic_rag_enabled() -> bool:
    """Return whether the LlamaIndex Agentic RAG gateway is enabled."""
    raw_value = os.getenv(FEATURE_FLAG, "false")
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _serialize_tool_result(result: Any) -> str:
    """Serialize the existing INNA formal RAG result safely."""
    if isinstance(result, str):
        return result

    if hasattr(result, "model_dump"):
        result = result.model_dump()

    if isinstance(result, Mapping):
        return json.dumps(
            dict(result),
            ensure_ascii=False,
            default=str,
        )

    if isinstance(result, (list, tuple)):
        return json.dumps(
            list(result),
            ensure_ascii=False,
            default=str,
        )

    return str(result)


def consultar_conhecimento_inna(pergunta: str) -> str:
    """Call the existing INNA Formal RAG Tool."""
    result = rag_tools.consultar_rag_inna(pergunta)
    return _serialize_tool_result(result)


def criar_llamaindex_rag_tool() -> FunctionTool:
    """Expose INNA Formal RAG as a LlamaIndex FunctionTool."""
    return FunctionTool.from_defaults(
        fn=consultar_conhecimento_inna,
        name=TOOL_NAME,
        description=(
            "Consulta a base de conhecimento financeira da INNA usando "
            "o Formal RAG Tool existente, incluindo o pipeline RAG e "
            "GraphRAG quando aplicavel."
        ),
    )


def _create_default_llm() -> GoogleGenAI:
    """Build the default Gemini LLM without exposing credentials."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = (
        os.getenv("INNA_RAG_MODEL", "").strip()
        or os.getenv("GEMINI_MODEL", "").strip()
    )

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY nao configurada.")

    if not model:
        raise RuntimeError(
            "INNA_RAG_MODEL ou GEMINI_MODEL nao configurado."
        )

    return GoogleGenAI(
        model=model,
        api_key=api_key,
        temperature=0.0,
    )


def criar_llamaindex_rag_agent(
    *,
    llm: Any | None = None,
) -> FunctionAgent:
    """Create the INNA knowledge Research Agent in LlamaIndex."""
    selected_llm = llm if llm is not None else _create_default_llm()
    tool = criar_llamaindex_rag_tool()

    return FunctionAgent(
        name=RESEARCH_AGENT_NAME,
        description=(
            "Agente LlamaIndex especializado em pesquisa fundamentada "
            "na base de conhecimento da INNA."
        ),
        system_prompt=(
            "Voce e o Research Agent de conhecimento da INNA. "
            "Para perguntas financeiras educacionais, use a ferramenta "
            "consultar_rag_inna. Baseie a resposta nas evidencias "
            "recuperadas e nao invente fatos ausentes."
        ),
        tools=[tool],
        llm=selected_llm,
        initial_tool_choice=TOOL_NAME,
        allow_parallel_tool_calls=False,
        can_handoff_to=[],
        streaming=False,
    )



def criar_llamaindex_router_agent(
    *,
    llm: Any | None = None,
) -> FunctionAgent:
    """Create the LlamaIndex routing agent for INNA."""
    selected_llm = llm if llm is not None else _create_default_llm()

    return FunctionAgent(
        name=ROUTER_AGENT_NAME,
        description=(
            "Agente roteador que direciona perguntas de conhecimento "
            "financeiro para o Research Agent da INNA."
        ),
        system_prompt=(
            "Voce e o Router Agent da INNA. Analise a solicitacao. "
            "Quando a pergunta exigir conhecimento financeiro educativo "
            "ou consulta documental, faca handoff para "
            "INNAKnowledgeResearchAgent. Nao invente resposta factual "
            "quando a pesquisa for necessaria."
        ),
        tools=[],
        llm=selected_llm,
        can_handoff_to=[RESEARCH_AGENT_NAME],
        allow_parallel_tool_calls=False,
        streaming=False,
    )


def criar_llamaindex_agent_workflow(
    *,
    llm: Any | None = None,
) -> AgentWorkflow:
    """Create Router -> Research multi-agent workflow."""
    selected_llm = llm if llm is not None else _create_default_llm()

    router_agent = criar_llamaindex_router_agent(
        llm=selected_llm,
    )
    research_agent = criar_llamaindex_rag_agent(
        llm=selected_llm,
    )

    return AgentWorkflow(
        agents=[
            router_agent,
            research_agent,
        ],
        root_agent=router_agent.name,
        timeout=120.0,
    )

async def executar_llamaindex_agent_workflow_payload(
    pergunta: str,
    *,
    idioma: str = "pt",
    top_k: int = 2,
    llm: Any | None = None,
) -> dict[str, Any]:
    """Execute AgentWorkflow and preserve the Formal RAG payload."""
    if not llamaindex_agentic_rag_enabled():
        raise RuntimeError(
            "LlamaIndex Agentic RAG esta desabilitado por feature flag."
        )

    selected_llm = llm if llm is not None else _create_default_llm()
    capture: dict[str, Any] = {}

    def _capturing_tool(pergunta: str) -> str:
        formal_result = rag_tools.consultar_rag_inna(
            pergunta,
            idioma=idioma,
            top_k=top_k,
        )
        serialized = _serialize_tool_result(formal_result)

        normalized = formal_result
        if hasattr(normalized, "model_dump"):
            normalized = normalized.model_dump()

        if isinstance(normalized, Mapping):
            capture["formal_rag_result"] = dict(normalized)
        else:
            try:
                parsed = json.loads(serialized)
            except (TypeError, ValueError, json.JSONDecodeError):
                parsed = None

            if isinstance(parsed, dict):
                capture["formal_rag_result"] = parsed

        return serialized

    tool = FunctionTool.from_defaults(
        fn=_capturing_tool,
        name=TOOL_NAME,
        description=(
            "Consulta a base de conhecimento financeira da INNA usando "
            "o Formal RAG Tool existente, incluindo RAG e GraphRAG."
        ),
    )

    research_agent = FunctionAgent(
        name=RESEARCH_AGENT_NAME,
        description=(
            "Agente LlamaIndex especializado em pesquisa fundamentada "
            "na base de conhecimento da INNA."
        ),
        system_prompt=(
            "Voce e o Research Agent de conhecimento da INNA. "
            "Para perguntas financeiras educacionais, use a ferramenta "
            "consultar_rag_inna e baseie a resposta nas evidencias."
        ),
        tools=[tool],
        llm=selected_llm,
        initial_tool_choice=TOOL_NAME,
        can_handoff_to=[],
        allow_parallel_tool_calls=False,
        streaming=False,
    )

    router_agent = criar_llamaindex_router_agent(
        llm=selected_llm,
    )

    workflow = AgentWorkflow(
        agents=[router_agent, research_agent],
        root_agent=router_agent.name,
        timeout=120.0,
    )

    result = await workflow.run(user_msg=pergunta)
    formal_payload = capture.get("formal_rag_result")

    if not isinstance(formal_payload, dict):
        raise RuntimeError(
            "LlamaIndex AgentWorkflow nao retornou payload Formal RAG."
        )

    raw_result = formal_payload.get("raw_result")

    if isinstance(raw_result, Mapping):
        payload = dict(raw_result)
    else:
        payload = dict(formal_payload)

        if "fontes" not in payload and "sources" in formal_payload:
            payload["fontes"] = list(
                formal_payload.get("sources") or []
            )

        if "modo" not in payload and "mode" in formal_payload:
            payload["modo"] = str(
                formal_payload.get("mode") or "rag"
            )

    payload["resposta"] = str(result)
    payload["llamaindex_agentic_rag"] = {
        "enabled": True,
        "executed": True,
        "fallback_used": False,
        "runtime": "agent_workflow",
        "router_agent": ROUTER_AGENT_NAME,
        "research_agent": RESEARCH_AGENT_NAME,
    }
    return payload


async def executar_llamaindex_agent_workflow(
    pergunta: str,
    *,
    llm: Any | None = None,
) -> str:
    """Execute Router -> Research AgentWorkflow when enabled."""
    if not llamaindex_agentic_rag_enabled():
        raise RuntimeError(
            "LlamaIndex Agentic RAG esta desabilitado por feature flag."
        )

    workflow = criar_llamaindex_agent_workflow(llm=llm)
    result = await workflow.run(user_msg=pergunta)
    return str(result)
async def executar_llamaindex_agentic_rag(
    pergunta: str,
    *,
    llm: Any | None = None,
) -> str:
    """Execute the LlamaIndex gateway only when explicitly enabled."""
    if not llamaindex_agentic_rag_enabled():
        raise RuntimeError(
            "LlamaIndex Agentic RAG esta desabilitado por feature flag."
        )

    agent = criar_llamaindex_rag_agent(llm=llm)
    result = await agent.run(user_msg=pergunta)
    return str(result)
