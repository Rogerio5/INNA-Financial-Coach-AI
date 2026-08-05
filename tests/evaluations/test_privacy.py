from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import pytest
from pydantic import BaseModel

from src.evaluation.privacy import (
    DEFAULT_HASH_DIGEST_SIZE,
    MAX_DEPTH_REACHED,
    REDACTED_AUTH,
    REDACTED_BINARY,
    REDACTED_CARD,
    REDACTED_DATABASE_URL,
    REDACTED_DOCUMENT,
    REDACTED_EMAIL,
    REDACTED_FINANCIAL_DATA,
    REDACTED_IP,
    REDACTED_PERSONAL_DATA,
    REDACTED_PHONE,
    REDACTED_PIX,
    REDACTED_SECRET,
    TRUNCATED,
    assert_safe_for_external_export,
    contains_possible_personal_data,
    contains_possible_secret,
    content_hash,
    hash_identifier,
    normalize_key,
    prepare_external_payload,
    prepare_internal_payload,
    safe_artifact_name,
    safe_json_dumps,
    sanitize_exception,
    sanitize_headers,
    sanitize_mapping,
    sanitize_pix_key,
    sanitize_sequence,
    sanitize_text,
    sanitize_value,
    truncate_text,
)

# ============================================================
# OBJETOS AUXILIARES
# ============================================================


@dataclass
class ExampleDataclassPayload:
    email: str
    income: int
    token: str
    message: str


class ExamplePydanticPayload(BaseModel):
    email: str
    monthly_income: int
    api_key: str
    description: str


class ExampleStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"


class UnknownObject:
    def __repr__(self) -> str:
        return "UnknownObject(email=usuario@exemplo.com, token=segredo123)"


# ============================================================
# NORMALIZAÇÃO DE CHAVES
# ============================================================


@pytest.mark.parametrize(
    ("original", "expected"),
    (
        ("API Key", "api_key"),
        ("api-key", "api_key"),
        ("API_KEY", "api_key"),
        ("  Database URL  ", "database_url"),
        ("Nome Completo", "nome_completo"),
        ("X-INNA-Signature", "x_inna_signature"),
        ("financial.data", "financial_data"),
        ("", ""),
    ),
)
def test_normalize_key(
    original: str,
    expected: str,
) -> None:
    assert normalize_key(original) == expected


def test_normalize_key_accepts_non_string() -> None:
    assert normalize_key(123) == "123"


# ============================================================
# TRUNCAMENTO
# ============================================================


def test_truncate_text_preserves_short_text() -> None:
    value = "texto curto"

    assert (
        truncate_text(
            value,
            max_length=100,
        )
        == value
    )


def test_truncate_text_limits_long_text() -> None:
    value = "abcdefghij"

    truncated = truncate_text(
        value,
        max_length=5,
    )

    assert truncated.startswith("abcde")
    assert TRUNCATED in truncated
    assert ":5" in truncated


@pytest.mark.parametrize(
    "invalid_limit",
    (
        0,
        -1,
        -100,
    ),
)
def test_truncate_text_rejects_invalid_limit(
    invalid_limit: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="max_length",
    ):
        truncate_text(
            "texto",
            max_length=invalid_limit,
        )


# ============================================================
# SANITIZAÇÃO DE TEXTO
# ============================================================


def test_sanitize_text_redacts_email() -> None:
    sanitized = sanitize_text("Entre em contato com usuario@exemplo.com.")

    assert "usuario@exemplo.com" not in sanitized
    assert REDACTED_EMAIL in sanitized


def test_sanitize_text_redacts_phone() -> None:
    sanitized = sanitize_text("Meu telefone é (14) 99999-9999.")

    assert "99999-9999" not in sanitized
    assert REDACTED_PHONE in sanitized


@pytest.mark.parametrize(
    "document",
    (
        "123.456.789-09",
        "12345678909",
        "12.345.678/0001-90",
        "12345678000190",
    ),
)
def test_sanitize_text_redacts_documents(
    document: str,
) -> None:
    sanitized = sanitize_text(f"Documento: {document}")

    assert document not in sanitized
    assert REDACTED_DOCUMENT in sanitized


