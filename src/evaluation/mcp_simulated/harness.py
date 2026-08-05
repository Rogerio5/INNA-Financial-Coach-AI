"""Harness offline para avaliação MCP ponta a ponta."""

from __future__ import annotations

import inspect
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.agent_tools.core.contracts import (
    ToolCall,
    ToolExecutionContext,
    ToolResult,
)
from src.agent_tools.core.executor import ToolExecutor
from src.agent_tools.core.permissions import ToolPermissionPolicy
from src.agent_tools.core.registry import (
    ToolDefinition,
    ToolRegistry,
)


class HealthInput(BaseModel):
    """Entrada do health check."""

    model_config = ConfigDict(extra="forbid")


class HealthOutput(BaseModel):
    """Saída do health check."""

    status: str
    service: str
    trace_id: str


class SimulatedRAGInput(BaseModel):
    """Entrada da ferramenta RAG simulada."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(
        min_length=10,
        max_length=500,
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
    )


class SimulatedRAGOutput(BaseModel):
    """Saída da ferramenta RAG simulada."""

    answer: str
    sources: list[str]
    evidence_count: int
    user_id: str
    session_id: str
    trace_id: str


class SimulatedFinancialInput(BaseModel):
    """Entrada da ferramenta financeira simulada."""

    model_config = ConfigDict(extra="forbid")

    monthly_income: float = Field(gt=0)
    fixed_expenses: float = Field(ge=0)
    variable_expenses: float = Field(ge=0)
    monthly_debts: float = Field(default=0, ge=0)


class SimulatedFinancialOutput(BaseModel):
    """Saída da ferramenta financeira simulada."""

    estimated_balance: float
    risk_level: str
    user_id: str
    session_id: str
    trace_id: str


class ControlledErrorInput(BaseModel):
    """Entrada para cenário de erro controlado."""

    model_config = ConfigDict(extra="forbid")

    message: str = "simulated failure"


class ControlledErrorOutput(BaseModel):
    """Saída formal do cenário de erro."""

    completed: bool


class TimeoutInput(BaseModel):
    """Entrada da ferramenta lenta."""

    model_config = ConfigDict(extra="forbid")

    delay_seconds: float = Field(
        default=0.15,
        ge=0,
        le=1,
    )


class TimeoutOutput(BaseModel):
    """Saída da ferramenta lenta."""

    completed: bool


@dataclass(frozen=True, slots=True)
class SimulatedMCPRequest:
    """Requisição do cliente MCP simulado."""

    tool_name: str
    arguments: Mapping[str, Any]
    agent_name: str
    user_id: str
    session_id: str
    trace_id: str
    call_id: str


@dataclass(slots=True)
class SimulatedMCPHarness:
    """Ambiente governado MCP usado na avaliação."""

    registry: ToolRegistry
    permission_policy: ToolPermissionPolicy
    executor: ToolExecutor

    def close(self) -> None:
        """Fecha o executor."""

        self.executor.close()


class SimulatedMCPClient:
    """Cliente MCP local sem servidor de rede."""

    def __init__(
        self,
        harness: SimulatedMCPHarness,
        *,
        agent_name: str,
        user_id: str,
        session_id: str,
    ) -> None:
        self._harness = harness
        self._agent_name = agent_name
        self._user_id = user_id
        self._session_id = session_id

    def call(
        self,
        tool_name: str,
        arguments: Mapping[str, Any],
        *,
        trace_id: str | None = None,
    ) -> ToolResult:
        """Executa uma ferramenta usando o executor real."""

        request = SimulatedMCPRequest(
            tool_name=tool_name,
            arguments=dict(arguments),
            agent_name=self._agent_name,
            user_id=self._user_id,
            session_id=self._session_id,
            trace_id=(
                trace_id
                or f"trace-{uuid.uuid4().hex}"
            ),
            call_id=f"call-{uuid.uuid4().hex}",
        )

        context = build_execution_context(
            request
        )

        call = build_tool_call(
            request,
            context=context,
        )

        return self._harness.executor.execute(
            call
        )


def _construct_compatible(
    target: type[Any],
    candidates: Mapping[str, Any],
) -> Any:
    """Constrói um contrato usando seus parâmetros reais."""

    signature = inspect.signature(
        target
    )

    kwargs: dict[str, Any] = {}

    for name, parameter in signature.parameters.items():
        if name == "self":
            continue

        if parameter.kind in {
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        }:
            continue

        if name in candidates:
            kwargs[name] = candidates[name]
            continue

        if (
            parameter.default
            is inspect.Parameter.empty
        ):
            raise TypeError(
                "Parâmetro obrigatório não mapeado em "
                f"{target.__name__}: {name}"
            )

    return target(
        **kwargs
    )


def build_execution_context(
    request: SimulatedMCPRequest,
) -> ToolExecutionContext:
    """Cria ToolExecutionContext usando aliases conhecidos."""

    now = datetime.now(
        UTC
    )

    candidates = {
        "agent_name": request.agent_name,
        "agent": request.agent_name,
        "caller_agent": request.agent_name,
        "requested_by": request.agent_name,
        "user_id": request.user_id,
        "trusted_user_id": request.user_id,
        "session_id": request.session_id,
        "conversation_id": request.session_id,
        "trace_id": request.trace_id,
        "correlation_id": request.trace_id,
        "request_id": request.call_id,
        "channel": "simulated-mcp",
        "language": "pt",
        "locale": "pt-BR",
        "currency": "BRL",
        "created_at": now,
        "requested_at": now,
        "metadata": {
            "transport": "simulated-mcp",
            "offline": True,
        },
        "context_metadata": {
            "transport": "simulated-mcp",
            "offline": True,
        },
    }

    return _construct_compatible(
        ToolExecutionContext,
        candidates,
    )


def build_tool_call(
    request: SimulatedMCPRequest,
    *,
    context: ToolExecutionContext,
) -> ToolCall:
    """Cria ToolCall usando os campos reais do contrato."""

    now = datetime.now(
        UTC
    )

    candidates = {
        "call_id": request.call_id,
        "id": request.call_id,
        "request_id": request.call_id,
        "tool_name": request.tool_name,
        "name": request.tool_name,
        "arguments": dict(request.arguments),
        "args": dict(request.arguments),
        "input": dict(request.arguments),
        "payload": dict(request.arguments),
        "context": context,
        "execution_context": context,
        "created_at": now,
        "requested_at": now,
    }

    return _construct_compatible(
        ToolCall,
        candidates,
    )


def _extract_context(
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
) -> Any:
    for name in (
        "context",
        "execution_context",
        "tool_context",
    ):
        if name in kwargs:
            return kwargs[name]

    for value in args:
        if isinstance(
            value,
            ToolExecutionContext,
        ):
            return value

    return None


def _extract_input(
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
) -> Any:
    for name in (
        "input_data",
        "input",
        "arguments",
        "payload",
        "request",
    ):
        if name in kwargs:
            return kwargs[name]

    for value in args:
        if isinstance(
            value,
            BaseModel,
        ):
            return value

    for value in args:
        if isinstance(
            value,
            Mapping,
        ):
            return value

    return None


def _payload_mapping(
    value: Any,
) -> dict[str, Any]:
    if value is None:
        return {}

    if isinstance(
        value,
        BaseModel,
    ):
        return value.model_dump()

    if isinstance(
        value,
        Mapping,
    ):
        return dict(value)

    if hasattr(
        value,
        "model_dump",
    ):
        return dict(
            value.model_dump()
        )

    raise TypeError(
        "Entrada não suportada: "
        f"{type(value).__name__}"
    )


def _context_value(
    context: Any,
    *names: str,
) -> str:
    for name in names:
        value = getattr(
            context,
            name,
            None,
        )

        if value is not None:
            return str(value)

    return ""


def _context_identifiers(
    context: Any,
) -> tuple[str, str, str]:
    return (
        _context_value(
            context,
            "user_id",
            "trusted_user_id",
        ),
        _context_value(
            context,
            "session_id",
            "conversation_id",
        ),
        _context_value(
            context,
            "trace_id",
            "correlation_id",
        ),
    )


def _health_handler(
    *args: Any,
    **kwargs: Any,
) -> Mapping[str, Any]:
    context = _extract_context(
        args,
        kwargs,
    )

    _, _, trace_id = _context_identifiers(
        context
    )

    return {
        "status": "ok",
        "service": "inna-mcp-simulated",
        "trace_id": trace_id,
    }


def _rag_handler(
    *args: Any,
    **kwargs: Any,
) -> Mapping[str, Any]:
    context = _extract_context(
        args,
        kwargs,
    )

    payload = _payload_mapping(
        _extract_input(
            args,
            kwargs,
        )
    )

    user_id, session_id, trace_id = (
        _context_identifiers(
            context
        )
    )

    question = str(
        payload.get(
            "question",
            "",
        )
    )

    return {
        "answer": (
            "Resposta simulada fundamentada para: "
            f"{question}"
        ),
        "sources": [
            "synthetic-financial-education",
            "synthetic-budget-guide",
        ],
        "evidence_count": 2,
        "user_id": user_id,
        "session_id": session_id,
        "trace_id": trace_id,
    }


def _financial_handler(
    *args: Any,
    **kwargs: Any,
) -> Mapping[str, Any]:
    context = _extract_context(
        args,
        kwargs,
    )

    payload = _payload_mapping(
        _extract_input(
            args,
            kwargs,
        )
    )

    income = float(
        payload["monthly_income"]
    )

    expenses = (
        float(payload["fixed_expenses"])
        + float(payload["variable_expenses"])
        + float(
            payload.get(
                "monthly_debts",
                0,
            )
        )
    )

    balance = round(
        income - expenses,
        2,
    )

    risk_level = (
        "low"
        if balance >= income * 0.2
        else (
            "medium"
            if balance >= 0
            else "high"
        )
    )

    user_id, session_id, trace_id = (
        _context_identifiers(
            context
        )
    )

    return {
        "estimated_balance": balance,
        "risk_level": risk_level,
        "user_id": user_id,
        "session_id": session_id,
        "trace_id": trace_id,
    }


def _controlled_error_handler(
    *args: Any,
    **kwargs: Any,
) -> Mapping[str, Any]:
    del args
    del kwargs

    raise RuntimeError(
        "simulated controlled MCP failure"
    )


def _timeout_handler(
    *args: Any,
    **kwargs: Any,
) -> Mapping[str, Any]:
    payload = _payload_mapping(
        _extract_input(
            args,
            kwargs,
        )
    )

    time.sleep(
        float(
            payload.get(
                "delay_seconds",
                0.15,
            )
        )
    )

    return {
        "completed": True,
    }


def build_tool_definition(
    *,
    name: str,
    description: str,
    input_model: type[BaseModel],
    output_model: type[BaseModel],
    handler: Callable[..., Any],
    allowed_agents: tuple[str, ...],
    timeout_seconds: float,
) -> ToolDefinition:
    """Cria ToolDefinition compatível com o registry real."""

    agents = frozenset(
        allowed_agents
    )

    candidates = {
        "name": name,
        "tool_name": name,
        "description": description,
        "summary": description,
        "input_model": input_model,
        "input_schema": input_model,
        "arguments_model": input_model,
        "output_model": output_model,
        "output_schema": output_model,
        "result_model": output_model,
        "handler": handler,
        "function": handler,
        "callback": handler,
        "allowed_agents": agents,
        "authorized_agents": agents,
        "agents": agents,
        "timeout_seconds": timeout_seconds,
        "timeout": timeout_seconds,
        "timeout_s": timeout_seconds,
        "version": "1.0.0",
        "category": "evaluation",
        "risk_level": "low",
        "side_effects": False,
        "idempotent": True,
        "enabled": True,
        "requires_confirmation": False,
        "metadata": {
            "offline": True,
            "simulated": True,
        },
    }

    return _construct_compatible(
        ToolDefinition,
        candidates,
    )


def build_simulated_mcp_harness() -> SimulatedMCPHarness:
    """Monta registry, política e executor reais."""

    registry = ToolRegistry()

    definitions = (
        build_tool_definition(
            name="mcp_health",
            description="Health check MCP simulado.",
            input_model=HealthInput,
            output_model=HealthOutput,
            handler=_health_handler,
            allowed_agents=(
                "supervisor",
                "rag_agent",
                "financial_agent",
            ),
            timeout_seconds=1.0,
        ),
        build_tool_definition(
            name="mcp_rag_search",
            description="RAG sintético sem chamada externa.",
            input_model=SimulatedRAGInput,
            output_model=SimulatedRAGOutput,
            handler=_rag_handler,
            allowed_agents=(
                "rag_agent",
                "supervisor",
            ),
            timeout_seconds=1.0,
        ),
        build_tool_definition(
            name="mcp_financial_calculate",
            description="Cálculo financeiro sintético.",
            input_model=SimulatedFinancialInput,
            output_model=SimulatedFinancialOutput,
            handler=_financial_handler,
            allowed_agents=(
                "financial_agent",
                "supervisor",
            ),
            timeout_seconds=1.0,
        ),
        build_tool_definition(
            name="mcp_controlled_error",
            description="Erro controlado para avaliação.",
            input_model=ControlledErrorInput,
            output_model=ControlledErrorOutput,
            handler=_controlled_error_handler,
            allowed_agents=("supervisor",),
            timeout_seconds=1.0,
        ),
        build_tool_definition(
            name="mcp_timeout",
            description="Timeout simulado.",
            input_model=TimeoutInput,
            output_model=TimeoutOutput,
            handler=_timeout_handler,
            allowed_agents=("supervisor",),
            timeout_seconds=0.05,
        ),
    )

    for definition in definitions:
        registry.register(
            definition
        )

    permission_policy = ToolPermissionPolicy()

    executor = ToolExecutor(
        registry=registry,
        permission_policy=permission_policy,
        max_workers=4,
    )

    return SimulatedMCPHarness(
        registry=registry,
        permission_policy=permission_policy,
        executor=executor,
    )


def status_value(
    result: ToolResult,
) -> str:
    """Retorna o status textual."""

    return str(
        getattr(
            result.status,
            "value",
            result.status,
        )
    )


def output_mapping(
    result: ToolResult,
) -> Mapping[str, Any]:
    """Normaliza a saída da ferramenta."""

    output = result.output

    if output is None:
        return {}

    if isinstance(
        output,
        BaseModel,
    ):
        return output.model_dump()

    if isinstance(
        output,
        Mapping,
    ):
        return dict(output)

    if hasattr(
        output,
        "model_dump",
    ):
        return dict(
            output.model_dump()
        )

    raise TypeError(
        "Saída MCP não suportada: "
        f"{type(output).__name__}"
    )


def error_code(
    result: ToolResult,
) -> str:
    """Retorna o código seguro de erro."""

    if result.error is None:
        return ""

    return str(
        getattr(
            result.error,
            "code",
            "",
        )
    )
