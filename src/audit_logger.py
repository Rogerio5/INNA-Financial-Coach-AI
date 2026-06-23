
import os
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json


load_dotenv(".env")


def record_event(
    canal: str,
    usuario: str | None = None,
    idioma: str | None = None,
    moeda: str | None = None,
    status: str = "success",
    diagnostico_id: int | None = None,
    pergunta: str | None = None,
    resposta: str | None = None,
    metadata: dict[str, Any] | None = None,
    usuario_id: str | None = None,
    tempo_resposta_segundos: float = 0,
) -> None:
    """
    Registra qualquer evento da INNA no PostgreSQL Neon.

    Exemplos de canal:
    web-app, pdf-download, email, feedback, telegram, dashboard, gmail, instagram
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("[audit_logger] DATABASE_URL não encontrada.")
        return

    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO interacoes_inna (
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
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
                Json(metadata or {}),
            ),
        )

        conn.commit()
        cur.close()
        conn.close()

    except Exception as exc:
        print(f"[audit_logger] Erro ao registrar evento: {exc}")
