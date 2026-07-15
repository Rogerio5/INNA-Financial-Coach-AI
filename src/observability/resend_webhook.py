"""
Processamento dos eventos de entrega enviados pelo Resend.

O módulo:
- valida e normaliza o evento já verificado pela API;
- mantém idempotência pelo identificador Svix;
- atualiza a auditoria da notificação pelo message ID do Resend;
- não armazena o conteúdo do e-mail.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError


load_dotenv(
    dotenv_path=Path(".env"),
    override=False,
)


NOME_TABELA_EVENTOS = "resend_webhook_events_inna"
NOME_TABELA_NOTIFICACOES = "llm_alert_notifications_inna"


STATUS_POR_EVENTO = {
    "email.sent": "enviado",
    "email.delivered": "entregue",
    "email.delivery_delayed": "atrasado",
    "email.bounced": "devolvido",
    "email.failed": "falhou",
    "email.suppressed": "suprimido",
    "email.complained": "reclamacao",
    "email.opened": "aberto_email",
    "email.clicked": "clicado",
}


def _database_url() -> str:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não configurada."
        )

    return database_url


def _criar_engine():
    return create_engine(
        _database_url(),
        pool_pre_ping=True,
    )


def inicializar_tabelas_resend_webhook() -> dict[str, Any]:
    """
    Cria a tabela de idempotência e acrescenta os campos
    de entrega à auditoria existente.
    """
    try:
        engine = _criar_engine()

        criar_eventos = text(f"""
            CREATE TABLE IF NOT EXISTS {NOME_TABELA_EVENTOS} (
                id BIGSERIAL PRIMARY KEY,

                svix_id VARCHAR(255) NOT NULL UNIQUE,
                evento_tipo VARCHAR(120) NOT NULL,
                provider_message_id VARCHAR(255),

                recebido_em TIMESTAMPTZ NOT NULL
                    DEFAULT NOW(),

                processado BOOLEAN NOT NULL
                    DEFAULT FALSE,

                processado_em TIMESTAMPTZ,

                resultado VARCHAR(50),
                erro_mensagem TEXT,

                metadados_json JSONB NOT NULL
                    DEFAULT '{{}}'::jsonb
            );
        """)

        alteracoes = [
            text(f"""
                ALTER TABLE {NOME_TABELA_NOTIFICACOES}
                ADD COLUMN IF NOT EXISTS
                status_entrega VARCHAR(50);
            """),
            text(f"""
                ALTER TABLE {NOME_TABELA_NOTIFICACOES}
                ADD COLUMN IF NOT EXISTS
                evento_provider VARCHAR(120);
            """),
            text(f"""
                ALTER TABLE {NOME_TABELA_NOTIFICACOES}
                ADD COLUMN IF NOT EXISTS
                entregue_em TIMESTAMPTZ;
            """),
            text(f"""
                ALTER TABLE {NOME_TABELA_NOTIFICACOES}
                ADD COLUMN IF NOT EXISTS
                devolvido_em TIMESTAMPTZ;
            """),
            text(f"""
                ALTER TABLE {NOME_TABELA_NOTIFICACOES}
                ADD COLUMN IF NOT EXISTS
                webhook_recebido_em TIMESTAMPTZ;
            """),
            text(f"""
                ALTER TABLE {NOME_TABELA_NOTIFICACOES}
                ADD COLUMN IF NOT EXISTS
                motivo_entrega TEXT;
            """),
        ]

        indices = [
            text(f"""
                CREATE INDEX IF NOT EXISTS
                idx_{NOME_TABELA_EVENTOS}_message_id
                ON {NOME_TABELA_EVENTOS}
                (provider_message_id);
            """),
            text(f"""
                CREATE INDEX IF NOT EXISTS
                idx_{NOME_TABELA_EVENTOS}_tipo
                ON {NOME_TABELA_EVENTOS}
                (evento_tipo);
            """),
        ]

        with engine.begin() as connection:
            connection.execute(criar_eventos)

            for comando in alteracoes:
                connection.execute(comando)

            for indice in indices:
                connection.execute(indice)

        engine.dispose()

        return {
            "ok": True,
            "message": "Estrutura do webhook inicializada.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (
                "Erro ao inicializar webhook: "
                f"{exc}"
            ),
        }


def extrair_message_id(
    evento: dict[str, Any],
) -> str | None:
    """
    Extrai o identificador da mensagem de diferentes
    formatos possíveis do evento.
    """
    data = evento.get("data") or {}

    return (
        data.get("email_id")
        or data.get("id")
        or evento.get("email_id")
        or evento.get("message_id")
    )


def extrair_motivo(
    evento: dict[str, Any],
) -> str | None:
    data = evento.get("data") or {}

    candidatos = [
        data.get("reason"),
        data.get("message"),
        data.get("error"),
        data.get("bounce"),
        evento.get("reason"),
    ]

    for valor in candidatos:
        if valor:
            if isinstance(valor, str):
                return valor[:2000]

            return json.dumps(
                valor,
                ensure_ascii=False,
                default=str,
            )[:2000]

    return None


def processar_evento_resend(
    *,
    svix_id: str,
    evento: dict[str, Any],
) -> dict[str, Any]:
    """
    Persiste e processa um evento já autenticado.
    """
    inicializacao = (
        inicializar_tabelas_resend_webhook()
    )

    if not inicializacao.get("ok"):
        return inicializacao

    evento_tipo = str(
        evento.get("type", "desconhecido")
    )

    provider_message_id = extrair_message_id(
        evento
    )

    status_entrega = STATUS_POR_EVENTO.get(
        evento_tipo,
        evento_tipo.replace("email.", ""),
    )

    motivo = extrair_motivo(evento)

    engine = _criar_engine()

    inserir_evento = text(f"""
        INSERT INTO {NOME_TABELA_EVENTOS} (
            svix_id,
            evento_tipo,
            provider_message_id,
            processado,
            metadados_json
        )
        VALUES (
            :svix_id,
            :evento_tipo,
            :provider_message_id,
            FALSE,
            CAST(:metadados_json AS JSONB)
        );
    """)

    try:
        with engine.begin() as connection:
            connection.execute(
                inserir_evento,
                {
                    "svix_id": svix_id,
                    "evento_tipo": evento_tipo,
                    "provider_message_id": (
                        provider_message_id
                    ),
                    "metadados_json": json.dumps(
                        {
                            "type": evento_tipo,
                            "message_id": (
                                provider_message_id
                            ),
                        },
                        ensure_ascii=False,
                    ),
                },
            )

    except IntegrityError:
        engine.dispose()

        return {
            "ok": True,
            "duplicado": True,
            "atualizado": False,
            "message": (
                "Evento já processado anteriormente."
            ),
        }

    try:
        atualizado = False

        if provider_message_id:
            atualizar_notificacao = text(f"""
                UPDATE {NOME_TABELA_NOTIFICACOES}
                SET
                    status_entrega = :status_entrega,
                    evento_provider = :evento_tipo,
                    webhook_recebido_em = NOW(),
                    entregue_em = CASE
                        WHEN :evento_tipo = 'email.delivered'
                        THEN COALESCE(entregue_em, NOW())
                        ELSE entregue_em
                    END,
                    devolvido_em = CASE
                        WHEN :evento_tipo IN (
                            'email.bounced',
                            'email.failed',
                            'email.suppressed'
                        )
                        THEN COALESCE(devolvido_em, NOW())
                        ELSE devolvido_em
                    END,
                    motivo_entrega = :motivo,
                    atualizado_em = NOW()
                WHERE provider_message_id =
                    :provider_message_id
                RETURNING id;
            """)

            with engine.begin() as connection:
                registro = connection.execute(
                    atualizar_notificacao,
                    {
                        "status_entrega": (
                            status_entrega
                        ),
                        "evento_tipo": evento_tipo,
                        "motivo": motivo,
                        "provider_message_id": (
                            provider_message_id
                        ),
                    },
                ).first()

            atualizado = registro is not None

        finalizar_evento = text(f"""
            UPDATE {NOME_TABELA_EVENTOS}
            SET
                processado = TRUE,
                processado_em = NOW(),
                resultado = :resultado
            WHERE svix_id = :svix_id;
        """)

        with engine.begin() as connection:
            connection.execute(
                finalizar_evento,
                {
                    "svix_id": svix_id,
                    "resultado": (
                        "notificacao_atualizada"
                        if atualizado
                        else "mensagem_nao_localizada"
                    ),
                },
            )

        engine.dispose()

        return {
            "ok": True,
            "duplicado": False,
            "atualizado": atualizado,
            "evento_tipo": evento_tipo,
            "status_entrega": status_entrega,
            "provider_message_id": (
                provider_message_id
            ),
            "message": (
                "Evento processado com sucesso."
            ),
        }

    except Exception as exc:
        registrar_erro = text(f"""
            UPDATE {NOME_TABELA_EVENTOS}
            SET
                processado = FALSE,
                resultado = 'erro',
                erro_mensagem = :erro
            WHERE svix_id = :svix_id;
        """)

        with engine.begin() as connection:
            connection.execute(
                registrar_erro,
                {
                    "svix_id": svix_id,
                    "erro": str(exc)[:4000],
                },
            )

        engine.dispose()

        return {
            "ok": False,
            "duplicado": False,
            "atualizado": False,
            "message": (
                "Erro ao processar evento: "
                f"{exc}"
            ),
        }


__all__ = [
    "NOME_TABELA_EVENTOS",
    "STATUS_POR_EVENTO",
    "inicializar_tabelas_resend_webhook",
    "extrair_message_id",
    "extrair_motivo",
    "processar_evento_resend",
]
