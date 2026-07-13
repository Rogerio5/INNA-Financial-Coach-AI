"""
Observabilidade das Tools financeiras da INNA.

Responsabilidades:
- criar a tabela de eventos;
- registrar execuções das Tools;
- preservar o fluxo principal quando o banco estiver indisponível;
- carregar histórico e indicadores operacionais.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


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


def preparar_tabela_eventos_tools(
    conn=None,
) -> dict:
    """
    Cria a tabela de observabilidade quando necessário.
    """
    conexao_propria = conn is None

    try:
        if conexao_propria:
            conn = _conectar_postgres()

        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS tools_eventos_inna (
                id BIGSERIAL PRIMARY KEY,
                usuario_id TEXT,
                pergunta TEXT,
                tool_nome TEXT,
                tool_label TEXT,
                intencao TEXT,
                confianca DOUBLE PRECISION,
                executada BOOLEAN DEFAULT FALSE,
                sucesso BOOLEAN DEFAULT FALSE,
                argumentos JSONB,
                resultado JSONB,
                dados_ausentes JSONB,
                mensagem TEXT,
                erro TEXT,
                duracao_ms DOUBLE PRECISION,
                origem TEXT DEFAULT 'dashboard',
                metadata JSONB,
                criado_em TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_tools_eventos_usuario
            ON tools_eventos_inna (
                usuario_id,
                criado_em DESC
            );
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_tools_eventos_tool
            ON tools_eventos_inna (
                tool_nome,
                criado_em DESC
            );
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_tools_eventos_sucesso
            ON tools_eventos_inna (
                sucesso,
                criado_em DESC
            );
        """)

        conn.commit()
        cur.close()

        if conexao_propria:
            conn.close()

        return {
            "ok": True,
            "message": (
                "Tabela de eventos das Tools preparada."
            ),
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
                "Erro ao preparar observabilidade: "
                f"{exc}"
            ),
        }


