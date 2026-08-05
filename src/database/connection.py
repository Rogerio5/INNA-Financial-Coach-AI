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

import math
import os
import socket
import time
from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Any, Generator, Optional


class DatabaseConfigurationError(RuntimeError):
    """Erro de configuração da conexão com o banco."""


class DatabaseConnectionError(RuntimeError):
    """Erro ao abrir ou utilizar uma conexão com o banco."""


DEFAULT_DB_CONNECT_TIMEOUT_SECONDS = 8
DEFAULT_DB_DNS_CACHE_TTL_SECONDS = 60

SUPPORTED_DB_NETWORK_FAMILIES = frozenset(
    {
        "ipv4",
        "system",
    }
)


_ipv4_dns_cache: dict[
    tuple[str, int],
    tuple[float, tuple[str, ...]],
] = {}

_ipv4_dns_cache_lock = Lock()


def _positive_integer_environment(
    name: str,
    default: int,
    *,
    minimum: int = 1,
    maximum: int = 300,
) -> int:
    raw_value = str(os.getenv(name, "")).strip()

    if not raw_value:
        return default

    try:
        parsed = int(raw_value)
    except (TypeError, ValueError):
        return default

    if parsed < minimum:
        return default

    return min(
        parsed,
        maximum,
    )


def _obter_familia_rede_postgres() -> str:
    family = (
        str(
            os.getenv(
                "INNA_POSTGRES_NETWORK_FAMILY",
                "ipv4",
            )
        )
        .strip()
        .lower()
    )

    if family not in (SUPPORTED_DB_NETWORK_FAMILIES):
        raise DatabaseConfigurationError(
            "INNA_POSTGRES_NETWORK_FAMILY deve ser 'ipv4' ou 'system'."
        )

    return family


def _extrair_host_porta_database_url(
    psycopg2_module,
    database_url: str,
) -> tuple[str, int]:
    try:
        parameters = psycopg2_module.extensions.parse_dsn(database_url)
    except Exception:
        raise DatabaseConfigurationError(
            "DATABASE_URL possui formato inválido."
        ) from None

    raw_host = str(parameters.get("host") or "").strip()

    # A INNA utiliza uma única origem PostgreSQL.
    # Em uma URL multi-host, somente o primeiro host
    # é tratado por esta camada.
    host = raw_host.split(",")[0].strip()

    if not host:
        raise DatabaseConfigurationError(
            "Hostname PostgreSQL não encontrado na DATABASE_URL."
        )

    raw_port = str(parameters.get("port") or "5432").split(",")[0].strip()

    try:
        port = int(raw_port)
    except (TypeError, ValueError):
        raise DatabaseConfigurationError("Porta PostgreSQL inválida.") from None

    if not 1 <= port <= 65535:
        raise DatabaseConfigurationError("Porta PostgreSQL fora da faixa válida.")

    return (
        host,
        port,
    )


def _invalidar_cache_ipv4(
    host: str,
    port: int,
) -> None:
    with _ipv4_dns_cache_lock:
        _ipv4_dns_cache.pop(
            (
                host,
                port,
            ),
            None,
        )


def _limpar_cache_ipv4() -> None:
    """
    Utilizada por testes e operações controladas.
    """
    with _ipv4_dns_cache_lock:
        _ipv4_dns_cache.clear()


