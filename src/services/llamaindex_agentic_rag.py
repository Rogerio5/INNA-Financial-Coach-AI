"""LlamaIndex Agentic RAG runtime adapter for INNA."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.google_genai import GoogleGenAI

from src.agent_tools import rag_tools

FEATURE_FLAG = "INNA_LLAMAINDEX_AGENTIC_RAG_ENABLED"
TOOL_NAME = "consultar_rag_inna"


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
        name="INNAKnowledgeResearchAgent",
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
        streaming=False,
    )


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
