"""
Notificações administrativas dos alertas de LLM da INNA.

Envia somente informações técnicas, sem prompts, respostas
ou dados financeiros pessoais.
"""

from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

try:
    from email_sender import send_text_email
except ImportError:
    from src.email_sender import send_text_email


load_dotenv(
    dotenv_path=Path(".env"),
    override=True,
)


NOME_TABELA = "llm_alert_notifications_inna"

ORDEM_SEVERIDADE = {
    "informativa": 1,
    "baixa": 2,
    "media": 3,
    "alta": 4,
    "critica": 5,
}


def _get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não configurada."
        )

    return database_url


def _criar_engine():
    return create_engine(
        _get_database_url(),
        pool_pre_ping=True,
    )


def carregar_configuracao() -> dict[str, Any]:
    habilitado = (
        os.getenv(
            "LLM_ALERT_EMAIL_ENABLED",
            "false",
        )
        .strip()
        .lower()
        in {"true", "1", "yes", "sim", "on"}
    )

    destinatario = os.getenv(
        "LLM_ALERT_EMAIL_TO",
        "",
    ).strip()

    severidade_minima = os.getenv(
        "LLM_ALERT_MIN_SEVERITY",
        "alta",
    ).strip().lower()

    if severidade_minima not in ORDEM_SEVERIDADE:
        severidade_minima = "alta"

    return {
        "habilitado": habilitado,
        "destinatario": destinatario,
        "severidade_minima": severidade_minima,
        "resend_configurado": bool(
            os.getenv("RESEND_API_KEY")
        ),
    }


def mascarar_email(email: str) -> str:
    valor = str(email or "").strip()

    if "@" not in valor:
        return "***"

    usuario, dominio = valor.split("@", 1)

    if len(usuario) <= 2:
        usuario_mascarado = usuario[:1] + "***"
    else:
        usuario_mascarado = (
            usuario[:2]
            + "***"
            + usuario[-1:]
        )

    return f"{usuario_mascarado}@{dominio}"


def inicializar_tabela_notificacoes() -> dict[str, Any]:
    try:
        engine = _criar_engine()

        comando = text(f"""
            CREATE TABLE IF NOT EXISTS {NOME_TABELA} (
                id BIGSERIAL PRIMARY KEY,

                alerta_id BIGINT NOT NULL,
                canal VARCHAR(30) NOT NULL
                    DEFAULT 'email',

                status VARCHAR(30) NOT NULL
                    DEFAULT 'processando',

                destinatario_mascarado VARCHAR(255),
                assunto VARCHAR(255),

                tentativas INTEGER NOT NULL
                    DEFAULT 1,

                provider_message_id VARCHAR(255),

                criado_em TIMESTAMPTZ NOT NULL
                    DEFAULT NOW(),

                atualizado_em TIMESTAMPTZ NOT NULL
                    DEFAULT NOW(),

                enviado_em TIMESTAMPTZ,

                erro_tipo VARCHAR(150),
                erro_mensagem TEXT,

                CONSTRAINT uq_llm_alert_notification
                    UNIQUE (alerta_id, canal)
            );
        """)

        indice = text(f"""
            CREATE INDEX IF NOT EXISTS
            idx_{NOME_TABELA}_status
            ON {NOME_TABELA} (status);
        """)

        with engine.begin() as connection:
            connection.execute(comando)
            connection.execute(indice)

        engine.dispose()

        return {
            "ok": True,
            "message": (
                "Tabela de notificações inicializada."
            ),
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (
                "Erro ao inicializar tabela: "
                f"{exc}"
            ),
        }


def alerta_deve_ser_enviado(
    alerta: dict[str, Any],
    *,
    severidade_minima: str,
) -> bool:
    status = str(
        alerta.get("status", "aberto")
    ).lower()

    severidade = str(
        alerta.get(
            "severidade",
            "informativa",
        )
    ).lower()

    minimo = str(
        severidade_minima or "alta"
    ).lower()

    if minimo not in ORDEM_SEVERIDADE:
        minimo = "alta"

    return (
        status == "aberto"
        and ORDEM_SEVERIDADE.get(
            severidade,
            0,
        )
        >= ORDEM_SEVERIDADE[minimo]
    )