def test_sanitize_text_redacts_database_url() -> None:
    value = "Falha de conexão em postgresql://user:password@host:5432/database"

    sanitized = sanitize_text(value)

    assert "postgresql://" not in sanitized
    assert "password" not in sanitized
    assert REDACTED_DATABASE_URL in sanitized


@pytest.mark.parametrize(
    "database_url",
    (
        "postgresql://user:pass@host/db",
        "postgres://user:pass@host/db",
        "mysql://user:pass@host/db",
        "mariadb://user:pass@host/db",
        "mongodb://user:pass@host/db",
        "mongodb+srv://user:pass@host/db",
        "redis://user:pass@host:6379",
        "amqp://user:pass@host/vhost",
    ),
)
def test_sanitize_text_redacts_supported_database_urls(
    database_url: str,
) -> None:
    sanitized = sanitize_text(f"Conexão: {database_url}")

    assert database_url not in sanitized
    assert REDACTED_DATABASE_URL in sanitized


def test_sanitize_text_redacts_bearer_token() -> None:
    sanitized = sanitize_text("Authorization: Bearer token-secreto-123")

    assert "token-secreto-123" not in sanitized
    assert REDACTED_AUTH in sanitized


def test_sanitize_text_redacts_basic_auth() -> None:
    sanitized = sanitize_text("Authorization: Basic dXNlcjpwYXNzd29yZA==")

    assert "dXNlcjpwYXNzd29yZA==" not in sanitized
    assert REDACTED_AUTH in sanitized


def test_sanitize_text_redacts_jwt() -> None:
    token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature123"

    sanitized = sanitize_text(f"JWT: {token}")

    assert token not in sanitized
    assert REDACTED_AUTH in sanitized


@pytest.mark.parametrize(
    "assignment",
    (
        "api_key=super-secret",
        "API-KEY: super-secret",
        "password=minha-senha",
        "senha: minha-senha",
        "secret=abc123",
        "access_token=token123",
        "private_key=valor-secreto",
        "database_url=postgresql://user:pass@host/db",
        "connection_string=mysql://user:pass@host/db",
    ),
)
def test_sanitize_text_redacts_secret_assignments(
    assignment: str,
) -> None:
    sanitized = sanitize_text(assignment)

    assert "super-secret" not in sanitized
    assert "minha-senha" not in sanitized
    assert "abc123" not in sanitized
    assert "token123" not in sanitized
    assert "valor-secreto" not in sanitized
    assert "postgresql://" not in sanitized
    assert "mysql://" not in sanitized


def test_sanitize_text_redacts_private_key() -> None:
    private_key = """
-----BEGIN PRIVATE KEY-----
abcdefghijklmnopqrstuvwxyz
-----END PRIVATE KEY-----
"""

    sanitized = sanitize_text(private_key)

    assert "abcdefghijklmnopqrstuvwxyz" not in sanitized
    assert REDACTED_SECRET in sanitized


def test_sanitize_text_removes_http_url_credentials() -> None:
    value = "Acesse https://usuario:senha@servidor.exemplo.com/recurso"

    sanitized = sanitize_text(value)

    assert "usuario:senha@" not in sanitized
    assert "https://servidor.exemplo.com/recurso" in sanitized


def test_sanitize_text_preserves_safe_http_url() -> None:
    value = "Documentação em https://exemplo.com/docs"

    sanitized = sanitize_text(value)

    assert sanitized == value


def test_sanitize_text_redacts_valid_credit_card() -> None:
    sanitized = sanitize_text("Cartão de teste: 4111 1111 1111 1111")

    assert "4111" not in sanitized
    assert REDACTED_CARD in sanitized


def test_sanitize_text_preserves_non_card_number() -> None:
    number = "1234 5678 9012 3456"

    sanitized = sanitize_text(f"Sequência de teste: {number}")

    assert number in sanitized


def test_sanitize_text_redacts_valid_ipv4() -> None:
    sanitized = sanitize_text("Servidor interno: 192.168.0.10")

    assert "192.168.0.10" not in sanitized
    assert REDACTED_IP in sanitized


def test_sanitize_text_preserves_invalid_ipv4() -> None:
    invalid_ip = "999.999.999.999"

    sanitized = sanitize_text(f"Valor inválido: {invalid_ip}")

    assert invalid_ip in sanitized


