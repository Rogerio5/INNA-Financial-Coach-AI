"""
Timeline distribuída das execuções da INNA.

Cada interação recebe um trace_id único. As etapas da execução
são registradas em ordem, permitindo acompanhar o caminho:

pergunta -> memória -> router -> Tool -> RAG -> prompt ->
Gemini -> formatação -> resposta.

A observabilidade é não bloqueante: falhas no registro não devem
interromper a resposta principal da INNA.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, TypeVar


T = TypeVar("T")


ETAPAS_TIMELINE = {
    "pergunta_recebida": 10,
    "memoria_consultada": 20,
    "router_executado": 30,
    "tool_executada": 40,
    "rag_consultado": 50,
    "prompt_montado": 60,
    "gemini_executado": 70,
    "resposta_formatada": 80,
    "resposta_entregue": 90,
}


LABELS_ETAPAS = {
    "pergunta_recebida": "Pergunta recebida",
    "memoria_consultada": "Memória consultada",
    "router_executado": "Router executado",
    "tool_executada": "Tool financeira executada",
    "rag_consultado": "Busca RAG concluída",
    "prompt_montado": "Prompt estruturado",
    "gemini_executado": "Gemini executado",
    "resposta_formatada": "Resposta formatada",
    "resposta_entregue": "Resposta entregue",
}


def gerar_trace_id() -> str:
    """
    Gera identificador único para uma execução completa.
    """
    return str(uuid.uuid4())


def _carregar_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        try:
            from dotenv import load_dotenv

            load_dotenv(
                dotenv_path=Path(".env")
            )

            database_url = os.getenv(
                "DATABASE_URL"
            )
        except Exception:
            database_url = None

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não encontrada."
        )

    return database_url


def _conectar_postgres():
    try:
        import psycopg2
    except ImportError as exc:
        raise RuntimeError(
            "Pacote psycopg2 não instalado."
        ) from exc

    return psycopg2.connect(
        _carregar_database_url()
    )


def preparar_tabela_timeline(
    conn=None,
) -> dict[str, Any]:
    """
    Cria a tabela e os índices da Timeline.
    """
    conexao_propria = conn is None

    try:
        if conexao_propria:
            conn = _conectar_postgres()

        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS timeline_eventos_inna (
                id BIGSERIAL PRIMARY KEY,
                trace_id UUID NOT NULL,
                usuario_id TEXT,
                sessao_id TEXT,
                pergunta TEXT,
                etapa TEXT NOT NULL,
                etapa_label TEXT NOT NULL,
                ordem INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'sucesso',
                inicio_em TIMESTAMPTZ,
                fim_em TIMESTAMPTZ,
                duracao_ms DOUBLE PRECISION,
                mensagem TEXT,
                erro TEXT,
                origem TEXT DEFAULT 'dashboard_rag',
                metadata JSONB DEFAULT '{}'::jsonb,
                criado_em TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_timeline_trace_ordem
            ON timeline_eventos_inna (
                trace_id,
                ordem
            );
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_timeline_usuario_data
            ON timeline_eventos_inna (
                usuario_id,
                criado_em DESC
            );
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_timeline_etapa_status
            ON timeline_eventos_inna (
                etapa,
                status,
                criado_em DESC
            );
        """)

        conn.commit()
        cur.close()

        if conexao_propria:
            conn.close()

        return {
            "ok": True,
            "message": "Tabela da Timeline preparada.",
        }

    except Exception as exc:
        try:
            if conn:
                conn.rollback()
        except Exception:
            pass

        try:
            if conexao_propria and conn:
                conn.close()
        except Exception:
            pass

        return {
            "ok": False,
            "message": (
                "Erro ao preparar Timeline: "
                f"{exc}"
            ),
        }


