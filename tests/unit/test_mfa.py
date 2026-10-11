"""MFA vectors and security boundaries; PostgreSQL is mocked in these unit tests."""

import base64
import json
from contextlib import contextmanager

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.inna_platform.services.finance import finance_auth_routes as auth
from src.inna_platform.services.finance import mfa

SECRET = base64.b32encode(b"12345678901234567890").decode()
USER = {"user_id": "alice", "email": "alice@example.com"}
ORIGIN = "https://sabino-ai-plataforma-inna.onrender.com"
HEADERS = {"Origin": ORIGIN, "X-Sabino-MFA": "1"}


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    monkeypatch.setenv(
        "SABINO_MFA_ENCRYPTION_KEY", "test-only-key-never-used-in-production-1234"
    )
    monkeypatch.setenv("SABINO_PUBLIC_URL", ORIGIN)
    monkeypatch.setattr(mfa, "ensure_schema", lambda: None)
    monkeypatch.setattr(mfa.recovery, "allow", lambda *args: True)
    monkeypatch.setattr(mfa.time, "time", lambda: 1234567890)


@pytest.mark.parametrize(
    "timestamp,expected",
    [
        (59, "94287082"),
        (1111111109, "07081804"),
        (1111111111, "14050471"),
        (1234567890, "89005924"),
        (2000000000, "69279037"),
        (20000000000, "65353130"),
    ],
)
def test_rfc6238_sha1_vectors(timestamp, expected):
    assert mfa.totp(SECRET, timestamp // 30, digits=8) == expected


def test_reject_replayed_expired_and_malformed_codes():
    step = 1234567890 // 30
    code = mfa.totp(SECRET, step)
    assert mfa.matching_step(SECRET, code) == step
    assert mfa.matching_step(SECRET, code, last_step=step) is None
    assert mfa.matching_step(SECRET, mfa.totp(SECRET, step - 2)) is None
    assert mfa.matching_step(SECRET, "abcdef") is None
    assert mfa.matching_step(SECRET, "12345") is None


def test_encrypted_seed_is_owner_bound_and_randomized():
    encrypted = mfa.seal("alice", SECRET)
    assert SECRET not in encrypted
    assert mfa.unseal("alice", encrypted) == SECRET
    assert encrypted != mfa.seal("alice", SECRET)
    with pytest.raises(ValueError):
        mfa.unseal("bob", encrypted)


def test_missing_key_cannot_decrypt_or_enroll(monkeypatch):
    monkeypatch.delenv("SABINO_MFA_ENCRYPTION_KEY")
    assert not mfa.available()
    with pytest.raises(HTTPException) as error:
        mfa.seal("alice", SECRET)
    assert error.value.status_code == 503


class Cursor:
    def __init__(self, row):
        self.row = row
        self.statements = []

    def execute(self, sql, params=()):
        self.statements.append((sql, params))
        if "SET last_step=" in sql:
            self.row["last_step"] = params[0]
        if "SET recovery_hashes=" in sql:
            self.row["recovery_hashes"] = json.loads(params[0])

    def fetchone(self):
        return self.row


def database(monkeypatch, row):
    cursor = Cursor(row)

    @contextmanager
    def mocked(**kwargs):
        yield cursor

    monkeypatch.setattr(mfa, "cursor_postgres", mocked)
    monkeypatch.setattr(mfa, "lock_user", lambda *args: USER)
    return cursor


def enrollment(enabled=True):
    return {
        "secret": mfa.seal("alice", SECRET),
        "enabled": enabled,
        "last_step": -1,
        "recovery_hashes": [],
        "valid": True,
    }


def inserted(cur):
    return [sql for sql, _ in cur.statements if "INSERT INTO inna_auth_sessions" in sql]


def test_password_alone_never_creates_session(monkeypatch):
    cur = database(monkeypatch, enrollment())
    assert mfa.login_session(USER, "password", "") is None
    assert not inserted(cur)


def test_wrong_code_never_creates_session(monkeypatch):
    cur = database(monkeypatch, enrollment())
    with pytest.raises(HTTPException):
        mfa.login_session(USER, "password", "invalid")
    assert not inserted(cur)


def test_valid_totp_creates_session_once_and_stores_only_hash(monkeypatch):
    cur = database(monkeypatch, enrollment())
    code = mfa.totp(SECRET, 1234567890 // 30)
    session = mfa.login_session(USER, "password", code)
    assert len(inserted(cur)) == 1
    assert session["session_token"] not in str(cur.statements)
    with pytest.raises(HTTPException):
        mfa.login_session(USER, "password", code)
    assert len(inserted(cur)) == 1


def test_recovery_code_is_single_use_and_user_bound(monkeypatch):
    row = enrollment()
    code = "A1B2C3D4-E5F60718-AABBCCDD"
    row["recovery_hashes"] = [mfa.recovery_hash("alice", code)]
    assert mfa.recovery_hash("bob", code) != row["recovery_hashes"][0]
    cur = database(monkeypatch, row)
    mfa.login_session(USER, "password", code.lower())
    assert row["recovery_hashes"] == []
    with pytest.raises(HTTPException):
        mfa.login_session(USER, "password", code)
    assert len(inserted(cur)) == 1


def test_non_enrolled_account_keeps_password_login(monkeypatch):
    cur = database(monkeypatch, None)
    assert mfa.login_session(USER, "password", "")["session_token"]
    assert len(inserted(cur)) == 1


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(auth, "authenticate_user", lambda **kwargs: USER)
    app = FastAPI()
    app.include_router(auth.router)
    app.middleware("http")(mfa.account_page_gate)

    @app.get("/dashboard")
    def dashboard():
        return {"private": True}

    return TestClient(app)


def test_http_requires_second_factor_and_does_not_set_cookie(client, monkeypatch):
    database(monkeypatch, enrollment())
    response = client.post(
        "/auth/login", json={"email": USER["email"], "password": "password"}
    )
    assert response.json() == {"authenticated": False, "mfa_required": True}
    assert "set-cookie" not in response.headers
    assert response.headers["cache-control"] == "no-store"
    assert client.get("/dashboard", follow_redirects=False).status_code == 303


def test_totp_success_sets_httponly_cookie(client, monkeypatch):
    database(monkeypatch, enrollment())
    response = client.post(
        "/auth/login",
        json={
            "email": USER["email"],
            "password": "password",
            "mfa_code": mfa.totp(SECRET, 1234567890 // 30),
        },
    )
    assert response.json()["authenticated"] is True
    assert "HttpOnly" in response.headers["set-cookie"]


def test_settings_require_session_and_origin(client, monkeypatch):
    assert client.get("/auth/mfa/status").status_code == 401
    response = client.post("/auth/mfa/setup", json={"password": "test-password"})
    assert response.status_code == 403
    assert (
        client.post(
            "/auth/mfa/setup", headers=HEADERS, json={"password": "test-password"}
        ).status_code
        == 401
    )


def test_activation_revokes_existing_sessions_and_returns_codes_once(
    client, monkeypatch
):
    monkeypatch.setattr(mfa, "current_user", lambda request: USER)
    cur = database(monkeypatch, enrollment(enabled=False))
    response = client.post(
        "/auth/mfa/confirm",
        headers=HEADERS,
        json={"password": "test-password", "code": mfa.totp(SECRET, 1234567890 // 30)},
    )
    assert response.status_code == 200
    codes = response.json()["recovery_codes"]
    assert len(set(codes)) == 8
    assert all(code not in str(cur.statements) for code in codes)
    assert any("revoked_at=NOW()" in sql for sql, _ in cur.statements)
    assert "set-cookie" not in response.headers
    assert response.headers["cache-control"] == "no-store"


def test_expired_enrollment_cannot_activate(client, monkeypatch):
    monkeypatch.setattr(mfa, "current_user", lambda request: USER)
    row = enrollment(False)
    row["valid"] = False
    cur = database(monkeypatch, row)
    assert (
        client.post(
            "/auth/mfa/confirm",
            headers=HEADERS,
            json={"password": "test-password", "code": "123456"},
        ).status_code
        == 400
    )
    assert not any("enabled=TRUE" in sql for sql, _ in cur.statements)


def test_rate_limit_blocks_even_correct_credentials(client, monkeypatch):
    monkeypatch.setattr(mfa.recovery, "allow", lambda *args: False)
    monkeypatch.setattr(
        auth,
        "authenticate_user",
        lambda **kwargs: pytest.fail("must throttle before password verification"),
    )
    assert (
        client.post(
            "/auth/login", json={"email": USER["email"], "password": "password"}
        ).status_code
        == 429
    )


def test_key_loss_never_bypasses_mfa(client, monkeypatch):
    cur = database(monkeypatch, enrollment())
    monkeypatch.delenv("SABINO_MFA_ENCRYPTION_KEY")
    response = client.post(
        "/auth/login",
        json={"email": USER["email"], "password": "password", "mfa_code": "123456"},
    )
    assert response.status_code == 503
    assert not inserted(cur)
    assert "set-cookie" not in response.headers


def test_setup_generates_local_qr_with_server_identity(client, monkeypatch):
    monkeypatch.setattr(mfa, "current_user", lambda request: USER)
    database(monkeypatch, None)
    response = client.post(
        "/auth/mfa/setup", headers=HEADERS, json={"password": "test-password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["qr_data_uri"].startswith("data:image/svg+xml;base64,")
    assert b"<svg" in base64.b64decode(data["qr_data_uri"].split(",")[1])
    from urllib.parse import parse_qs, unquote, urlparse

    assert unquote(urlparse(data["uri"]).path) == "/Sabino.AI:alice@example.com"
    assert parse_qs(urlparse(data["uri"]).query)["secret"] == [data["secret"]]
    assert response.headers["cache-control"] == "no-store"