def test_sanitize_text_redacts_uuid_when_enabled() -> None:
    uuid_value = "550e8400-e29b-41d4-a716-446655440000"

    sanitized = sanitize_text(
        uuid_value,
        redact_uuid=True,
    )

    assert uuid_value not in sanitized
    assert REDACTED_PERSONAL_DATA in sanitized


def test_sanitize_text_preserves_uuid_by_default() -> None:
    uuid_value = "550e8400-e29b-41d4-a716-446655440000"

    sanitized = sanitize_text(uuid_value)

    assert sanitized == uuid_value


def test_sanitize_text_applies_max_length() -> None:
    sanitized = sanitize_text(
        "a" * 100,
        max_length=10,
    )

    assert sanitized.startswith("a" * 10)
    assert TRUNCATED in sanitized


# ============================================================
# HASHES E PSEUDONIMIZAÇÃO
# ============================================================


def test_hash_identifier_is_stable() -> None:
    first = hash_identifier(
        "usuario-123",
        salt="salt-seguro-de-teste",
    )

    second = hash_identifier(
        "usuario-123",
        salt="salt-seguro-de-teste",
    )

    assert first == second


def test_hash_identifier_changes_for_different_value() -> None:
    first = hash_identifier(
        "usuario-123",
        salt="salt-seguro-de-teste",
    )

    second = hash_identifier(
        "usuario-456",
        salt="salt-seguro-de-teste",
    )

    assert first != second


def test_hash_identifier_changes_for_different_salt() -> None:
    first = hash_identifier(
        "usuario-123",
        salt="salt-um",
    )

    second = hash_identifier(
        "usuario-123",
        salt="salt-dois",
    )

    assert first != second


def test_hash_identifier_uses_prefix() -> None:
    result = hash_identifier(
        "usuario-123",
        salt="salt-seguro-de-teste",
        prefix="account",
    )

    assert result is not None
    assert result.startswith("account_")


@pytest.mark.parametrize(
    "value",
    (
        None,
        "",
        "   ",
    ),
)
def test_hash_identifier_returns_none_for_empty_values(
    value: str | None,
) -> None:
    result = hash_identifier(
        value,
        salt="salt-seguro-de-teste",
    )

    assert result is None


def test_hash_identifier_rejects_empty_salt() -> None:
    with pytest.raises(
        ValueError,
        match="salt",
    ):
        hash_identifier(
            "usuario-123",
            salt="",
        )


@pytest.mark.parametrize(
    "digest_size",
    (
        0,
        7,
        65,
        100,
    ),
)
def test_hash_identifier_rejects_invalid_digest_size(
    digest_size: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="digest_size",
    ):
        hash_identifier(
            "usuario-123",
            salt="salt-seguro-de-teste",
            digest_size=digest_size,
        )


def test_hash_identifier_accepts_default_digest_size() -> None:
    result = hash_identifier(
        "usuario-123",
        salt="salt-seguro-de-teste",
    )

    assert result is not None

    expected_hex_length = DEFAULT_HASH_DIGEST_SIZE * 2

    digest = result.split(
        "_",
        maxsplit=1,
    )[1]

    assert len(digest) == expected_hex_length


def test_content_hash_is_stable() -> None:
    first = content_hash("Documento financeiro de teste")

    second = content_hash("Documento financeiro de teste")

    assert first == second


def test_content_hash_changes_for_different_content() -> None:
    first = content_hash("Documento A")
    second = content_hash("Documento B")

    assert first != second


def test_content_hash_accepts_bytes() -> None:
    result = content_hash(b"conteudo-binario")

    assert isinstance(result, str)
    assert result


@pytest.mark.parametrize(
    "digest_size",
    (
        0,
        7,
        65,
    ),
)
def test_content_hash_rejects_invalid_digest_size(
    digest_size: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="digest_size",
    ):
        content_hash(
            "documento",
            digest_size=digest_size,
        )


# ============================================================
# SANITIZAÇÃO DE MAPEAMENTOS
# ============================================================


