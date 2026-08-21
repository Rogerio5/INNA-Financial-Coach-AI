from __future__ import annotations

import re
from typing import Literal
from uuid import uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from src.compartilhado.agent_tools.core import (
    ToolDefinition,
    ToolExecutionContext,
)

PREPARE_FINANCIAL_EMAIL_TOOL_NAME = "preparar_email_financeiro"

PREPARE_TELEGRAM_MESSAGE_TOOL_NAME = "preparar_mensagem_telegram"

MAX_SUBJECT_LENGTH = 180
MAX_MESSAGE_LENGTH = 10_000

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CommunicationPreparationError(RuntimeError):
    """Erro seguro na preparação de comunicação."""


class PrepararEmailFinanceiroInput(BaseModel):
    """Entrada pública para preparar um e-mail."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    destinatario: str = Field(
        min_length=5,
        max_length=320,
    )
    assunto: str = Field(
        min_length=1,
        max_length=MAX_SUBJECT_LENGTH,
    )
    corpo: str = Field(
        min_length=1,
        max_length=MAX_MESSAGE_LENGTH,
    )
    html_corpo: str | None = Field(
        default=None,
        max_length=MAX_MESSAGE_LENGTH,
    )
    idioma: str = Field(
        default="pt",
        min_length=2,
        max_length=12,
    )

    @field_validator("destinatario")
    @classmethod
    def validar_destinatario(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip().lower()

        if not _EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError("Endereço de e-mail inválido.")

        return normalized


class PrepararMensagemTelegramInput(BaseModel):
    """Entrada pública para preparar Telegram."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    chat_id: str = Field(
        min_length=1,
        max_length=100,
    )
    mensagem: str = Field(
        min_length=1,
        max_length=4096,
    )
    idioma: str = Field(
        default="pt",
        min_length=2,
        max_length=12,
    )

    @field_validator("chat_id")
    @classmethod
    def validar_chat_id(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not re.fullmatch(
            r"-?[0-9]{1,30}",
            normalized,
        ):
            raise ValueError("chat_id do Telegram inválido.")

        return normalized


class ComunicacaoPendenteOutput(BaseModel):
    """Resultado seguro da preparação."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    preparation_id: str
    review_id: str
    review_persisted: Literal[True]
    channel: Literal[
        "email",
        "telegram",
    ]
    status: Literal["pending_approval"]
    requires_human_approval: Literal[True]
    sent: Literal[False]

    recipient_masked: str
    content_length: int = Field(ge=1)
    language: str

    trace_id: str | None = None
    requested_by: str

    available_actions: tuple[
        Literal[
            "approve",
            "correct",
            "reject",
            "cancel",
        ],
        ...,
    ] = (
        "approve",
        "correct",
        "reject",
        "cancel",
    )


def _mascarar_email(
    email: str,
) -> str:
    local, domain = email.split("@", 1)

    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + ("*" * min(len(local) - 2, 8)) + local[-1]

    return f"{masked_local}@{domain}"


def _mascarar_chat_id(
    chat_id: str,
) -> str:
    prefix = "-" if chat_id.startswith("-") else ""
    digits = chat_id.lstrip("-")

    if len(digits) <= 4:
        return prefix + ("*" * len(digits))

    return prefix + ("*" * (len(digits) - 4)) + digits[-4:]


def registrar_revisao_pendente(
    interrupt_payload: dict[str, object],
) -> object:
    """
    Importa o serviço HITL apenas no momento da execução.

    Isso evita o ciclo:
    catalog -> communication_tools -> human_review
    -> graph -> nodes -> runtime -> catalog.
    """
    from src.plataforma.governanca.human_review.service import (
        registrar_revisao_pendente as persistir,
    )

    return persistir(interrupt_payload)


def _resolver_thread_id(
    context: ToolExecutionContext,
    preparation_id: str,
) -> str:
    return context.session_id or context.trace_id or preparation_id


def _persistir_revisao_comunicacao(
    *,
    preparation_id: str,
    channel: Literal["email", "telegram"],
    recipient: str,
    content: dict[str, object],
    language: str,
    context: ToolExecutionContext,
) -> str:
    """
    Registra uma revisão humana persistente.

    O conteúdo permanece no payload HITL para que
    o administrador possa revisar e corrigir antes
    de qualquer envio.
    """
    review_id = preparation_id
    thread_id = _resolver_thread_id(
        context,
        preparation_id,
    )

    interrupt_payload = {
        "type": "human_review",
        "review_id": review_id,
        "thread_id": thread_id,
        "status": "pending",
        "requested_by": context.requested_by,
        "reason": (f"Aprovação obrigatória antes do envio por {channel}."),
        "trigger": "mcp_communication_preparation",
        "risk_level": "medium",
        "payload": {
            "operation": "send_communication",
            "channel": channel,
            "recipient": recipient,
            "content": content,
            "language": language,
            "sent": False,
            "source": "mcp",
            "trace_id": context.trace_id,
        },
        "allowed_actions": [
            "approve",
            "correct",
            "reject",
            "cancel",
        ],
    }

    registrar_revisao_pendente(interrupt_payload)

    return review_id


def executar_preparacao_email_financeiro(
    payload: PrepararEmailFinanceiroInput,
    context: ToolExecutionContext,
) -> ComunicacaoPendenteOutput:
    """
    Prepara e valida um e-mail.

    Esta função não envia o e-mail.
    """
    preparation_id = f"email-{uuid4().hex}"

    review_id = _persistir_revisao_comunicacao(
        preparation_id=preparation_id,
        channel="email",
        recipient=payload.destinatario,
        content={
            "subject": payload.assunto,
            "body": payload.corpo,
            "html_body": payload.html_corpo,
        },
        language=payload.idioma,
        context=context,
    )

    return ComunicacaoPendenteOutput(
        preparation_id=preparation_id,
        review_id=review_id,
        review_persisted=True,
        channel="email",
        status="pending_approval",
        requires_human_approval=True,
        sent=False,
        recipient_masked=_mascarar_email(payload.destinatario),
        content_length=len(payload.corpo),
        language=payload.idioma,
        trace_id=context.trace_id,
        requested_by=context.requested_by,
    )


def executar_preparacao_mensagem_telegram(
    payload: PrepararMensagemTelegramInput,
    context: ToolExecutionContext,
) -> ComunicacaoPendenteOutput:
    """
    Prepara e valida uma mensagem Telegram.

    Esta função não envia a mensagem.
    """
    preparation_id = f"telegram-{uuid4().hex}"

    review_id = _persistir_revisao_comunicacao(
        preparation_id=preparation_id,
        channel="telegram",
        recipient=payload.chat_id,
        content={
            "message": payload.mensagem,
        },
        language=payload.idioma,
        context=context,
    )

    return ComunicacaoPendenteOutput(
        preparation_id=preparation_id,
        review_id=review_id,
        review_persisted=True,
        channel="telegram",
        status="pending_approval",
        requires_human_approval=True,
        sent=False,
        recipient_masked=_mascarar_chat_id(payload.chat_id),
        content_length=len(payload.mensagem),
        language=payload.idioma,
        trace_id=context.trace_id,
        requested_by=context.requested_by,
    )


def criar_definicao_preparar_email_financeiro(
    *,
    timeout_seconds: float = 2.0,
) -> ToolDefinition:
    """Cria a ferramenta formal de e-mail."""
    return ToolDefinition(
        name=PREPARE_FINANCIAL_EMAIL_TOOL_NAME,
        description=(
            "Prepara e valida um e-mail financeiro "
            "para aprovação humana. Não realiza envio."
        ),
        input_model=PrepararEmailFinanceiroInput,
        output_model=ComunicacaoPendenteOutput,
        handler=executar_preparacao_email_financeiro,
        allowed_agents=frozenset(
            {
                "communication_agent",
                "report_agent",
            }
        ),
        timeout_seconds=timeout_seconds,
        idempotent=False,
        sensitive_output=True,
        tags=frozenset(
            {
                "communication",
                "email",
                "human_approval",
                "no_direct_send",
            }
        ),
    )


def criar_definicao_preparar_mensagem_telegram(
    *,
    timeout_seconds: float = 2.0,
) -> ToolDefinition:
    """Cria a ferramenta formal de Telegram."""
    return ToolDefinition(
        name=PREPARE_TELEGRAM_MESSAGE_TOOL_NAME,
        description=(
            "Prepara e valida uma mensagem Telegram "
            "para aprovação humana. Não realiza envio."
        ),
        input_model=PrepararMensagemTelegramInput,
        output_model=ComunicacaoPendenteOutput,
        handler=executar_preparacao_mensagem_telegram,
        allowed_agents=frozenset(
            {
                "communication_agent",
            }
        ),
        timeout_seconds=timeout_seconds,
        idempotent=False,
        sensitive_output=True,
        tags=frozenset(
            {
                "communication",
                "telegram",
                "human_approval",
                "no_direct_send",
            }
        ),
    )


__all__ = [
    "CommunicationPreparationError",
    "ComunicacaoPendenteOutput",
    "PREPARE_FINANCIAL_EMAIL_TOOL_NAME",
    "PREPARE_TELEGRAM_MESSAGE_TOOL_NAME",
    "PrepararEmailFinanceiroInput",
    "PrepararMensagemTelegramInput",
    "criar_definicao_preparar_email_financeiro",
    "criar_definicao_preparar_mensagem_telegram",
    "executar_preparacao_email_financeiro",
    "executar_preparacao_mensagem_telegram",
]