def montar_email_alerta(
    alerta: dict[str, Any],
) -> dict[str, str]:
    titulo = str(
        alerta.get(
            "titulo",
            "Alerta operacional",
        )
    )

    severidade = str(
        alerta.get(
            "severidade",
            "informativa",
        )
    ).title()

    categoria = str(
        alerta.get(
            "categoria",
            "observabilidade",
        )
    ).title()

    descricao = str(
        alerta.get("descricao", "")
    )

    recomendacao = str(
        alerta.get("recomendacao", "")
    )

    valor_atual = alerta.get(
        "valor_atual",
        0,
    )

    valor_limite = alerta.get(
        "valor_limite",
        0,
    )

    unidade = str(
        alerta.get("unidade", "")
    )

    assunto = (
        f"[INNA] Alerta {severidade}: {titulo}"
    )[:255]

    corpo_texto = f"""INNA Financial Coach AI

Novo alerta operacional detectado.

Alerta: {titulo}
Severidade: {severidade}
Categoria: {categoria}

Descrição:
{descricao}

Valor atual: {valor_atual} {unidade}
Limite configurado: {valor_limite} {unidade}

Recomendação:
{recomendacao}

Esta mensagem contém somente telemetria técnica.
Nenhum prompt, resposta ou dado financeiro pessoal foi incluído.
"""

    corpo_html = f"""
    <div style="
        max-width: 680px;
        margin: auto;
        font-family: Arial, sans-serif;
        color: #172033;
    ">
        <h2>🚨 Alerta operacional da INNA</h2>

        <p>
            A INNA Financial Coach AI detectou
            um novo alerta técnico.
        </p>

        <table style="
            width: 100%;
            border-collapse: collapse;
        ">
            <tr>
                <td><strong>Alerta</strong></td>
                <td>{html.escape(titulo)}</td>
            </tr>
            <tr>
                <td><strong>Severidade</strong></td>
                <td>{html.escape(severidade)}</td>
            </tr>
            <tr>
                <td><strong>Categoria</strong></td>
                <td>{html.escape(categoria)}</td>
            </tr>
            <tr>
                <td><strong>Valor atual</strong></td>
                <td>
                    {html.escape(str(valor_atual))}
                    {html.escape(unidade)}
                </td>
            </tr>
            <tr>
                <td><strong>Limite</strong></td>
                <td>
                    {html.escape(str(valor_limite))}
                    {html.escape(unidade)}
                </td>
            </tr>
        </table>

        <h3>Descrição</h3>
        <p>{html.escape(descricao)}</p>

        <h3>Recomendação</h3>
        <p>{html.escape(recomendacao)}</p>

        <hr>

        <p style="
            font-size: 12px;
            color: #667085;
        ">
            Esta notificação contém somente
            informações técnicas de observabilidade.
        </p>
    </div>
    """

    return {
        "assunto": assunto,
        "texto": corpo_texto,
        "html": corpo_html,
    }


def notificar_alerta_email(
    alerta: dict[str, Any],
) -> dict[str, Any]:
    configuracao = carregar_configuracao()

    if not configuracao["habilitado"]:
        return {
            "ok": True,
            "enviado": False,
            "ignorado": True,
            "message": (
                "Notificações por e-mail desabilitadas."
            ),
        }

    if not configuracao["destinatario"]:
        return {
            "ok": False,
            "enviado": False,
            "message": (
                "LLM_ALERT_EMAIL_TO não configurado."
            ),
        }

    if not alerta_deve_ser_enviado(
        alerta,
        severidade_minima=configuracao[
            "severidade_minima"
        ],
    ):
        return {
            "ok": True,
            "enviado": False,
            "ignorado": True,
            "message": (
                "Alerta não atende aos critérios "
                "de envio."
            ),
        }

    alerta_id = int(
        alerta.get("id", 0)
    )

    if alerta_id <= 0:
        return {
            "ok": False,
            "enviado": False,
            "message": (
                "O alerta precisa possuir um ID."
            ),
        }

    inicializacao = (
        inicializar_tabela_notificacoes()
    )

    if not inicializacao.get("ok"):
        return {
            **inicializacao,
            "enviado": False,
        }

    email = montar_email_alerta(alerta)
    engine = _criar_engine()

    inserir = text(f"""
        INSERT INTO {NOME_TABELA} (
            alerta_id,
            canal,
            status,
            destinatario_mascarado,
            assunto,
            tentativas
        )
        VALUES (
            :alerta_id,
            'email',
            'processando',
            :destinatario,
            :assunto,
            1
        );
    """)

    try:
        with engine.begin() as connection:
            connection.execute(
                inserir,
                {
                    "alerta_id": alerta_id,
                    "destinatario": mascarar_email(
                        configuracao[
                            "destinatario"
                        ]
                    ),
                    "assunto": email["assunto"],
                },
            )

    except IntegrityError:
        engine.dispose()

        return {
            "ok": True,
            "enviado": False,
            "duplicado": True,
            "message": (
                "Este alerta já foi processado "
                "por e-mail."
            ),
        }

    try:
        resultado_envio = send_text_email(
            to_email=configuracao[
                "destinatario"
            ],
            subject=email["assunto"],
            body=email["texto"],
            html_body=email["html"],
        )

        atualizar = text(f"""
            UPDATE {NOME_TABELA}
            SET
                status = 'enviado',
                provider_message_id =
                    :provider_message_id,
                enviado_em = NOW(),
                atualizado_em = NOW()
            WHERE alerta_id = :alerta_id
              AND canal = 'email';
        """)

        with engine.begin() as connection:
            connection.execute(
                atualizar,
                {
                    "alerta_id": alerta_id,
                    "provider_message_id": (
                        resultado_envio.get(
                            "message_id"
                        )
                    ),
                },
            )

        engine.dispose()

        return {
            "ok": True,
            "enviado": True,
            "duplicado": False,
            **resultado_envio,
        }

    except Exception as exc:
        atualizar_erro = text(f"""
            UPDATE {NOME_TABELA}
            SET
                status = 'falhou',
                erro_tipo = :erro_tipo,
                erro_mensagem = :erro_mensagem,
                atualizado_em = NOW()
            WHERE alerta_id = :alerta_id
              AND canal = 'email';
        """)

        with engine.begin() as connection:
            connection.execute(
                atualizar_erro,
                {
                    "alerta_id": alerta_id,
                    "erro_tipo": type(exc).__name__,
                    "erro_mensagem": str(exc),
                },
            )

        engine.dispose()

        return {
            "ok": False,
            "enviado": False,
            "duplicado": False,
            "message": str(exc),
        }