def test_sanitize_mapping_redacts_sensitive_keys() -> None:
    payload = {
        "api_key": "secret-api-key",
        "password": "secret-password",
        "database_url": ("postgresql://user:pass@host/db"),
        "authorization": "Bearer token",
    }

    sanitized = sanitize_mapping(payload)

    assert sanitized["api_key"] == REDACTED_SECRET
    assert sanitized["password"] == REDACTED_SECRET
    assert sanitized["database_url"] == REDACTED_SECRET
    assert sanitized["authorization"] == REDACTED_SECRET


@pytest.mark.parametrize(
    "field_name",
    (
        "token",
        "access_token",
        "refresh_token",
        "client_secret",
        "private_key",
        "gemini_api_key",
        "google_api_key",
        "wandb_api_key",
        "hmac_secret",
        "signing_secret",
        "encryption_key",
        "session_token",
        "cookie",
    ),
)
def test_sanitize_mapping_redacts_supported_secret_fields(
    field_name: str,
) -> None:
    sanitized = sanitize_mapping(
        {
            field_name: "valor-secreto",
        }
    )

    assert sanitized[field_name] == REDACTED_SECRET


@pytest.mark.parametrize(
    "field_name",
    (
        "email",
        "phone",
        "cpf",
        "cnpj",
        "full_name",
        "name",
        "nome",
        "address",
        "cep",
        "rg",
        "birth_date",
        "user_email",
        "user_name",
    ),
)
def test_sanitize_mapping_redacts_personal_fields(
    field_name: str,
) -> None:
    sanitized = sanitize_mapping(
        {
            field_name: "dado-pessoal",
        }
    )

    assert sanitized[field_name] == REDACTED_PERSONAL_DATA


@pytest.mark.parametrize(
    "field_name",
    (
        "income",
        "monthly_income",
        "salary",
        "expenses",
        "fixed_expenses",
        "variable_expenses",
        "debt",
        "debts",
        "reserve",
        "savings",
        "account_number",
        "bank_account",
        "credit_card",
        "card_number",
        "card_cvv",
        "financial_data",
        "financial_inputs",
    ),
)
def test_sanitize_mapping_redacts_financial_fields(
    field_name: str,
) -> None:
    sanitized = sanitize_mapping(
        {
            field_name: 3000,
        }
    )

    assert sanitized[field_name] == REDACTED_FINANCIAL_DATA


@pytest.mark.parametrize(
    "field_name",
    (
        "pix",
        "pix_key",
        "pix_keys",
        "chave_pix",
        "primary_pix_key",
    ),
)
def test_sanitize_mapping_redacts_pix_fields(
    field_name: str,
) -> None:
    sanitized = sanitize_mapping(
        {
            field_name: "usuario@exemplo.com",
        }
    )

    assert sanitized[field_name] in {
        REDACTED_PIX,
        REDACTED_FINANCIAL_DATA,
    }


def test_sanitize_mapping_can_preserve_personal_fields() -> None:
    payload = {
        "email": "usuario@exemplo.com",
    }

    sanitized = sanitize_mapping(
        payload,
        redact_personal_fields=False,
    )

    assert sanitized["email"] == REDACTED_EMAIL


def test_sanitize_mapping_can_preserve_financial_values() -> None:
    payload = {
        "income": 3000,
        "debt": 500,
    }

    sanitized = sanitize_mapping(
        payload,
        redact_financial_fields=False,
    )

    assert sanitized["income"] == 3000
    assert sanitized["debt"] == 500


def test_sanitize_mapping_limits_items() -> None:
    payload = {f"field_{index}": index for index in range(10)}

    sanitized = sanitize_mapping(
        payload,
        max_items=3,
    )

    regular_keys = [key for key in sanitized if key != "_truncated_items"]

    assert len(regular_keys) == 3
    assert sanitized["_truncated_items"] == 7


def test_sanitize_mapping_enforces_maximum_depth() -> None:
    payload = {
        "level_1": {
            "level_2": {
                "level_3": {
                    "value": "hidden",
                },
            },
        },
    }

    sanitized = sanitize_mapping(
        payload,
        max_depth=2,
    )

    assert MAX_DEPTH_REACHED in str(sanitized)


# ============================================================
# SANITIZAÇÃO DE SEQUÊNCIAS
# ============================================================


