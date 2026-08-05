import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from psycopg2.extras import Json

load_dotenv()


def _get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        return None

    try:
        import psycopg2

        return psycopg2.connect(database_url)
    except Exception:
        return None


def ensure_interactions_table() -> None:
    conn = _get_connection()

    if conn is None:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS interacoes_inna (
                        id SERIAL PRIMARY KEY,
                        data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        canal VARCHAR(50) NOT NULL,
                        usuario_id VARCHAR(255),
                        usuario VARCHAR(255),
                        idioma VARCHAR(20),
                        moeda VARCHAR(20),
                        pergunta TEXT,
                        resposta TEXT,
                        status VARCHAR(50) DEFAULT 'success',
                        tempo_resposta_segundos NUMERIC(10, 3) DEFAULT 0,
                        diagnostico_id INTEGER,
                        metadata JSONB
                    );
                    """
                )
    finally:
        conn.close()


def record_interaction(
    canal: str,
    usuario_id: str | None = None,
    usuario: str | None = None,
    idioma: str | None = None,
    moeda: str | None = None,
    pergunta: str | None = None,
    resposta: str | None = None,
    status: str = "success",
    tempo_resposta_segundos: float = 0.0,
    diagnostico_id: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    conn = _get_connection()

    if conn is None:
        return

    try:
        ensure_interactions_table()

        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO interacoes_inna (
                        data_hora,
                        canal,
                        usuario_id,
                        usuario,
                        idioma,
                        moeda,
                        pergunta,
                        resposta,
                        status,
                        tempo_resposta_segundos,
                        diagnostico_id,
                        metadata
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                    """,
                    (
                        datetime.now(),
                        canal or "desconhecido",
                        usuario_id,
                        usuario,
                        idioma,
                        moeda,
                        pergunta,
                        resposta,
                        status,
                        round(float(tempo_resposta_segundos or 0), 3),
                        diagnostico_id,
                        Json(metadata) if metadata is not None else None,
                    ),
                )
    except Exception:
        return
    finally:
        conn.close()