def avaliar_persistir_e_notificar_alertas(
    df,
    finops: dict[str, Any],
) -> dict[str, Any]:
    """
    Detecta, persiste e notifica somente alertas novos.

    Regras:
    - não notifica alertas duplicados;
    - não notifica alertas médios ou baixos;
    - registra cada tentativa na auditoria;
    - falha de e-mail não desfaz o alerta persistido.
    """
    try:
        try:
            from src.plataforma.observabilidade.llm_alerts import (
                avaliar_e_persistir_alertas,
            )
        except ImportError:
            from src.plataforma.observabilidade.llm_alerts import (
                avaliar_e_persistir_alertas,
            )

        resultado_alertas = (
            avaliar_e_persistir_alertas(
                df,
                finops,
            )
        )

        detectados = resultado_alertas.get(
            "alertas_detectados",
            [],
        )

        persistencias = resultado_alertas.get(
            "resultados_persistencia",
            [],
        )

        notificacoes: list[dict[str, Any]] = []

        for alerta, persistencia in zip(
            detectados,
            persistencias,
        ):
            if not persistencia.get("salvo"):
                notificacoes.append(
                    {
                        "ok": True,
                        "enviado": False,
                        "duplicado": bool(
                            persistencia.get(
                                "duplicado"
                            )
                        ),
                        "ignorado": True,
                        "codigo": alerta.get(
                            "codigo"
                        ),
                        "message": (
                            "Alerta não notificado porque "
                            "não foi criado um novo registro."
                        ),
                    }
                )
                continue

            alerta_persistido = {
                **alerta,
                "id": int(
                    persistencia["id"]
                ),
                "status": "aberto",
                "criado_em": persistencia.get(
                    "criado_em"
                ),
            }

            resultado_notificacao = (
                notificar_alerta_email(
                    alerta_persistido
                )
            )

            notificacoes.append(
                {
                    **resultado_notificacao,
                    "alerta_id": (
                        alerta_persistido["id"]
                    ),
                    "codigo": alerta.get(
                        "codigo"
                    ),
                    "severidade": alerta.get(
                        "severidade"
                    ),
                }
            )

        total_enviados = sum(
            1
            for item in notificacoes
            if item.get("enviado")
        )

        total_ignorados = sum(
            1
            for item in notificacoes
            if item.get("ignorado")
        )

        total_falhas = sum(
            1
            for item in notificacoes
            if (
                not item.get("ok")
                and not item.get("ignorado")
            )
        )

        return {
            **resultado_alertas,
            "notificacoes": notificacoes,
            "total_notificacoes_enviadas": (
                total_enviados
            ),
            "total_notificacoes_ignoradas": (
                total_ignorados
            ),
            "total_notificacoes_falhas": (
                total_falhas
            ),
            "ok_notificacoes": (
                total_falhas == 0
            ),
        }

    except Exception as exc:
        return {
            "ok": False,
            "ok_notificacoes": False,
            "alertas_detectados": [],
            "resultados_persistencia": [],
            "notificacoes": [],
            "total_detectados": 0,
            "total_salvos": 0,
            "total_duplicados": 0,
            "total_notificacoes_enviadas": 0,
            "total_notificacoes_ignoradas": 0,
            "total_notificacoes_falhas": 1,
            "message": (
                "Erro na automação de alertas: "
                f"{exc}"
            ),
        }