def test_sanitize_sequence_redacts_values() -> None:
    sequence = [
        "usuario@exemplo.com",
        "123.456.789-09",
        "conteúdo seguro",
    ]

    sanitized = sanitize_sequence(sequence)

    assert sanitized[0] == REDACTED_EMAIL
    assert sanitized[1] == REDACTED_DOCUMENT
    assert sanitized[2] == "conteúdo seguro"


def test_sanitize_sequence_limits_items() -> None:
    sequence = list(range(10))

    sanitized = sanitize_sequence(
        sequence,
        max_items=3,
    )

    assert sanitized[:3] == [
        0,
        1,
        2,
    ]

    assert sanitized[3] == f"{TRUNCATED}:7"


def test_sanitize_sequence_enforces_maximum_depth() -> None:
    sequence = [
        [
            [
                [
                    "conteúdo",
                ],
            ],
        ],
    ]

    sanitized = sanitize_sequence(
        sequence,
        max_depth=2,
    )

    assert MAX_DEPTH_REACHED in str(sanitized)


# ============================================================
# SANITIZADOR GENÉRICO
# ============================================================


def test_sanitize_value_returns_none() -> None:
    assert sanitize_value(None) is None


@pytest.mark.parametrize(
    "value",
    (
        True,
        False,
        1,
        1.5,
        0,
    ),
)
def test_sanitize_value_preserves_primitive_values(
    value: bool | int | float,
) -> None:
    assert sanitize_value(value) == value


def test_sanitize_value_handles_enum() -> None:
    sanitized = sanitize_value(ExampleStatus.ACTIVE)

    assert sanitized == "active"


def test_sanitize_value_handles_dataclass() -> None:
    payload = ExampleDataclassPayload(
        email="usuario@exemplo.com",
        income=3000,
        token="segredo",
        message="Mensagem segura",
    )

    sanitized = sanitize_value(payload)

    assert sanitized["email"] == REDACTED_PERSONAL_DATA
    assert sanitized["income"] == REDACTED_FINANCIAL_DATA
    assert sanitized["token"] == REDACTED_SECRET
    assert sanitized["message"] == "Mensagem segura"


def test_sanitize_value_handles_pydantic_model() -> None:
    payload = ExamplePydanticPayload(
        email="usuario@exemplo.com",
        monthly_income=3000,
        api_key="segredo",
        description="Teste seguro",
    )

    sanitized = sanitize_value(payload)

    assert sanitized["email"] == REDACTED_PERSONAL_DATA
    assert sanitized["monthly_income"] == REDACTED_FINANCIAL_DATA
    assert sanitized["api_key"] == REDACTED_SECRET
    assert sanitized["description"] == "Teste seguro"


def test_sanitize_value_handles_exception() -> None:
    error = RuntimeError(
        "Erro em postgresql://user:pass@host/db para usuario@exemplo.com"
    )

    sanitized = sanitize_value(error)
    rendered = str(sanitized)

    assert "postgresql://" not in rendered
    assert "usuario@exemplo.com" not in rendered
    assert sanitized["type"] == "RuntimeError"


def test_sanitize_value_handles_binary_data() -> None:
    sanitized = sanitize_value(b"secret binary data")

    assert REDACTED_BINARY in sanitized
    assert "18 bytes" in sanitized


def test_sanitize_value_handles_bytearray() -> None:
    value = bytearray(b"binary")

    sanitized = sanitize_value(value)

    assert REDACTED_BINARY in sanitized
    assert "6 bytes" in sanitized


def test_sanitize_value_handles_unknown_object() -> None:
    sanitized = sanitize_value(UnknownObject())

    assert "usuario@exemplo.com" not in sanitized
    assert "segredo123" not in sanitized
    assert REDACTED_EMAIL in sanitized


# ============================================================
# CABEÇALHOS HTTP
# ============================================================


@pytest.mark.parametrize(
    "header_name",
    (
        "Authorization",
        "Cookie",
        "Proxy-Authorization",
        "Set-Cookie",
        "X-API-Key",
        "X-Auth-Token",
        "X-INNA-Signature",
        "X-Internal-Token",
    ),
)
def test_sanitize_headers_redacts_sensitive_headers(
    header_name: str,
) -> None:
    sanitized = sanitize_headers(
        {
            header_name: "segredo",
        }
    )

    assert sanitized[header_name] == REDACTED_AUTH


