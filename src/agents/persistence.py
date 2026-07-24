"""
Persistência PostgreSQL do núcleo de agentes da INNA.

Usa um pool resiliente para evitar que conexões encerradas
pelo PostgreSQL/Neon interrompam checkpoints do LangGraph.
"""

from __future__ import annotations

import atexit
import os
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Iterator

from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


load_dotenv(
    dotenv_path=Path(".env"),
    override=False,
)


_pool: ConnectionPool | None = None
_pool_lock = Lock()


def obter_database_url() -> str:
    database_url = str(
        os.getenv("DATABASE_URL", "")
    ).strip()

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não configurada."
        )

    return database_url


def obter_pool_postgres() -> ConnectionPool:
    """
    Retorna um único pool reutilizável pela aplicação.

    O check valida a conexão antes de entregá-la.
    Conexões quebradas são descartadas pelo pool.
    """
    global _pool

    if _pool is not None and not _pool.closed:
        return _pool

    with _pool_lock:
        if _pool is not None and not _pool.closed:
            return _pool

        _pool = ConnectionPool(
            conninfo=obter_database_url(),
            min_size=1,
            max_size=5,
            timeout=30,
            max_lifetime=300,
            max_idle=60,
            reconnect_timeout=30,
            check=ConnectionPool.check_connection,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0,
                "row_factory": dict_row,
                "connect_timeout": 15,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 3,
            },
            open=True,
            name="inna-agent-checkpoints",
        )

        _pool.wait(timeout=30)

        return _pool


def fechar_pool_postgres() -> None:
    global _pool

    if _pool is not None and not _pool.closed:
        _pool.close(timeout=5)

    _pool = None


atexit.register(fechar_pool_postgres)


@contextmanager
def abrir_checkpointer_postgres() -> Iterator[PostgresSaver]:
    """
    Cria um PostgresSaver apoiado pelo pool compartilhado.

    O pool não é fechado depois de cada execução.
    """
    pool = obter_pool_postgres()
    yield PostgresSaver(pool)


def verificar_conexao_memoria() -> dict[str, object]:
    """
    Executa um teste simples antes de usar a memória.
    """
    try:
        pool = obter_pool_postgres()

        with pool.connection(timeout=15) as connection:
            resultado = connection.execute(
                "SELECT 1 AS ok"
            ).fetchone()

        return {
            "ok": bool(resultado and resultado["ok"] == 1),
            "message": "Conexão da memória operacional.",
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (
                "Falha na conexão da memória: "
                f"{type(exc).__name__}"
            ),
            "error_type": type(exc).__name__,
        }


def inicializar_memoria_agentes() -> dict[str, object]:
    """
    Cria ou atualiza as tabelas internas do LangGraph.
    """
    try:
        with abrir_checkpointer_postgres() as checkpointer:
            checkpointer.setup()

        return {
            "ok": True,
            "message": (
                "Memória persistente dos agentes "
                "inicializada no PostgreSQL."
            ),
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (
                "Erro ao inicializar a memória "
                f"dos agentes: {exc}"
            ),
            "error_type": type(exc).__name__,
        }


__all__ = [
    "obter_database_url",
    "obter_pool_postgres",
    "fechar_pool_postgres",
    "abrir_checkpointer_postgres",
    "verificar_conexao_memoria",
    "inicializar_memoria_agentes",
]
