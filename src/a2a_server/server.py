"""Servidor A2A 1.x nativo da INNA.

Esta camada prova interoperabilidade do protocolo A2A oficial.
A integração com o runtime agentic interno permanece separada.
"""

from __future__ import annotations

from a2a.helpers import (
    get_message_text,
    new_text_message,
)
from a2a.server.agent_execution import (
    AgentExecutor,
    RequestContext,
)
from a2a.server.events import EventQueue
from a2a.server.request_handlers import (
    DefaultRequestHandler,
)
from a2a.server.routes import (
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
    Role,
)
from starlette.applications import Starlette

from src.a2a_server.adapter import (
    InnaNativeA2AAdapter,
)

INNA_A2A_SERVER_VERSION = "1.0.0"
INNA_A2A_PROTOCOL_VERSION = "1.0"

A2A_JSONRPC_PATH = "/a2a/jsonrpc/"


class InnaA2AExecutor(AgentExecutor):
    """Executor A2A conectado ao núcleo agentic INNA."""

    def __init__(
        self,
        adapter: InnaNativeA2AAdapter | None = None,
    ) -> None:
        self._adapter = (
            adapter
            or InnaNativeA2AAdapter()
        )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        message = context.message

        user_text = ""

        if message is not None:
            user_text = get_message_text(
                message
            ).strip()

        response_text = self._adapter.execute(
            user_text
        )

        response = new_text_message(
            text=response_text,
            context_id=context.context_id,
            task_id=context.task_id,
            role=Role.ROLE_AGENT,
        )

        await event_queue.enqueue_event(
            response
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        del context
        del event_queue

        return None


def build_agent_card(
    *,
    base_url: str = "http://127.0.0.1:8123",
) -> AgentCard:
    """Cria o Agent Card público da INNA."""

    normalized_base = base_url.rstrip("/")

    interface = AgentInterface(
        url=(
            normalized_base
            + A2A_JSONRPC_PATH
        ),
        protocol_binding="JSONRPC",
        protocol_version=(
            INNA_A2A_PROTOCOL_VERSION
        ),
    )

    skill = AgentSkill(
        id="inna-native-a2a",
        name="INNA Native A2A",
        description=(
            "Receives native A2A messages "
            "through the governed INNA gateway."
        ),
        tags=[
            "inna",
            "a2a",
            "agent-interoperability",
        ],
        examples=[
            "Check INNA A2A availability.",
        ],
        input_modes=[
            "text/plain",
        ],
        output_modes=[
            "text/plain",
        ],
    )

    return AgentCard(
        name="INNA A2A Gateway",
        description=(
            "Native Agent2Agent gateway "
            "for INNA interoperability."
        ),
        supported_interfaces=[
            interface,
        ],
        version=INNA_A2A_SERVER_VERSION,
        capabilities=AgentCapabilities(
            streaming=False,
            push_notifications=False,
            extended_agent_card=False,
        ),
        default_input_modes=[
            "text/plain",
        ],
        default_output_modes=[
            "text/plain",
        ],
        skills=[
            skill,
        ],
    )


def create_app(
    *,
    base_url: str = "http://127.0.0.1:8123",
    executor: AgentExecutor | None = None,
) -> Starlette:
    """Monta aplicação A2A usando as rotas oficiais."""

    agent_card = build_agent_card(
        base_url=base_url
    )

    request_handler = DefaultRequestHandler(
        agent_executor=(
            executor
            or InnaA2AExecutor()
        ),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    routes = []

    routes.extend(
        create_agent_card_routes(
            agent_card
        )
    )

    routes.extend(
        create_jsonrpc_routes(
            request_handler,
            rpc_url=A2A_JSONRPC_PATH,
        )
    )

    return Starlette(
        routes=routes
    )


app = create_app()


__all__ = [
    "A2A_JSONRPC_PATH",
    "INNA_A2A_PROTOCOL_VERSION",
    "INNA_A2A_SERVER_VERSION",
    "InnaA2AExecutor",
    "app",
    "build_agent_card",
    "create_app",
]