def test_sanitize_headers_preserves_safe_headers() -> None:
    sanitized = sanitize_headers(
        {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Request-ID": "request-123",
        }
    )

    assert sanitized["Content-Type"] == "application/json"
    assert sanitized["Accept"] == "application/json"
    assert sanitized["X-Request-ID"] == "request-123"


def test_sanitize_headers_allowlist_removes_unknown_headers() -> None:
    sanitized = sanitize_headers(
        {
            "Content-Type": "application/json",
            "X-Unknown": "valor",
            "Authorization": "Bearer segredo",
        },
        allow_only_safe_headers=True,
    )

    assert "Content-Type" in sanitized
    assert "Authorization" in sanitized
    assert "X-Unknown" not in sanitized


def test_sanitize_headers_sanitizes_value_content() -> None:
    sanitized = sanitize_headers(
        {
            "User-Agent": ("client usuario@exemplo.com"),
        }
    )

    assert "usuario@exemplo.com" not in (sanitized["User-Agent"])


# ============================================================
# EXCEÇÕES
# ============================================================


def test_sanitize_exception_includes_type_by_default() -> None:
    sanitized = sanitize_exception(RuntimeError("Falha segura"))

    assert sanitized["type"] == "RuntimeError"
    assert sanitized["message"] == "Falha segura"


def test_sanitize_exception_can_omit_type() -> None:
    sanitized = sanitize_exception(
        ValueError("Falha"),
        include_type=False,
    )

    assert "type" not in sanitized
    assert sanitized["message"] == "Falha"


def test_sanitize_exception_redacts_sensitive_content() -> None:
    error = RuntimeError(
        "Falha com Bearer segredo123 em "
        "postgresql://user:pass@host/db "
        "para usuario@exemplo.com"
    )

    sanitized = sanitize_exception(error)
    rendered = str(sanitized)

    assert "segredo123" not in rendered
    assert "postgresql://" not in rendered
    assert "usuario@exemplo.com" not in rendered


def test_sanitize_exception_limits_message_size() -> None:
    error = RuntimeError("x" * 100)

    sanitized = sanitize_exception(
        error,
        max_string_length=10,
    )

    assert TRUNCATED in sanitized["message"]


# ============================================================
# CHAVES PIX
# ============================================================


@pytest.mark.parametrize(
    "pix_key",
    (
        "123.456.789-09",
        "12.345.678/0001-90",
        "usuario@exemplo.com",
        "+5514999999999",
        "550e8400-e29b-41d4-a716-446655440000",
        "chave-personalizada",
    ),
)
def test_sanitize_pix_key_always_redacts(
    pix_key: str,
) -> None:
    assert sanitize_pix_key(pix_key) == REDACTED_PIX


def test_sanitize_pix_key_preserves_empty_value() -> None:
    assert sanitize_pix_key("") == ""
    assert sanitize_pix_key("   ") == ""


# ============================================================
# DETECÇÃO DE SEGREDOS
# ============================================================


@pytest.mark.parametrize(
    "value",
    (
        "postgresql://user:pass@host/db",
        "Authorization: Bearer segredo",
        "Authorization: Basic dXNlcjpwYXNz",
        ("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.signature"),
        "api_key=segredo123",
        """
-----BEGIN PRIVATE KEY-----
private-content
-----END PRIVATE KEY-----
""",
    ),
)
def test_contains_possible_secret_detects_secret(
    value: str,
) -> None:
    assert contains_possible_secret(
        {
            "value": value,
        }
    )


def test_contains_possible_secret_accepts_safe_payload() -> None:
    assert not contains_possible_secret(
        {
            "message": "Conteúdo seguro",
            "status": "success",
        }
    )


# ============================================================
# DETECÇÃO DE DADOS PESSOAIS
# ============================================================


@pytest.mark.parametrize(
    "value",
    (
        "usuario@exemplo.com",
        "(14) 99999-9999",
        "123.456.789-09",
        "12.345.678/0001-90",
    ),
)
def test_contains_possible_personal_data_detects_values(
    value: str,
) -> None:
    assert contains_possible_personal_data(
        {
            "message": value,
        }
    )


