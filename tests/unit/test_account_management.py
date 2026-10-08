from contextlib import contextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.inna_platform.services.finance import account_management as accounts
from src.inna_platform.services.finance import finance_auth_routes as auth
from src.inna_platform.services.finance.finance_identity import verify_password

ORIGIN = "https://sabino-ai-plataforma-inna.onrender.com"
HEADERS = {"Origin": ORIGIN, "X-Sabino-Account": "1"}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("SABINO_PUBLIC_URL", ORIGIN)
    monkeypatch.setattr(accounts, "ensure_schema", lambda: None)
    monkeypatch.setattr(accounts.recovery, "allow", lambda *args: True)
    app = FastAPI()
    app.include_router(auth.router)
    return TestClient(app)


def payload(**changes):
    return {
        "name": "  Ana   Silva ",
        "email": " ANA@EXAMPLE.COM ",
        "password": "test-only-passphrase",
        **changes,
    }


def test_registration_normalizes_and_does_not_grant_session(client, monkeypatch):
    received = []
    monkeypatch.setattr(
        accounts, "insert_account", lambda *args: received.append(args) or True
    )
    response = client.post("/auth/register", json=payload(), headers=HEADERS)
    assert response.status_code == 201
    assert received == [("Ana Silva", "ana@example.com", "test-only-passphrase")]
    assert "set-cookie" not in response.headers
    assert response.headers["cache-control"] == "no-store"
    assert "password" not in response.text


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Origin": "https://evil.example", "X-Sabino-Account": "1"},
        {"Origin": ORIGIN},
    ],
)
def test_signup_rejects_cross_origin(client, monkeypatch, headers):
    monkeypatch.setattr(
        accounts, "insert_account", lambda *args: pytest.fail("must not create")
    )
    assert (
        client.post("/auth/register", json=payload(), headers=headers).status_code
        == 403
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"password": "short"},
        {"password": "x" * 129},
        {"name": "  "},
        {"email": "a@"},
        {"email": "a@x com"},
        {"user_id": "victim"},
        {"active": True},
    ],
)
def test_signup_rejects_invalid_or_privileged_fields(client, monkeypatch, changes):
    monkeypatch.setattr(
        accounts, "insert_account", lambda *args: pytest.fail("must not create")
    )
    assert client.post(
        "/auth/register", json=payload(**changes), headers=HEADERS
    ).status_code in {400, 422}


def test_duplicate_does_not_return_success(client, monkeypatch):
    monkeypatch.setattr(accounts, "insert_account", lambda *args: False)
    assert (
        client.post("/auth/register", json=payload(), headers=HEADERS).status_code
        == 409
    )


def test_rate_limit_stops_creation(client, monkeypatch):
    monkeypatch.setattr(accounts.recovery, "allow", lambda *args: False)
    monkeypatch.setattr(
        accounts, "insert_account", lambda *args: pytest.fail("must not create")
    )
    assert (
        client.post("/auth/register", json=payload(), headers=HEADERS).status_code
        == 429
    )


def test_database_errors_are_sanitized(client, monkeypatch):
    def fail(*args):
        raise RuntimeError("postgres://secret@example/password")

    monkeypatch.setattr(accounts, "insert_account", fail)
    response = client.post("/auth/register", json=payload(), headers=HEADERS)
    assert response.status_code == 503
    assert "secret" not in response.text


def test_profile_requires_session(client):
    assert client.get("/auth/profile").status_code == 401
    assert (
        client.patch("/auth/profile", json={"name": "Ana"}, headers=HEADERS).status_code
        == 401
    )