def _resolver_enderecos_ipv4(
    host: str,
    port: int,
    *,
    cache_ttl_seconds: int | None = None,
) -> tuple[str, ...]:
    ttl = (
        cache_ttl_seconds
        if cache_ttl_seconds is not None
        else _positive_integer_environment(
            ("INNA_POSTGRES_DNS_CACHE_TTL_SECONDS"),
            DEFAULT_DB_DNS_CACHE_TTL_SECONDS,
            minimum=1,
            maximum=3600,
        )
    )

    cache_key = (
        host,
        port,
    )

    now = time.monotonic()

    with _ipv4_dns_cache_lock:
        cached = _ipv4_dns_cache.get(cache_key)

        if cached is not None:
            expires_at, addresses = cached

            if expires_at > now:
                return addresses

            _ipv4_dns_cache.pop(
                cache_key,
                None,
            )

    try:
        address_infos = socket.getaddrinfo(
            host,
            port,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )
    except Exception as exc:
        raise DatabaseConnectionError(
            "Não foi possível resolver um "
            "endereço IPv4 do PostgreSQL: "
            f"{type(exc).__name__}"
        ) from None

    addresses = []

    for info in address_infos:
        address = str(info[4][0]).strip()

        if address and address not in addresses:
            addresses.append(address)

    if not addresses:
        raise DatabaseConnectionError(
            "Nenhum endereço IPv4 foi encontrado para o PostgreSQL."
        )

    result = tuple(addresses)

    with _ipv4_dns_cache_lock:
        _ipv4_dns_cache[cache_key] = (
            now + ttl,
            result,
        )

    return result


def _conectar_postgres_ipv4(
    psycopg2_module,
    *,
    database_url: str,
    connect_timeout: int,
):
    host, port = _extrair_host_porta_database_url(
        psycopg2_module,
        database_url,
    )

    addresses = _resolver_enderecos_ipv4(
        host,
        port,
    )

    deadline = time.monotonic() + connect_timeout

    last_error_type = "ConnectionError"

    for address in addresses:
        remaining_seconds = deadline - time.monotonic()

        if remaining_seconds <= 0:
            break

        # Um endereço individual não pode consumir
        # todo o orçamento de conexão.
        attempt_timeout = max(
            1,
            min(
                3,
                math.ceil(remaining_seconds),
            ),
        )

        try:
            return psycopg2_module.connect(
                database_url,
                host=host,
                hostaddr=address,
                port=port,
                connect_timeout=(attempt_timeout),
                application_name=("inna-financial-coach-ai"),
            )

        except Exception as exc:
            last_error_type = type(exc).__name__

    _invalidar_cache_ipv4(
        host,
        port,
    )

    raise DatabaseConnectionError(
        "Não foi possível conectar ao PostgreSQL "
        "pelos endereços IPv4 disponíveis: "
        f"{last_error_type}"
    )


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
    connect_timeout: int | None = None,
):
    """
    Cria uma conexão segura com PostgreSQL.

    Por padrão, resolve somente endereços IPv4 e usa
    hostaddr, preservando o hostname original para SSL.

    A senha e a URL nunca são exibidas em mensagens
    de erro.
    """
    try:
        import psycopg2
    except ImportError as exc:
        raise DatabaseConfigurationError("Dependência psycopg2 não instalada.") from exc

    database_url = obter_database_url(obrigatoria=True)

    effective_timeout = (
        int(connect_timeout)
        if connect_timeout is not None
        else _positive_integer_environment(
            ("INNA_POSTGRES_CONNECT_TIMEOUT_SECONDS"),
            DEFAULT_DB_CONNECT_TIMEOUT_SECONDS,
            minimum=1,
            maximum=60,
        )
    )

    if effective_timeout < 1:
        raise ValueError("connect_timeout deve ser positivo.")

    network_family = _obter_familia_rede_postgres()

    try:
        if network_family == "system":
            connection = psycopg2.connect(
                database_url,
                connect_timeout=(effective_timeout),
                application_name=("inna-financial-coach-ai"),
            )
        else:
            connection = _conectar_postgres_ipv4(
                psycopg2,
                database_url=database_url,
                connect_timeout=(effective_timeout),
            )

        connection.autocommit = autocommit

        return connection

    except (
        DatabaseConfigurationError,
        DatabaseConnectionError,
    ):
        raise

    except Exception as exc:
        raise DatabaseConnectionError(
            f"Não foi possível conectar ao PostgreSQL: {type(exc).__name__}"
        ) from None


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

    with conexao_postgres(commit_automatico=commit_automatico) as conexao:
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
            "server_time": (str(registro.get("horario_banco")) if registro else None),
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
        raise ValueError(f"buscar deve ser uma destas opções: {opcoes_validas}")

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