def test_contains_possible_personal_data_accepts_safe_payload() -> None:
    assert not contains_possible_personal_data(
        {
            "message": "Conteúdo sem dado pessoal",
        }
    )


# ============================================================
# BLOQUEIO DE EXPORTAÇÃO
# ============================================================


def test_assert_safe_for_external_export_blocks_secret() -> None:
    with pytest.raises(
        ValueError,
        match="segredo",
    ):
        assert_safe_for_external_export(
            {
                "database": ("postgresql://user:pass@host/db"),
            }
        )


def test_assert_safe_for_external_export_blocks_personal_data() -> None:
    with pytest.raises(
        ValueError,
        match="dado pessoal",
    ):
        assert_safe_for_external_export(
            {
                "message": "usuario@exemplo.com",
            }
        )


def test_assert_safe_for_external_export_can_allow_personal_check_off() -> None:
    assert_safe_for_external_export(
        {
            "message": "usuario@exemplo.com",
        },
        block_personal_data=False,
    )


def test_assert_safe_for_external_export_accepts_safe_payload() -> None:
    assert_safe_for_external_export(
        {
            "message": "Conteúdo seguro",
            "status": "completed",
        }
    )


# ============================================================
# PAYLOAD EXTERNO
# ============================================================


def test_prepare_external_payload_redacts_every_sensitive_category() -> None:
    payload = {
        "email": "usuario@exemplo.com",
        "phone": "(14) 99999-9999",
        "cpf": "123.456.789-09",
        "api_key": "chave-secreta",
        "database_url": ("postgresql://user:pass@host/db"),
        "financial_data": {
            "income": 3000,
            "debt": 500,
        },
        "pix_key": "usuario@exemplo.com",
        "trace_id": ("550e8400-e29b-41d4-a716-446655440000"),
    }

    sanitized = prepare_external_payload(payload)
    rendered = safe_json_dumps(sanitized)

    assert "usuario@exemplo.com" not in rendered
    assert "99999-9999" not in rendered
    assert "123.456.789-09" not in rendered
    assert "chave-secreta" not in rendered
    assert "postgresql://" not in rendered
    assert '"income": 3000' not in rendered
    assert '"debt": 500' not in rendered
    assert "550e8400-e29b-41d4-a716-446655440000" not in rendered


def test_prepare_external_payload_preserves_safe_metadata() -> None:
    payload = {
        "status": "completed",
        "agent": "financial_agent",
        "intent": "diagnostico_financeiro",
    }

    sanitized = prepare_external_payload(payload)

    assert sanitized == payload


def test_prepare_external_payload_limits_large_strings() -> None:
    payload = {
        "message": "a" * 100,
    }

    sanitized = prepare_external_payload(
        payload,
        max_string_length=10,
    )

    assert TRUNCATED in sanitized["message"]


def test_prepare_external_payload_limits_items() -> None:
    payload = {f"field_{index}": index for index in range(10)}

    sanitized = prepare_external_payload(
        payload,
        max_items=3,
    )

    assert sanitized["_truncated_items"] == 7


# ============================================================
# PAYLOAD INTERNO
# ============================================================


def test_prepare_internal_payload_removes_personal_data() -> None:
    payload = {
        "email": "usuario@exemplo.com",
        "message": "Contato usuario@exemplo.com",
    }

    sanitized = prepare_internal_payload(payload)
    rendered = str(sanitized)

    assert "usuario@exemplo.com" not in rendered


def test_prepare_internal_payload_preserves_financial_values() -> None:
    payload = {
        "financial_context": {
            "monthly_income": 3000,
            "debt": 500,
        },
    }

    sanitized = prepare_internal_payload(payload)

    assert sanitized["financial_context"]["monthly_income"] == 3000
    assert sanitized["financial_context"]["debt"] == 500


def test_prepare_internal_payload_blocks_remaining_secret() -> None:
    class SecretObject:
        def __repr__(self) -> str:
            return "postgresql://user:pass@host/db"

    sanitized = prepare_internal_payload(
        {
            "unknown": SecretObject(),
        }
    )

    assert "postgresql://" not in str(sanitized)


# ============================================================
# SERIALIZAÇÃO JSON
# ============================================================


