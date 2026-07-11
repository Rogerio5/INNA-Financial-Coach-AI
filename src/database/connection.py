"""
Conexão centralizada com Neon/PostgreSQL.

Este módulo é responsável por:

- carregar a DATABASE_URL;
- criar conexões PostgreSQL;
- controlar commit e rollback;
- fechar conexões automaticamente;
- testar a disponibilidade do banco;
- evitar repetição de código nos serviços da INNA.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional


class DatabaseConfigurationError(RuntimeError):
    """Erro de configuração da conexão com o banco."""


class DatabaseConnectionError(RuntimeError):
    """Erro ao abrir ou utilizar uma conexão com o banco."""


def carregar_variaveis_ambiente() -> None:
    """
    Carrega o arquivo .env da raiz do projeto quando ele existir.

    Em produção, as variáveis podem ser fornecidas diretamente
    pelo ambiente do Render, Docker, AWS ou outro serviço.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    env_path = Path(".env")

    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)


def obter_database_url(obrigatoria: bool = True) -> Optional[str]:
    """
    Retorna a DATABASE_URL configurada.

    Args:
        obrigatoria:
            Quando True, lança erro se a variável não existir.

    Returns:
        URL de conexão ou None.
    """
    carregar_variaveis_ambiente()

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return database_url.strip()

    if obrigatoria:
        raise DatabaseConfigurationError(
            "DATABASE_URL não encontrada no ambiente nem no arquivo .env."
        )

    return None


def criar_conexao(
    *,
    autocommit: bool = False,
    connect_timeout: int = 15,
):
    """
    Cria uma conexão com PostgreSQL.

    A senha e a URL nunca são exibidas em mensagens de erro.
    """
    try:
        import psycopg2
    except ImportError as exc:
        raise DatabaseConfigurationError(
            "Dependência psycopg2 não instalada."
        ) from exc

    database_url = obter_database_url(obrigatoria=True)

    try:
        conexao = psycopg2.connect(
            database_url,
            connect_timeout=connect_timeout,
            application_name="inna-financial-coach-ai",
        )
        conexao.autocommit = autocommit
        return conexao

    except Exception as exc:
        raise DatabaseConnectionError(
            f"Não foi possível conectar ao PostgreSQL: {type(exc).__name__}"
        ) from exc


@contextmanager
def conexao_postgres(
    *,
    autocommit: bool = False,
    commit_automatico: bool = True,
) -> Generator[Any, None, None]:
    """
    Context manager para conexão PostgreSQL.

    Exemplo:

        with conexao_postgres() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")

    Se ocorrer erro:
    - executa rollback;
    - fecha a conexão;
    - propaga a exceção.

    Se não ocorrer erro:
    - executa commit quando configurado;
    - fecha a conexão.
    """
    conexao = criar_conexao(autocommit=autocommit)

    try:
        yield conexao

        if commit_automatico and not autocommit:
            conexao.commit()

    except Exception:
        if not autocommit:
            conexao.rollback()
        raise

    finally:
        conexao.close()


@contextmanager
def cursor_postgres(
    *,
    dict_cursor: bool = False,
    commit_automatico: bool = True,
):
    """
    Entrega um cursor pronto para uso e fecha tudo automaticamente.

    Args:
        dict_cursor:
            Quando True, retorna registros semelhantes a dicionários.

        commit_automatico:
            Controla o commit após execução bem-sucedida.
    """
    cursor_factory = None

    if dict_cursor:
        try:
            from psycopg2.extras import RealDictCursor
            cursor_factory = RealDictCursor
        except ImportError as exc:
            raise DatabaseConfigurationError(
                "psycopg2.extras não está disponível."
            ) from exc

    with conexao_postgres(
        commit_automatico=commit_automatico
    ) as conexao:
        cursor = conexao.cursor(cursor_factory=cursor_factory)

        try:
            yield cursor
        finally:
            cursor.close()


def testar_conexao_postgres() -> dict:
    """
    Executa um teste simples de conexão.

    Não retorna DATABASE_URL nem informações sensíveis.
    """
    try:
        with cursor_postgres(
            dict_cursor=True,
            commit_automatico=False,
        ) as cursor:
            cursor.execute("""
                SELECT
                    current_database() AS banco,
                    current_user AS usuario,
                    version() AS versao,
                    NOW() AS horario_banco;
            """)

            registro = cursor.fetchone()

        return {
            "ok": True,
            "message": "Conexão com PostgreSQL validada.",
            "database": registro.get("banco") if registro else None,
            "user": registro.get("usuario") if registro else None,
            "server_time": (
                str(registro.get("horario_banco"))
                if registro
                else None
            ),
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": str(exc),
            "database": None,
            "user": None,
            "server_time": None,
        }


def executar_sql(
    sql: str,
    parametros: Optional[tuple] = None,
    *,
    buscar: str = "nenhum",
    dict_cursor: bool = False,
):
    """
    Executa SQL parametrizado de forma reutilizável.

    buscar:
    - "nenhum": não retorna registros;
    - "um": retorna fetchone();
    - "todos": retorna fetchall().
    """
    opcoes_validas = {"nenhum", "um", "todos"}

    if buscar not in opcoes_validas:
        raise ValueError(
            f"buscar deve ser uma destas opções: {opcoes_validas}"
        )

    with cursor_postgres(
        dict_cursor=dict_cursor,
        commit_automatico=True,
    ) as cursor:
        cursor.execute(sql, parametros or ())

        if buscar == "um":
            return cursor.fetchone()

        if buscar == "todos":
            return cursor.fetchall()

        return None