def reenviar_notificacao_email(
    *,
    notificacao_id: int,
    max_tentativas: int = 3,
) -> dict[str, Any]:
    """
    Reenvia uma notificação que apresentou falha.

    Proteções:
    - aceita somente notificações com falha;
    - bloqueia e-mails já entregues;
    - limita o número total de tentativas;
    - atualiza o provider_message_id;
    - aguarda o novo webhook do Resend.
    """
    inicializacao = (
        inicializar_tabela_notificacoes()
    )

    if not inicializacao.get("ok"):
        return {
            **inicializacao,
            "reenviado": False,
        }

    configuracao = carregar_configuracao()

    if not configuracao.get("habilitado"):
        return {
            "ok": False,
            "reenviado": False,
            "message": (
                "Notificações por e-mail "
                "estão desabilitadas."
            ),
        }

    if not configuracao.get("destinatario"):
        return {
            "ok": False,
            "reenviado": False,
            "message": (
                "LLM_ALERT_EMAIL_TO "
                "não configurado."
            ),
        }

    try:
        notificacao_id = int(notificacao_id)
        max_tentativas = max(
            int(max_tentativas),
            1,
        )
    except (TypeError, ValueError):
        return {
            "ok": False,
            "reenviado": False,
            "message": "Identificador inválido.",
        }

    engine = _criar_engine()

    consulta = text(f"""
        SELECT
            n.id AS notificacao_id,
            n.alerta_id,
            n.status,
            n.status_entrega,
            n.tentativas,
            n.provider_message_id,

            a.id,
            a.codigo,
            a.titulo,
            a.descricao,
            a.categoria,
            a.severidade,
            a.status AS alerta_status,
            a.valor_atual,
            a.valor_limite,
            a.unidade,
            a.modelo,
            a.operacao,
            a.recomendacao,
            a.criado_em

        FROM {NOME_TABELA} n

        INNER JOIN llm_alerts_inna a
            ON a.id = n.alerta_id

        WHERE n.id = :notificacao_id
        LIMIT 1;
    """)

    with engine.connect() as connection:
        registro = (
            connection.execute(
                consulta,
                {
                    "notificacao_id": (
                        notificacao_id
                    ),
                },
            )
            .mappings()
            .first()
        )

    if not registro:
        engine.dispose()

        return {
            "ok": False,
            "reenviado": False,
            "message": (
                "Notificação não encontrada."
            ),
        }

    status_entrega = str(
        registro.get("status_entrega")
        or ""
    ).strip().lower()

    status_envio = str(
        registro.get("status")
        or ""
    ).strip().lower()

    status_permitidos = {
        "falhou",
        "devolvido",
        "suprimido",
    }

    if status_entrega == "entregue":
        engine.dispose()

        return {
            "ok": False,
            "reenviado": False,
            "message": (
                "E-mails entregues não podem "
                "ser reenviados."
            ),
        }

    if (
        status_entrega not in status_permitidos
        and status_envio not in {
            "erro",
            "falhou",
        }
    ):
        engine.dispose()

        return {
            "ok": False,
            "reenviado": False,
            "message": (
                "O reenvio é permitido somente "
                "para notificações com falha."
            ),
        }

    tentativas = int(
        registro.get("tentativas")
        or 0
    )

    if tentativas >= max_tentativas:
        engine.dispose()

        return {
            "ok": False,
            "reenviado": False,
            "limite_atingido": True,
            "message": (
                "Limite máximo de tentativas "
                f"atingido: {max_tentativas}."
            ),
        }

    alerta = dict(registro)

    email = montar_email_alerta(alerta)

    bloquear = text(f"""
        UPDATE {NOME_TABELA}
        SET
            status = 'processando',
            tentativas = tentativas + 1,
            atualizado_em = NOW()
        WHERE id = :notificacao_id
          AND tentativas < :max_tentativas
          AND (
              status IN ('erro', 'falhou')
              OR status_entrega IN (
                  'falhou',
                  'devolvido',
                  'suprimido'
              )
          )
        RETURNING tentativas;
    """)

    with engine.begin() as connection:
        bloqueio = (
            connection.execute(
                bloquear,
                {
                    "notificacao_id": (
                        notificacao_id
                    ),
                    "max_tentativas": (
                        max_tentativas
                    ),
                },
            )
            .mappings()
            .first()
        )

    if not bloqueio:
        engine.dispose()

        return {
            "ok": False,
            "reenviado": False,
            "message": (
                "A notificação já está sendo "
                "processada ou não pode ser reenviada."
            ),
        }

    try:
        resultado_envio = send_text_email(
            to_email=configuracao[
                "destinatario"
            ],
            subject=email["assunto"],
            body=email["texto"],
            html_body=email["html"],
        )

        provider_message_id = (
            resultado_envio.get(
                "provider_message_id"
            )
            or resultado_envio.get("id")
            or resultado_envio.get(
                "message_id"
            )
        )

        atualizar_sucesso = text(f"""
            UPDATE {NOME_TABELA}
            SET
                status = 'enviado',
                status_entrega = 'enviado',
                evento_provider = NULL,
                provider_message_id =
                    :provider_message_id,
                enviado_em = NOW(),
                entregue_em = NULL,
                devolvido_em = NULL,
                webhook_recebido_em = NULL,
                motivo_entrega = NULL,
                erro_tipo = NULL,
                erro_mensagem = NULL,
                atualizado_em = NOW()
            WHERE id = :notificacao_id;
        """)

        with engine.begin() as connection:
            connection.execute(
                atualizar_sucesso,
                {
                    "notificacao_id": (
                        notificacao_id
                    ),
                    "provider_message_id": (
                        provider_message_id
                    ),
                },
            )

        engine.dispose()

        return {
            "ok": True,
            "reenviado": True,
            "notificacao_id": notificacao_id,
            "tentativas": int(
                bloqueio["tentativas"]
            ),
            "provider_message_id": (
                provider_message_id
            ),
            "message": (
                "Notificação reenviada "
                "com sucesso."
            ),
        }

    except Exception as exc:
        atualizar_erro = text(f"""
            UPDATE {NOME_TABELA}
            SET
                status = 'erro',
                status_entrega = 'falhou',
                erro_tipo = :erro_tipo,
                erro_mensagem = :erro_mensagem,
                atualizado_em = NOW()
            WHERE id = :notificacao_id;
        """)

        with engine.begin() as connection:
            connection.execute(
                atualizar_erro,
                {
                    "notificacao_id": (
                        notificacao_id
                    ),
                    "erro_tipo": (
                        type(exc).__name__
                    ),
                    "erro_mensagem": (
                        str(exc)[:4000]
                    ),
                },
            )

        engine.dispose()

        return {
            "ok": False,
            "reenviado": False,
            "notificacao_id": notificacao_id,
            "message": (
                "Falha ao reenviar: "
                f"{exc}"
            ),
        }



