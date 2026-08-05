"""
Repositório de documentos da base RAG da INNA.

Responsabilidades:
- preparar a tabela de documentos;
- registrar metadados de uploads;
- listar documentos;
- buscar documentos por ID;
- ativar e desativar documentos;
- atualizar dados após reprocessamento;
- registrar histórico de alterações.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


TABELA_DOCUMENTOS = "documentos_upload_rag"
TABELA_HISTORICO = "documentos_upload_rag_historico"


def _carregar_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        try:
            from dotenv import load_dotenv

            load_dotenv(
                dotenv_path=Path(".env"),
                override=False,
            )

            database_url = os.getenv("DATABASE_URL")
        except ImportError:
            database_url = None

    if not database_url:
        raise RuntimeError("DATABASE_URL não encontrada.")

    return database_url


def _conectar_postgres():
    try:
        import psycopg2
    except ImportError as exc:
        raise RuntimeError("Pacote psycopg2 não instalado.") from exc

    return psycopg2.connect(_carregar_database_url())


def _criar_engine_sqlalchemy():
    """
    Cria engine SQLAlchemy para consultas com pandas.
    """
    try:
        from sqlalchemy import create_engine
    except ImportError as exc:
        raise RuntimeError("Pacote SQLAlchemy não instalado.") from exc

    return create_engine(
        _carregar_database_url(),
        pool_pre_ping=True,
    )


def preparar_tabelas_documentos(
    conn=None,
) -> dict:
    """
    Cria e atualiza as tabelas de documentos e histórico.
    """
    conexao_propria = conn is None

    try:
        if conexao_propria:
            conn = _conectar_postgres()

        cur = conn.cursor()

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABELA_DOCUMENTOS} (
                id SERIAL PRIMARY KEY,
                nome_original TEXT,
                nome_salvo TEXT NOT NULL,
                caminho_upload TEXT,
                caminho_chunks TEXT,
                caminho_embedding_ready TEXT,
                extensao TEXT,
                tamanho_bytes INTEGER,
                total_chunks INTEGER DEFAULT 0,
                status TEXT DEFAULT 'processado',
                origem TEXT DEFAULT 'dashboard_upload',
                ativo BOOLEAN DEFAULT TRUE,
                criado_em TIMESTAMP DEFAULT NOW(),
                atualizado_em TIMESTAMP DEFAULT NOW()
            );
        """)

        colunas = [
            (
                "ativo",
                "BOOLEAN DEFAULT TRUE",
            ),
            (
                "atualizado_em",
                "TIMESTAMP DEFAULT NOW()",
            ),
            (
                "nome_logico",
                "TEXT",
            ),
            (
                "content_hash",
                "VARCHAR(64)",
            ),
            (
                "versao",
                "INTEGER DEFAULT 1",
            ),
            (
                "documento_raiz_id",
                "INTEGER",
            ),
            (
                "documento_anterior_id",
                "INTEGER",
            ),
        ]

        for nome_coluna, tipo_coluna in colunas:
            cur.execute(f"""
                ALTER TABLE {TABELA_DOCUMENTOS}
                ADD COLUMN IF NOT EXISTS
                    {nome_coluna} {tipo_coluna};
            """)

        cur.execute(f"""
            UPDATE {TABELA_DOCUMENTOS}
            SET ativo = TRUE
            WHERE ativo IS NULL;
        """)

        cur.execute(f"""
            UPDATE {TABELA_DOCUMENTOS}
            SET versao = 1
            WHERE versao IS NULL
               OR versao < 1;
        """)

        cur.execute(f"""
            CREATE INDEX IF NOT EXISTS
                idx_documentos_upload_rag_nome_logico
            ON {TABELA_DOCUMENTOS} (
                nome_logico
            );
        """)

        cur.execute(f"""
            CREATE INDEX IF NOT EXISTS
                idx_documentos_upload_rag_raiz
            ON {TABELA_DOCUMENTOS} (
                documento_raiz_id
            );
        """)

        cur.execute(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS
                uq_documentos_upload_rag_hash
            ON {TABELA_DOCUMENTOS} (
                content_hash
            )
            WHERE content_hash IS NOT NULL;
        """)

        cur.execute(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS
                uq_documentos_upload_rag_nome_versao
            ON {TABELA_DOCUMENTOS} (
                nome_logico,
                versao
            )
            WHERE nome_logico IS NOT NULL;
        """)

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABELA_HISTORICO} (
                id SERIAL PRIMARY KEY,
                documento_id INTEGER
                    REFERENCES {TABELA_DOCUMENTOS}(id)
                    ON DELETE CASCADE,
                tipo_evento TEXT NOT NULL,
                status_anterior TEXT,
                status_novo TEXT,
                ativo_anterior BOOLEAN,
                ativo_novo BOOLEAN,
                detalhes JSONB,
                origem TEXT DEFAULT 'document_repository',
                criado_em TIMESTAMP DEFAULT NOW()
            );
        """)

        conn.commit()
        cur.close()

        if conexao_propria:
            conn.close()

        return {
            "ok": True,
            "message": ("Tabelas de documentos criadas/validadas."),
        }

    except Exception as exc:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

        if conexao_propria and conn:
            try:
                conn.close()
            except Exception:
                pass

        return {
            "ok": False,
            "message": (f"Erro ao preparar tabelas de documentos: {exc}"),
        }


def registrar_historico_documento(
    documento_id: int,
    tipo_evento: str,
    *,
    status_anterior: str | None = None,
    status_novo: str | None = None,
    ativo_anterior: bool | None = None,
    ativo_novo: bool | None = None,
    detalhes: dict | None = None,
    origem: str = "document_repository",
    conn=None,
) -> dict:
    """
    Registra uma alteração feita no documento.
    """
    import json

    conexao_propria = conn is None

    try:
        if conexao_propria:
            conn = _conectar_postgres()

            preparacao = preparar_tabelas_documentos(conn)

            if not preparacao.get("ok"):
                conn.close()
                return preparacao

        cur = conn.cursor()

        cur.execute(
            f"""
            INSERT INTO {TABELA_HISTORICO} (
                documento_id,
                tipo_evento,
                status_anterior,
                status_novo,
                ativo_anterior,
                ativo_novo,
                detalhes,
                origem
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s::jsonb,
                %s
            )
            RETURNING id;
            """,
            (
                int(documento_id),
                str(tipo_evento),
                status_anterior,
                status_novo,
                ativo_anterior,
                ativo_novo,
                json.dumps(
                    detalhes or {},
                    ensure_ascii=False,
                ),
                origem,
            ),
        )

        historico_id = int(cur.fetchone()[0])

        if conexao_propria:
            conn.commit()

        cur.close()

        if conexao_propria:
            conn.close()

        return {
            "ok": True,
            "id": historico_id,
            "message": ("Histórico do documento registrado."),
        }

    except Exception as exc:
        if conexao_propria and conn:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass

        return {
            "ok": False,
            "message": (f"Erro ao registrar histórico: {exc}"),
        }


def registrar_documento(
    *,
    nome_original: str,
    nome_salvo: str,
    caminho_upload: str,
    caminho_chunks: str,
    caminho_embedding_ready: str,
    extensao: str,
    tamanho_bytes: int,
    total_chunks: int,
    nome_logico: str | None = None,
    content_hash: str | None = None,
    versao: int = 1,
    documento_raiz_id: int | None = None,
    documento_anterior_id: int | None = None,
    status: str = "processado",
    origem: str = "dashboard_upload",
) -> dict:
    """
    Salva os metadados de um novo documento.
    """
    conn = None

    try:
        conn = _conectar_postgres()

        preparacao = preparar_tabelas_documentos(conn)

        if not preparacao.get("ok"):
            conn.close()
            return preparacao

        cur = conn.cursor()

        cur.execute(
            f"""
            INSERT INTO {TABELA_DOCUMENTOS} (
                nome_original,
                nome_salvo,
                caminho_upload,
                caminho_chunks,
                caminho_embedding_ready,
                extensao,
                tamanho_bytes,
                total_chunks,
                nome_logico,
                content_hash,
                versao,
                documento_raiz_id,
                documento_anterior_id,
                status,
                origem,
                ativo,
                atualizado_em
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
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                TRUE,
                NOW()
            )
            RETURNING id;
            """,
            (
                nome_original,
                nome_salvo,
                caminho_upload,
                caminho_chunks,
                caminho_embedding_ready,
                extensao,
                int(tamanho_bytes),
                int(total_chunks),
                nome_logico,
                content_hash,
                int(versao),
                (int(documento_raiz_id) if documento_raiz_id is not None else None),
                (
                    int(documento_anterior_id)
                    if documento_anterior_id is not None
                    else None
                ),
                status,
                origem,
            ),
        )

        documento_id = int(cur.fetchone()[0])

        registrar_historico_documento(
            documento_id=documento_id,
            tipo_evento="documento_registrado",
            status_novo=status,
            ativo_novo=True,
            detalhes={
                "nome_original": nome_original,
                "nome_salvo": nome_salvo,
                "total_chunks": int(total_chunks),
                "tamanho_bytes": int(tamanho_bytes),
                "nome_logico": nome_logico,
                "content_hash": content_hash,
                "versao": int(versao),
                "documento_raiz_id": documento_raiz_id,
                "documento_anterior_id": (documento_anterior_id),
            },
            origem=origem,
            conn=conn,
        )

        conn.commit()
        cur.close()
        conn.close()

        return {
            "ok": True,
            "id": documento_id,
            "documento_id": documento_id,
            "nome_logico": nome_logico,
            "content_hash": content_hash,
            "versao": int(versao),
            "documento_raiz_id": (
                documento_raiz_id if documento_raiz_id is not None else documento_id
            ),
            "documento_anterior_id": (documento_anterior_id),
            "message": (f"Metadata salva no Neon/PostgreSQL com id {documento_id}."),
        }

    except Exception as exc:
        if conn:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass

        return {
            "ok": False,
            "message": (f"Erro ao salvar metadata no Neon/PostgreSQL: {exc}"),
        }


def buscar_contexto_versionamento_documento(
    nome_logico: str,
) -> dict:
    """
    Busca as versões já registradas de um documento lógico.

    Retorna:
    - versão atual;
    - documento raiz;
    - documento anterior;
    - hashes existentes;
    - quantidade de versões.
    """
    nome_logico_normalizado = str(nome_logico or "").strip()

    if not nome_logico_normalizado:
        return {
            "ok": False,
            "message": ("O nome lógico do documento não foi informado."),
            "contexto": None,
        }

    conn = None

    try:
        conn = _conectar_postgres()

        preparacao = preparar_tabelas_documentos(conn)

        if not preparacao.get("ok"):
            conn.close()
            return {
                "ok": False,
                "message": preparacao.get("message"),
                "contexto": None,
            }

        cur = conn.cursor()

        cur.execute(
            f"""
            SELECT
                id,
                COALESCE(versao, 1),
                documento_raiz_id,
                content_hash
            FROM {TABELA_DOCUMENTOS}
            WHERE nome_logico = %s
            ORDER BY
                COALESCE(versao, 1) DESC,
                id DESC;
            """,
            (nome_logico_normalizado,),
        )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        if not rows:
            return {
                "ok": True,
                "message": ("Nenhuma versão anterior encontrada."),
                "contexto": {
                    "nome_logico": (nome_logico_normalizado),
                    "current_version": None,
                    "root_document_id": None,
                    "previous_document_id": None,
                    "existing_content_hashes": [],
                    "total_versions": 0,
                },
            }

        latest = rows[0]

        latest_document_id = int(latest[0])

        current_version = int(latest[1] or 1)

        root_document_id = (
            int(latest[2]) if latest[2] is not None else latest_document_id
        )

        existing_hashes = [str(row[3]).strip().lower() for row in rows if row[3]]

        return {
            "ok": True,
            "message": ("Contexto de versionamento carregado."),
            "contexto": {
                "nome_logico": (nome_logico_normalizado),
                "current_version": (current_version),
                "root_document_id": (root_document_id),
                "previous_document_id": (latest_document_id),
                "existing_content_hashes": (existing_hashes),
                "total_versions": len(rows),
            },
        }

    except Exception as exc:
        if conn:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass

        return {
            "ok": False,
            "message": (f"Erro ao buscar contexto de versionamento: {exc}"),
            "contexto": None,
        }


def listar_documentos(
    *,
    limite: int = 100,
):
    """
    Retorna DataFrame e mensagem de erro, mantendo
    compatibilidade com o dashboard atual.
    """
    import pandas as pd

    limite = max(
        1,
        min(int(limite), 1000),
    )

    try:
        conn = _conectar_postgres()

        preparacao = preparar_tabelas_documentos(conn)

        if not preparacao.get("ok"):
            conn.close()
            return (
                pd.DataFrame(),
                preparacao.get("message"),
            )

        conn.close()

        engine = _criar_engine_sqlalchemy()

        query = f"""
            SELECT
                id,
                nome_original,
                nome_salvo,
                extensao,
                tamanho_bytes,
                total_chunks,
                status,
                origem,
                COALESCE(ativo, TRUE) AS ativo,
                nome_logico,
                content_hash,
                COALESCE(versao, 1) AS versao,
                documento_raiz_id,
                documento_anterior_id,
                caminho_upload,
                caminho_chunks,
                caminho_embedding_ready,
                criado_em,
                atualizado_em
            FROM {TABELA_DOCUMENTOS}
            ORDER BY criado_em DESC
            LIMIT {limite};
        """

        with engine.connect() as connection:
            df = pd.read_sql(
                query,
                connection,
            )

        engine.dispose()

        return df, None

    except Exception as exc:
        return (
            pd.DataFrame(),
            str(exc),
        )


def buscar_documento_por_id(
    documento_id: int,
) -> dict:
    """
    Busca um documento específico.
    """
    try:
        conn = _conectar_postgres()
        cur = conn.cursor()

        cur.execute(
            f"""
            SELECT
                id,
                nome_original,
                nome_salvo,
                caminho_upload,
                caminho_chunks,
                caminho_embedding_ready,
                extensao,
                tamanho_bytes,
                total_chunks,
                status,
                origem,
                COALESCE(ativo, TRUE),
                nome_logico,
                content_hash,
                COALESCE(versao, 1),
                documento_raiz_id,
                documento_anterior_id,
                criado_em,
                atualizado_em
            FROM {TABELA_DOCUMENTOS}
            WHERE id = %s;
            """,
            (int(documento_id),),
        )

        row = cur.fetchone()

        cur.close()
        conn.close()

        if not row:
            return {
                "ok": False,
                "message": "Documento não encontrado.",
                "documento": None,
            }

        colunas = [
            "id",
            "nome_original",
            "nome_salvo",
            "caminho_upload",
            "caminho_chunks",
            "caminho_embedding_ready",
            "extensao",
            "tamanho_bytes",
            "total_chunks",
            "status",
            "origem",
            "ativo",
            "nome_logico",
            "content_hash",
            "versao",
            "documento_raiz_id",
            "documento_anterior_id",
            "criado_em",
            "atualizado_em",
        ]

        documento = dict(zip(colunas, row))

        return {
            "ok": True,
            "message": "Documento encontrado.",
            "documento": documento,
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (f"Erro ao buscar documento: {exc}"),
            "documento": None,
        }


def atualizar_processamento_documento(
    documento_id: int,
    *,
    caminho_chunks: str,
    caminho_embedding_ready: str,
    total_chunks: int,
) -> dict:
    """
    Atualiza os caminhos após reprocessamento.
    """
    conn = None

    try:
        conn = _conectar_postgres()
        cur = conn.cursor()

        cur.execute(
            f"""
            SELECT
                status,
                caminho_chunks,
                caminho_embedding_ready,
                total_chunks
            FROM {TABELA_DOCUMENTOS}
            WHERE id = %s;
            """,
            (int(documento_id),),
        )

        anterior = cur.fetchone()

        if not anterior:
            cur.close()
            conn.close()

            return {
                "ok": False,
                "message": "Documento não encontrado.",
            }

        status_anterior = anterior[0]

        cur.execute(
            f"""
            UPDATE {TABELA_DOCUMENTOS}
            SET
                caminho_chunks = %s,
                caminho_embedding_ready = %s,
                total_chunks = %s,
                status = 'processado',
                atualizado_em = NOW()
            WHERE id = %s;
            """,
            (
                caminho_chunks,
                caminho_embedding_ready,
                int(total_chunks),
                int(documento_id),
            ),
        )

        registrar_historico_documento(
            documento_id=int(documento_id),
            tipo_evento="documento_reprocessado",
            status_anterior=status_anterior,
            status_novo="processado",
            detalhes={
                "caminho_chunks_anterior": anterior[1],
                "caminho_embedding_anterior": anterior[2],
                "total_chunks_anterior": anterior[3],
                "caminho_chunks_novo": caminho_chunks,
                "caminho_embedding_novo": (caminho_embedding_ready),
                "total_chunks_novo": int(total_chunks),
            },
            origem="dashboard_reprocessamento",
            conn=conn,
        )

        conn.commit()
        cur.close()
        conn.close()

        return {
            "ok": True,
            "message": ("Metadata do documento atualizada após reprocessamento."),
        }

    except Exception as exc:
        if conn:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass

        return {
            "ok": False,
            "message": (f"Erro ao atualizar metadata do documento: {exc}"),
        }


def atualizar_status_documento(
    documento_id: int,
    ativo: bool,
) -> dict:
    """
    Ativa ou desativa um documento na busca RAG.
    """
    conn = None

    try:
        conn = _conectar_postgres()

        preparacao = preparar_tabelas_documentos(conn)

        if not preparacao.get("ok"):
            conn.close()
            return preparacao

        cur = conn.cursor()

        cur.execute(
            f"""
            SELECT COALESCE(ativo, TRUE)
            FROM {TABELA_DOCUMENTOS}
            WHERE id = %s;
            """,
            (int(documento_id),),
        )

        row = cur.fetchone()

        if not row:
            cur.close()
            conn.close()

            return {
                "ok": False,
                "message": "Documento não encontrado.",
            }

        ativo_anterior = bool(row[0])
        ativo_novo = bool(ativo)

        cur.execute(
            f"""
            UPDATE {TABELA_DOCUMENTOS}
            SET
                ativo = %s,
                atualizado_em = NOW()
            WHERE id = %s;
            """,
            (
                ativo_novo,
                int(documento_id),
            ),
        )

        registrar_historico_documento(
            documento_id=int(documento_id),
            tipo_evento=("documento_ativado" if ativo_novo else "documento_desativado"),
            ativo_anterior=ativo_anterior,
            ativo_novo=ativo_novo,
            origem="dashboard_status",
            conn=conn,
        )

        conn.commit()
        cur.close()
        conn.close()

        estado = "ativado" if ativo_novo else "desativado"

        return {
            "ok": True,
            "message": (f"Documento {estado} com sucesso."),
            "ativo": ativo_novo,
        }

    except Exception as exc:
        if conn:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass

        return {
            "ok": False,
            "message": (f"Erro ao atualizar status do documento: {exc}"),
        }


def garantir_coluna_ativo() -> dict:
    """
    Adaptador explícito para instalações antigas.
    """
    return preparar_tabelas_documentos()


def listar_historico_documento(
    documento_id: int,
    *,
    limite: int = 50,
):
    """
    Retorna o histórico do documento em um DataFrame.
    """
    import pandas as pd

    try:
        engine = _criar_engine_sqlalchemy()

        query = f"""
            SELECT
                id,
                documento_id,
                tipo_evento,
                status_anterior,
                status_novo,
                ativo_anterior,
                ativo_novo,
                detalhes,
                origem,
                criado_em
            FROM {TABELA_HISTORICO}
            WHERE documento_id = %s
            ORDER BY criado_em DESC
            LIMIT %s;
        """

        with engine.connect() as connection:
            df = pd.read_sql(
                query,
                connection,
                params=(
                    int(documento_id),
                    int(limite),
                ),
            )

        engine.dispose()

        return {
            "ok": True,
            "message": "Histórico carregado.",
            "df": df,
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": (f"Erro ao carregar histórico: {exc}"),
            "df": pd.DataFrame(),
        }


__all__ = [
    "TABELA_DOCUMENTOS",
    "TABELA_HISTORICO",
    "preparar_tabelas_documentos",
    "registrar_historico_documento",
    "registrar_documento",
    "buscar_contexto_versionamento_documento",
    "listar_documentos",
    "buscar_documento_por_id",
    "atualizar_processamento_documento",
    "atualizar_status_documento",
    "garantir_coluna_ativo",
    "listar_historico_documento",
]