def registrar_evento_tool(
    *,
    usuario_id: str | None,
    pergunta: str,
    resultado_tools: dict[str, Any],
    duracao_ms: float | None = None,
    origem: str = "dashboard",
    metadata: dict[str, Any] | None = None,
) -> dict:
    """
    Registra uma execução sem interromper o fluxo principal.
    """
    conn = None

    try:
        conn = _conectar_postgres()

        preparacao = preparar_tabela_eventos_tools(
            conn
        )

        if not preparacao.get("ok"):
            conn.close()
            return preparacao

        cur = conn.cursor()

        tool_nome = resultado_tools.get(
            "tool_identificada"
        )

        execucao = (
            resultado_tools.get("router", {})
            .get("execucao")
            or {}
        )

        erro = None

        if (
            resultado_tools.get("executada")
            and not resultado_tools.get("ok")
        ):
            erro = resultado_tools.get(
                "message"
            )

        cur.execute("""
            INSERT INTO tools_eventos_inna (
                usuario_id,
                pergunta,
                tool_nome,
                tool_label,
                intencao,
                confianca,
                executada,
                sucesso,
                argumentos,
                resultado,
                dados_ausentes,
                mensagem,
                erro,
                duracao_ms,
                origem,
                metadata
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s::jsonb,
                %s::jsonb,
                %s::jsonb,
                %s,
                %s,
                %s,
                %s,
                %s::jsonb
            )
            RETURNING id;
        """, (
            usuario_id,
            pergunta,
            tool_nome,
            resultado_tools.get("tool_label"),
            resultado_tools.get("intencao"),
            resultado_tools.get("confianca"),
            bool(resultado_tools.get("executada")),
            bool(resultado_tools.get("ok")),
            json.dumps(
                resultado_tools.get(
                    "argumentos",
                    {},
                ),
                ensure_ascii=False,
                default=str,
            ),
            json.dumps(
                resultado_tools.get("resultado"),
                ensure_ascii=False,
                default=str,
            ),
            json.dumps(
                resultado_tools.get(
                    "dados_ausentes",
                    [],
                ),
                ensure_ascii=False,
                default=str,
            ),
            resultado_tools.get("message")
            or execucao.get("message"),
            erro,
            duracao_ms,
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
            "message": "Evento da Tool registrado.",
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
            "message": (
                "A resposta foi preservada, mas o evento "
                f"não pôde ser registrado: {exc}"
            ),
        }


def carregar_resumo_tools() -> dict:
    """
    Carrega indicadores agregados das Tools.
    """
    conn = None

    try:
        conn = _conectar_postgres()

        preparacao = preparar_tabela_eventos_tools(
            conn
        )

        if not preparacao.get("ok"):
            conn.close()
            return {
                **preparacao,
                "resumo": {},
            }

        cur = conn.cursor()

        cur.execute("""
            SELECT
                COUNT(*) AS total_eventos,
                COUNT(*) FILTER (
                    WHERE executada = TRUE
                ) AS total_executadas,
                COUNT(*) FILTER (
                    WHERE sucesso = TRUE
                ) AS total_sucesso,
                COUNT(*) FILTER (
                    WHERE sucesso = FALSE
                ) AS total_falhas,
                AVG(duracao_ms) FILTER (
                    WHERE duracao_ms IS NOT NULL
                ) AS duracao_media_ms,
                COUNT(DISTINCT tool_nome) FILTER (
                    WHERE tool_nome IS NOT NULL
                ) AS tools_distintas
            FROM tools_eventos_inna;
        """)

        row = cur.fetchone()

        resumo = {
            "total_eventos": int(row[0] or 0),
            "total_executadas": int(row[1] or 0),
            "total_sucesso": int(row[2] or 0),
            "total_falhas": int(row[3] or 0),
            "duracao_media_ms": (
                round(float(row[4]), 2)
                if row[4] is not None
                else 0.0
            ),
            "tools_distintas": int(row[5] or 0),
        }

        cur.close()
        conn.close()

        return {
            "ok": True,
            "message": "Resumo das Tools carregado.",
            "resumo": resumo,
        }

    except Exception as exc:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

        return {
            "ok": False,
            "message": (
                "Erro ao carregar resumo das Tools: "
                f"{exc}"
            ),
            "resumo": {},
        }


def carregar_eventos_tools(
    limite: int = 100,
) -> dict:
    """
    Retorna eventos recentes em DataFrame.
    """
    try:
        import pandas as pd
        from sqlalchemy import create_engine

        engine = create_engine(
            _carregar_database_url(),
            pool_pre_ping=True,
        )

        query = """
            SELECT
                id,
                criado_em,
                usuario_id,
                pergunta,
                tool_nome,
                tool_label,
                intencao,
                confianca,
                executada,
                sucesso,
                argumentos,
                resultado,
                dados_ausentes,
                duracao_ms,
                origem,
                mensagem,
                erro,
                metadata
            FROM tools_eventos_inna
            ORDER BY criado_em DESC
            LIMIT %(limite)s;
        """

        with engine.connect() as connection:
            df = pd.read_sql(
                query,
                connection,
                params={
                    "limite": max(
                        1,
                        min(int(limite), 1000),
                    ),
                },
            )

        engine.dispose()

        return {
            "ok": True,
            "message": "Eventos das Tools carregados.",
            "df": df,
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (
                "Erro ao carregar eventos: "
                f"{exc}"
            ),
            "df": None,
        }


def carregar_status_infraestrutura() -> dict:
    """
    Verifica componentes essenciais da infraestrutura.

    Nenhuma verificação deve interromper a aplicação.
    """
    status = {
        "postgresql": {
            "ok": False,
            "label": "PostgreSQL / Neon",
            "message": "Não verificado.",
        },
        "pgvector": {
            "ok": False,
            "label": "Extensão pgvector",
            "message": "Não verificado.",
        },
        "tools_table": {
            "ok": False,
            "label": "Tabela de eventos das Tools",
            "message": "Não verificado.",
        },
        "rag_table": {
            "ok": False,
            "label": "Base vetorial RAG",
            "message": "Não verificado.",
        },
        "memory_table": {
            "ok": False,
            "label": "Memória persistente",
            "message": "Não verificado.",
        },
        "gemini": {
            "ok": False,
            "label": "Configuração Gemini",
            "message": "Não verificado.",
        },
    }

    conn = None

    try:
        conn = _conectar_postgres()
        cur = conn.cursor()

        cur.execute("SELECT 1;")
        cur.fetchone()

        status["postgresql"] = {
            "ok": True,
            "label": "PostgreSQL / Neon",
            "message": "Conexão operacional.",
        }

        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM pg_extension
                WHERE extname = 'vector'
            );
        """)

        vector_ativo = bool(cur.fetchone()[0])

        status["pgvector"] = {
            "ok": vector_ativo,
            "label": "Extensão pgvector",
            "message": (
                "Extensão ativa."
                if vector_ativo
                else "Extensão não encontrada."
            ),
        }

        tabelas = {
            "tools_table": "tools_eventos_inna",
            "rag_table": "chunks_embeddings_rag",
            "memory_table": "memoria_usuarios_inna",
        }

        for chave, tabela in tabelas.items():
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name = %s
                );
            """, (tabela,))

            existe = bool(cur.fetchone()[0])

            status[chave]["ok"] = existe
            status[chave]["message"] = (
                f"Tabela {tabela} disponível."
                if existe
                else f"Tabela {tabela} não encontrada."
            )

        cur.close()
        conn.close()
        conn = None

    except Exception as exc:
        status["postgresql"]["message"] = (
            f"Falha na conexão: {exc}"
        )

    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not api_key:
        try:
            from dotenv import load_dotenv

            load_dotenv(
                dotenv_path=Path(".env")
            )

            api_key = (
                os.getenv("GEMINI_API_KEY")
                or os.getenv("GOOGLE_API_KEY")
            )
        except Exception:
            api_key = None

    status["gemini"] = {
        "ok": bool(api_key),
        "label": "Configuração Gemini",
        "message": (
            "Chave configurada."
            if api_key
            else "Chave não encontrada."
        ),
    }

    total_ok = sum(
        1
        for item in status.values()
        if item.get("ok")
    )

    return {
        "ok": True,
        "total_componentes": len(status),
        "total_operacionais": total_ok,
        "status": status,
    }




__all__ = [
    "preparar_tabela_eventos_tools",
    "registrar_evento_tool",
    "carregar_resumo_tools",
    "carregar_eventos_tools",
    "carregar_status_infraestrutura",
]