def registrar_evento_timeline(
    *,
    trace_id: str,
    etapa: str,
    usuario_id: str | None = None,
    sessao_id: str | None = None,
    pergunta: str | None = None,
    status: str = "sucesso",
    inicio_em: datetime | None = None,
    fim_em: datetime | None = None,
    duracao_ms: float | None = None,
    mensagem: str | None = None,
    erro: str | None = None,
    origem: str = "dashboard_rag",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Registra uma etapa sem bloquear o fluxo principal.
    """
    conn = None

    try:
        if not trace_id:
            raise ValueError(
                "trace_id não informado."
            )

        if etapa not in ETAPAS_TIMELINE:
            raise ValueError(
                f"Etapa desconhecida: {etapa}"
            )

        status_normalizado = str(
            status or "sucesso"
        ).lower()

        status_permitidos = {
            "iniciado",
            "sucesso",
            "falha",
            "ignorado",
        }

        if status_normalizado not in status_permitidos:
            raise ValueError(
                f"Status inválido: {status}"
            )

        conn = _conectar_postgres()

        preparacao = preparar_tabela_timeline(
            conn
        )

        if not preparacao.get("ok"):
            conn.close()
            return preparacao

        cur = conn.cursor()

        inicio = inicio_em
        fim = fim_em

        if inicio and inicio.tzinfo is None:
            inicio = inicio.replace(
                tzinfo=timezone.utc
            )

        if fim and fim.tzinfo is None:
            fim = fim.replace(
                tzinfo=timezone.utc
            )

        cur.execute("""
            INSERT INTO timeline_eventos_inna (
                trace_id,
                usuario_id,
                sessao_id,
                pergunta,
                etapa,
                etapa_label,
                ordem,
                status,
                inicio_em,
                fim_em,
                duracao_ms,
                mensagem,
                erro,
                origem,
                metadata
            )
            VALUES (
                %s::uuid,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s::jsonb
            )
            RETURNING id;
        """, (
            trace_id,
            usuario_id,
            sessao_id,
            pergunta,
            etapa,
            LABELS_ETAPAS[etapa],
            ETAPAS_TIMELINE[etapa],
            status_normalizado,
            inicio,
            fim,
            duracao_ms,
            mensagem,
            erro,
            origem,
            json.dumps(
                metadata or {},
                ensure_ascii=False,
                default=str,
            ),
        ))

        evento_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return {
            "ok": True,
            "evento_id": evento_id,
            "trace_id": trace_id,
            "etapa": etapa,
            "message": "Etapa registrada na Timeline.",
        }

    except Exception as exc:
        try:
            if conn:
                conn.rollback()
                conn.close()
        except Exception:
            pass

        return {
            "ok": False,
            "evento_id": None,
            "trace_id": trace_id,
            "etapa": etapa,
            "message": (
                "Falha não bloqueante na Timeline: "
                f"{exc}"
            ),
        }


def executar_etapa_timeline(
    *,
    trace_id: str,
    etapa: str,
    funcao: Callable[..., T],
    argumentos: dict[str, Any] | None = None,
    usuario_id: str | None = None,
    sessao_id: str | None = None,
    pergunta: str | None = None,
    origem: str = "dashboard_rag",
    metadata: dict[str, Any] | None = None,
    propagar_erro: bool = True,
) -> dict[str, Any]:
    """
    Executa uma função, mede o tempo e registra o resultado.

    O retorno contém:
    - ok;
    - resultado;
    - erro;
    - duração;
    - registro da Timeline.
    """
    inicio_perf = perf_counter()
    inicio_data = datetime.now(
        timezone.utc
    )

    resultado_funcao = None
    erro_texto = None
    status = "sucesso"

    try:
        resultado_funcao = funcao(
            **(argumentos or {})
        )

    except Exception as exc:
        status = "falha"
        erro_texto = str(exc)

        duracao_ms = round(
            (perf_counter() - inicio_perf)
            * 1000,
            3,
        )

        fim_data = datetime.now(
            timezone.utc
        )

        registro = registrar_evento_timeline(
            trace_id=trace_id,
            etapa=etapa,
            usuario_id=usuario_id,
            sessao_id=sessao_id,
            pergunta=pergunta,
            status=status,
            inicio_em=inicio_data,
            fim_em=fim_data,
            duracao_ms=duracao_ms,
            mensagem=(
                f"Falha durante a etapa "
                f"{LABELS_ETAPAS[etapa]}."
            ),
            erro=erro_texto,
            origem=origem,
            metadata=metadata,
        )

        if propagar_erro:
            raise

        return {
            "ok": False,
            "resultado": None,
            "erro": erro_texto,
            "duracao_ms": duracao_ms,
            "timeline": registro,
        }

    duracao_ms = round(
        (perf_counter() - inicio_perf)
        * 1000,
        3,
    )

    fim_data = datetime.now(
        timezone.utc
    )

    registro = registrar_evento_timeline(
        trace_id=trace_id,
        etapa=etapa,
        usuario_id=usuario_id,
        sessao_id=sessao_id,
        pergunta=pergunta,
        status=status,
        inicio_em=inicio_data,
        fim_em=fim_data,
        duracao_ms=duracao_ms,
        mensagem=(
            f"Etapa concluída com sucesso: "
            f"{LABELS_ETAPAS[etapa]}."
        ),
        erro=None,
        origem=origem,
        metadata=metadata,
    )

    return {
        "ok": True,
        "resultado": resultado_funcao,
        "erro": None,
        "duracao_ms": duracao_ms,
        "timeline": registro,
    }


def carregar_timeline_trace(
    trace_id: str,
) -> dict[str, Any]:
    """
    Carrega todas as etapas de uma execução.
    """
    try:
        import pandas as pd
        from sqlalchemy import create_engine, text

        engine = create_engine(
            _carregar_database_url(),
            pool_pre_ping=True,
        )

        query = text("""
            SELECT
                id,
                trace_id,
                usuario_id,
                sessao_id,
                pergunta,
                etapa,
                etapa_label,
                ordem,
                status,
                inicio_em,
                fim_em,
                duracao_ms,
                mensagem,
                erro,
                origem,
                metadata,
                criado_em
            FROM timeline_eventos_inna
            WHERE trace_id = :trace_id
            ORDER BY ordem, criado_em;
        """)

        with engine.connect() as connection:
            df = pd.read_sql(
                query,
                connection,
                params={
                    "trace_id": trace_id,
                },
            )

        engine.dispose()

        return {
            "ok": True,
            "message": "Timeline carregada.",
            "trace_id": trace_id,
            "df": df,
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (
                "Erro ao carregar Timeline: "
                f"{exc}"
            ),
            "trace_id": trace_id,
            "df": None,
        }


def carregar_traces_recentes(
    limite: int = 50,
) -> dict[str, Any]:
    """
    Retorna um resumo das execuções recentes.
    """
    try:
        import pandas as pd
        from sqlalchemy import create_engine, text

        limite_seguro = max(
            1,
            min(int(limite), 1000),
        )

        engine = create_engine(
            _carregar_database_url(),
            pool_pre_ping=True,
        )

        query = text("""
            SELECT
                trace_id,
                MAX(usuario_id) AS usuario_id,
                MAX(pergunta) AS pergunta,
                MIN(criado_em) AS inicio_trace,
                MAX(criado_em) AS fim_trace,
                COUNT(*) AS total_etapas,
                COUNT(*) FILTER (
                    WHERE status = 'falha'
                ) AS total_falhas,
                SUM(
                    COALESCE(duracao_ms, 0)
                ) AS duracao_total_ms,
                MAX(origem) AS origem
            FROM timeline_eventos_inna
            GROUP BY trace_id
            ORDER BY MAX(criado_em) DESC
            LIMIT :limite;
        """)

        with engine.connect() as connection:
            df = pd.read_sql(
                query,
                connection,
                params={
                    "limite": limite_seguro,
                },
            )

        engine.dispose()

        return {
            "ok": True,
            "message": "Traces recentes carregados.",
            "df": df,
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (
                "Erro ao carregar traces: "
                f"{exc}"
            ),
            "df": None,
        }


__all__ = [
    "ETAPAS_TIMELINE",
    "LABELS_ETAPAS",
    "gerar_trace_id",
    "preparar_tabela_timeline",
    "registrar_evento_timeline",
    "executar_etapa_timeline",
    "carregar_timeline_trace",
    "carregar_traces_recentes",
]
