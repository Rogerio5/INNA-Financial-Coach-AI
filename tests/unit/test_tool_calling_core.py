from __future__ import annotations

import time

from pydantic import BaseModel, ConfigDict

from src.agent_tools.core import (
    ToolCall,
    ToolDefinition,
    ToolExecutionContext,
    ToolExecutor,
    ToolPermissionPolicy,
    ToolRegistrationError,
    ToolRegistry,
    ToolStatus,
)


class SumInput(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    first: int
    second: int


class SumOutput(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    result: int


def sum_handler(
    payload: SumInput,
    context: ToolExecutionContext,
) -> SumOutput:
    del context

    return SumOutput(result=(payload.first + payload.second))


def build_registry(
    *,
    timeout_seconds: float = 1.0,
) -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="calculate_sum",
            description=("Calcula a soma de dois números."),
            input_model=SumInput,
            output_model=SumOutput,
            handler=sum_handler,
            allowed_agents=frozenset(
                {
                    "financial_agent",
                }
            ),
            timeout_seconds=(timeout_seconds),
            tags=frozenset(
                {
                    "financial",
                    "deterministic",
                }
            ),
        )
    )

    return registry


def build_call(
    *,
    agent: str = "financial_agent",
    tool_name: str = "calculate_sum",
    arguments: dict | None = None,
) -> ToolCall:
    return ToolCall(
        tool_name=tool_name,
        arguments=(
            arguments
            or {
                "first": 2,
                "second": 3,
            }
        ),
        context=ToolExecutionContext(
            requested_by=agent,
            user_id="user-test",
            session_id="session-test",
            trace_id="trace-test",
        ),
    )


def test_execute_registered_tool_successfully():
    registry = build_registry()

    with ToolExecutor(registry=registry) as executor:
        result = executor.execute(build_call())

    assert result.ok is True
    assert result.status == ToolStatus.SUCCESS
    assert result.output == {
        "result": 5,
    }
    assert result.error is None


def test_rejects_invalid_tool_arguments():
    registry = build_registry()

    with ToolExecutor(registry=registry) as executor:
        result = executor.execute(
            build_call(
                arguments={
                    "first": "invalid",
                    "second": 3,
                }
            )
        )

    assert result.status == ToolStatus.VALIDATION_ERROR

    assert result.error.code == "tool_input_validation_error"


def test_denies_unauthorized_agent():
    registry = build_registry()

    with ToolExecutor(
        registry=registry,
        permission_policy=(ToolPermissionPolicy()),
    ) as executor:
        result = executor.execute(build_call(agent="report_agent"))

    assert result.status == ToolStatus.DENIED

    assert result.error.code == "tool_permission_denied"


def test_returns_not_found_for_unknown_tool():
    registry = build_registry()

    with ToolExecutor(registry=registry) as executor:
        result = executor.execute(build_call(tool_name="unknown_tool"))

    assert result.status == ToolStatus.NOT_FOUND

    assert result.error.code == "tool_not_found"


def test_validates_tool_output():
    registry = ToolRegistry()

    def invalid_output_handler(
        payload: SumInput,
        context: ToolExecutionContext,
    ):
        del payload
        del context

        return {
            "unexpected": 10,
        }

    registry.register(
        ToolDefinition(
            name="invalid_output",
            description=("Ferramenta com saída inválida."),
            input_model=SumInput,
            output_model=SumOutput,
            handler=invalid_output_handler,
            allowed_agents=frozenset(
                {
                    "financial_agent",
                }
            ),
        )
    )

    with ToolExecutor(registry=registry) as executor:
        result = executor.execute(build_call(tool_name="invalid_output"))

    assert result.status == ToolStatus.VALIDATION_ERROR

    assert result.error.code == "tool_output_validation_error"


def test_enforces_tool_timeout():
    registry = ToolRegistry()

    def slow_handler(
        payload: SumInput,
        context: ToolExecutionContext,
    ) -> SumOutput:
        del context

        time.sleep(0.05)

        return SumOutput(result=(payload.first + payload.second))

    registry.register(
        ToolDefinition(
            name="slow_tool",
            description=("Ferramenta propositalmente lenta."),
            input_model=SumInput,
            output_model=SumOutput,
            handler=slow_handler,
            allowed_agents=frozenset(
                {
                    "financial_agent",
                }
            ),
            timeout_seconds=0.01,
        )
    )

    with ToolExecutor(registry=registry) as executor:
        result = executor.execute(build_call(tool_name="slow_tool"))

    assert result.status == ToolStatus.TIMEOUT
    assert result.error.code == "tool_timeout"
    assert result.error.retryable is True


def test_rejects_duplicate_registration():
    registry = build_registry()

    try:
        registry.register(registry.get("calculate_sum"))
    except ToolRegistrationError:
        duplicate_rejected = True
    else:
        duplicate_rejected = False

    assert duplicate_rejected is True