def test_safe_json_dumps_returns_valid_json_string() -> None:
    rendered = safe_json_dumps(
        {
            "status": "completed",
            "score": 0.95,
        }
    )

    assert isinstance(rendered, str)
    assert '"status": "completed"' in rendered
    assert '"score": 0.95' in rendered


def test_safe_json_dumps_redacts_secrets() -> None:
    rendered = safe_json_dumps(
        {
            "api_key": "super-segredo",
            "authorization": "Bearer token",
        }
    )

    assert "super-segredo" not in rendered
    assert "Bearer token" not in rendered
    assert REDACTED_SECRET in rendered


def test_safe_json_dumps_redacts_personal_fields() -> None:
    rendered = safe_json_dumps(
        {
            "email": "usuario@exemplo.com",
        }
    )

    assert "usuario@exemplo.com" not in rendered
    assert REDACTED_PERSONAL_DATA in rendered


def test_safe_json_dumps_can_preserve_financial_values() -> None:
    rendered = safe_json_dumps(
        {
            "income": 3000,
        },
        redact_financial_fields=False,
    )

    assert "3000" in rendered


def test_safe_json_dumps_can_disable_ascii_escaping() -> None:
    rendered = safe_json_dumps(
        {
            "message": "Avaliação concluída",
        },
        ensure_ascii=False,
    )

    assert "Avaliação concluída" in rendered


# ============================================================
# NOMES SEGUROS DE ARTEFATOS
# ============================================================


@pytest.mark.parametrize(
    ("original", "expected"),
    (
        (
            "Relatório Avaliação INNA.json",
            "relat-rio-avalia-o-inna.json",
        ),
        (
            "../../resultado.json",
            "resultado.json",
        ),
        (
            r"..\..\resultado.json",
            "resultado.json",
        ),
        (
            "  Relatório Final  ",
            "relat-rio-final",
        ),
    ),
)
def test_safe_artifact_name_normalizes_values(
    original: str,
    expected: str,
) -> None:
    assert safe_artifact_name(original) == expected


def test_safe_artifact_name_uses_default_for_empty_value() -> None:
    assert (
        safe_artifact_name(
            "",
            default="evaluation",
        )
        == "evaluation"
    )


def test_safe_artifact_name_limits_length() -> None:
    result = safe_artifact_name(
        "a" * 200,
        max_length=20,
    )

    assert len(result) == 20


def test_safe_artifact_name_blocks_path_traversal() -> None:
    artifact_name = safe_artifact_name("../../Relatório INNA.json")

    assert ".." not in artifact_name
    assert "/" not in artifact_name
    assert "\\" not in artifact_name


# ============================================================
# VALIDAÇÃO DE LIMITES
# ============================================================


@pytest.mark.parametrize(
    ("function_name", "kwargs"),
    (
        (
            "mapping_depth",
            {
                "max_depth": 0,
            },
        ),
        (
            "mapping_items",
            {
                "max_items": 0,
            },
        ),
        (
            "mapping_string",
            {
                "max_string_length": 0,
            },
        ),
    ),
)
def test_sanitize_mapping_rejects_invalid_limits(
    function_name: str,
    kwargs: dict[str, int],
) -> None:
    del function_name

    with pytest.raises(ValueError):
        sanitize_mapping(
            {
                "message": "teste",
            },
            **kwargs,
        )


@pytest.mark.parametrize(
    "kwargs",
    (
        {
            "max_depth": 0,
        },
        {
            "max_items": 0,
        },
        {
            "max_string_length": 0,
        },
    ),
)
def test_sanitize_sequence_rejects_invalid_limits(
    kwargs: dict[str, int],
) -> None:
    with pytest.raises(ValueError):
        sanitize_sequence(
            [
                "teste",
            ],
            **kwargs,
        )


@pytest.mark.parametrize(
    "kwargs",
    (
        {
            "max_depth": 0,
        },
        {
            "max_items": 0,
        },
        {
            "max_string_length": 0,
        },
    ),
)
def test_sanitize_value_rejects_invalid_limits(
    kwargs: dict[str, int],
) -> None:
    with pytest.raises(ValueError):
        sanitize_value(
            {
                "message": "teste",
            },
            **kwargs,
        )