def carregar_notificacoes(
    *,
    limite: int = 500,
) -> dict[str, Any]:
    inicializacao = (
        inicializar_tabela_notificacoes()
    )

    if not inicializacao.get("ok"):
        return {
            **inicializacao,
            "df": pd.DataFrame(),
        }

    try:
        engine = _criar_engine()

        consulta = text(f"""
            SELECT
                id,
                alerta_id,
                canal,
                status,
                destinatario_mascarado,
                assunto,
                tentativas,
                provider_message_id,
                criado_em,
                enviado_em,
                atualizado_em,
                erro_tipo,
                erro_mensagem,
                status_entrega,
                evento_provider,
                entregue_em,
                devolvido_em,
                webhook_recebido_em,
                motivo_entrega
            FROM {NOME_TABELA}
            ORDER BY criado_em DESC
            LIMIT :limite;
        """)

        with engine.connect() as connection:
            df = pd.read_sql(
                consulta,
                connection,
                params={
                    "limite": max(
                        int(limite),
                        1,
                    ),
                },
            )

        engine.dispose()

        return {
            "ok": True,
            "df": df,
            "total": len(df),
            "message": (
                "Notificações carregadas."
            ),
        }

    except Exception as exc:
        return {
            "ok": False,
            "df": pd.DataFrame(),
            "total": 0,
            "message": (
                "Erro ao carregar notificações: "
                f"{exc}"
            ),
        }


__all__ = [
    "NOME_TABELA",
    "ORDEM_SEVERIDADE",
    "carregar_configuracao",
    "mascarar_email",
    "inicializar_tabela_notificacoes",
    "alerta_deve_ser_enviado",
    "montar_email_alerta",
    "notificar_alerta_email",
    "avaliar_persistir_e_notificar_alertas",
    "carregar_notificacoes",
    "reenviar_notificacao_email",
]