def test_profile_uses_server_identity_and_does_not_change_email(client, monkeypatch):
    queries = []
    monkeypatch.setattr(
        accounts,
        "current_user",
        lambda request: {"user_id": "owner", "email": "ana@example.com"},
    )

    class Cursor:
        def execute(self, sql, params):
            queries.append((sql, params))

        def fetchone(self):
            return {"name": "Ana"}

    @contextmanager
    def cursor(**kwargs):
        yield Cursor()

    monkeypatch.setattr(accounts, "cursor_postgres", cursor)
    assert client.get("/auth/profile").json()["user"]["name"] == "Ana"
    response = client.patch(
        "/auth/profile", json={"name": "Ana Maria"}, headers=HEADERS
    )
    assert response.status_code == 200
    assert queries[-1][1] == ("owner", "Ana Maria")
    assert response.headers["cache-control"] == "no-store"
    assert (
        client.patch(
            "/auth/profile",
            json={"name": "Ana", "email": "victim@example.com"},
            headers=HEADERS,
        ).status_code
        == 422
    )
    assert (
        client.patch(
            "/auth/profile", json={"name": "Ana", "user_id": "victim"}, headers=HEADERS
        ).status_code
        == 422
    )
    assert client.patch("/auth/profile", json={"name": "Ana"}).status_code == 403


@pytest.mark.parametrize("duplicate", [False, True])
def test_insert_hashes_password_and_preserves_existing_account(monkeypatch, duplicate):
    statements = []

    class Cursor:
        def execute(self, sql, params):
            statements.append((sql, params))

        def fetchone(self):
            return None if duplicate else {"user_id": "new"}

    @contextmanager
    def cursor(**kwargs):
        assert kwargs["commit_automatico"] is True
        yield Cursor()

    monkeypatch.setattr(accounts, "cursor_postgres", cursor)
    assert (
        accounts.insert_account("Ana", "ana@example.com", "test-only-passphrase")
        is not duplicate
    )
    sql, params = statements[0]
    assert "ON CONFLICT(email) DO NOTHING" in sql
    assert verify_password(
        "test-only-passphrase", salt_hex=params[2], expected_hash_hex=params[3]
    )
    assert len(statements) == (1 if duplicate else 2)
    if not duplicate:
        assert statements[1][1] == (params[0], "Ana")


def test_public_pages_and_capabilities(client):
    for path in ["/cadastro", "/minha-conta"]:
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["cache-control"] == "no-store"
    assert client.get("/auth/capabilities").json()["registration"] is True


def test_existing_login_and_logout_still_work(client, monkeypatch):
    monkeypatch.setattr(
        auth,
        "authenticate_user",
        lambda **kwargs: {"user_id": "owner", "email": "ana@example.com"},
    )
    monkeypatch.setattr(
        auth, "create_session", lambda **kwargs: {"session_token": "test-token"}
    )
    monkeypatch.setattr(
        auth,
        "resolve_session_user",
        lambda token: {"user_id": "owner", "email": "ana@example.com"},
    )
    revoked = []
    monkeypatch.setattr(auth, "revoke_session", revoked.append)
    response = client.post(
        "/auth/login",
        json={"email": "ana@example.com", "password": "test-only-passphrase"},
    )
    assert response.status_code == 200
    assert "HttpOnly" in response.headers["set-cookie"]
    assert client.get("/auth/me").status_code == 200
    assert client.post("/auth/logout").status_code == 200
    assert revoked == ["test-token"]
    assert client.get("/auth/me").status_code == 401


def test_invalid_login_email_is_rejected_without_server_error(client, monkeypatch):
    def invalid(**kwargs):
        raise ValueError("email inválido")

    monkeypatch.setattr(auth, "authenticate_user", invalid)
    assert (
        client.post(
            "/auth/login", json={"email": "invalid", "password": "test-only-passphrase"}
        ).status_code
        == 401
    )


def test_recovery_routes_keep_origin_and_token_validation(client, monkeypatch):
    recovery = accounts.recovery
    monkeypatch.setattr(recovery, "ensure_schema", lambda: None)
    assert (
        client.post(
            "/auth/password/forgot", json={"email": "ana@example.com"}
        ).status_code
        == 403
    )
    response = client.post(
        "/auth/password/reset",
        json={"token": "!" * 43, "password": "test-only-passphrase"},
        headers={"Origin": ORIGIN, "X-Sabino-Recovery": "1"},
    )
    assert response.status_code == 400
    assert "expirado" in response.json()["detail"]
