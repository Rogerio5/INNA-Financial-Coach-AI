"""Optional TOTP: encrypted seeds, atomic replay protection and recovery codes.

SABINO_MFA_ENCRYPTION_KEY must be a stable, random secret of at least 32 characters.
Its absence prevents enrollment and fails closed for an already-enrolled account.
"""

import base64
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import struct
import time
from pathlib import Path
from urllib.parse import quote, urlencode

import qrcode
import qrcode.image.svg
from cryptography.fernet import Fernet
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from . import password_recovery as recovery
from .finance_identity import cursor_postgres, hash_session_token, verify_password

router = APIRouter()


def qr_data_uri(uri):
    output = io.BytesIO()
    qrcode.make(uri, image_factory=qrcode.image.svg.SvgPathImage).save(output)
    return "data:image/svg+xml;base64," + base64.b64encode(output.getvalue()).decode()


async def account_page_gate(request, call_next):
    path = request.url.path.rstrip("/")
    protected = {
        "/dashboard",
        "/modulos",
        "/inna",
        "/minha-conta",
        "/conta",
        "/seguranca-conta",
        "/static/sabino-dashboard.html",
        "/static/sabino-modulos.html",
        "/static/sabino-inna.html",
        "/static/sabino-mfa.html",
    }
    if path in protected:
        try:
            current_user(request)
        except HTTPException as exc:
            if exc.status_code == 401:
                return RedirectResponse(
                    "/", status_code=303, headers={"Cache-Control": "no-store"}
                )
            raise
    response = await call_next(request)
    if path in protected:
        response.headers["Cache-Control"] = "no-store"
    return response


def cipher():
    key = os.getenv("SABINO_MFA_ENCRYPTION_KEY", "")
    if len(key) < 32:
        raise HTTPException(503, "Autenticador temporariamente indisponível.")
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest()))


def available():
    return len(os.getenv("SABINO_MFA_ENCRYPTION_KEY", "")) >= 32


def seal(user_id, secret):
    return cipher().encrypt(json.dumps([user_id, secret]).encode()).decode()


def unseal(user_id, encrypted):
    owner, secret = json.loads(cipher().decrypt(encrypted.encode()))
    if not hmac.compare_digest(owner, user_id):
        raise ValueError("MFA owner mismatch")
    return secret


def totp(secret, step, digits=6):
    key = base64.b32decode(secret + "=" * (-len(secret) % 8))
    digest = hmac.new(key, struct.pack(">Q", step), hashlib.sha1).digest()
    offset = digest[-1] & 15
    value = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(value % (10**digits)).zfill(digits)


def matching_step(secret, code, last_step=-1, now=None):
    if not re.fullmatch(r"[0-9]{6}", code):
        return None
    current = int(time.time() if now is None else now) // 30
    for step in (current, current - 1, current + 1):
        if step > last_step and hmac.compare_digest(totp(secret, step), code):
            return step
    return None


def recovery_hash(user_id, code):
    normalized = code.replace("-", "").replace(" ", "").upper()
    return hashlib.sha256((user_id + ":" + normalized).encode()).hexdigest()


def ensure_schema():
    recovery.ensure_schema()
    with cursor_postgres() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS inna_auth_mfa (
            user_id TEXT PRIMARY KEY REFERENCES inna_auth_users(user_id) ON DELETE CASCADE,
            secret TEXT NOT NULL, enabled BOOLEAN NOT NULL DEFAULT FALSE,
            expires_at TIMESTAMPTZ, last_step BIGINT NOT NULL DEFAULT -1,
            recovery_hashes JSONB NOT NULL DEFAULT '[]'::jsonb)""")



def throttle(bucket, maximum=20):
    if not recovery.allow("mfa:" + bucket, maximum):
        raise HTTPException(429, "Muitas tentativas. Tente novamente mais tarde.")


def login_limit(email):
    ensure_schema()
    throttle("login:" + recovery.digest(email.strip().lower()), 60)
    throttle("login:global", 1000)


def lock_user(cur, user_id, password):
    cur.execute(
        """SELECT user_id,email,password_salt,password_hash FROM inna_auth_users
        WHERE user_id=%s AND active=TRUE FOR UPDATE""",
        (user_id,),
    )
    user = cur.fetchone()
    if not user or not verify_password(
        password,
        salt_hex=user["password_salt"],
        expected_hash_hex=user["password_hash"],
    ):
        raise HTTPException(401, "Credenciais inválidas.")
    return user


def consume(cur, user_id, row, code):
    # User row lock serializes login, activation, removal and password recovery.
    step = matching_step(unseal(user_id, row["secret"]), code, row["last_step"])
    if step is not None:
        cur.execute(
            "UPDATE inna_auth_mfa SET last_step=%s WHERE user_id=%s", (step, user_id)
        )
        return True
    hashes = row["recovery_hashes"]
    candidate = recovery_hash(user_id, code)
    for stored in hashes:
        if hmac.compare_digest(candidate, stored):
            remaining = [value for value in hashes if value != stored]
            cur.execute(
                "UPDATE inna_auth_mfa SET recovery_hashes=%s::jsonb WHERE user_id=%s",
                (json.dumps(remaining), user_id),
            )
            return True
    return False


def login_session(user, password, code):
    """No session is inserted until both factors succeed in the same transaction."""
    user_id = user["user_id"]
    with cursor_postgres(dict_cursor=True) as cur:
        lock_user(cur, user_id, password)
        cur.execute("SELECT * FROM inna_auth_mfa WHERE user_id=%s", (user_id,))
        row = cur.fetchone()
        if row and row["enabled"]:
            if not code:
                return None
            if not consume(cur, user_id, row, code.strip()):
                raise HTTPException(401, "Código inválido, expirado ou já utilizado.")
        token = secrets.token_urlsafe(48)
        cur.execute(
            """INSERT INTO inna_auth_sessions(session_hash,user_id,expires_at)
            VALUES (%s,%s,NOW()+INTERVAL '12 hours')""",
            (hash_session_token(token), user_id),
        )
        return {"session_token": token}


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")
    password: SecretStr = Field(min_length=10, max_length=128)
    code: str = Field(default="", max_length=64)


def protect(request):
    if (
        request.headers.get("origin") != recovery.public_origin()
        or request.headers.get("X-Sabino-MFA") != "1"
    ):
        raise HTTPException(403, "Origem inválida.")


def current_user(request):
    from .finance_auth_routes import get_authenticated_user

    return get_authenticated_user(request)


def prepare(request, response, mutation=False):
    response.headers["Cache-Control"] = "no-store"
    if mutation:
        protect(request)
    user = current_user(request)
    ensure_schema()
    if mutation:
        throttle("settings:" + recovery.digest(user["user_id"]), 20)
    return user


@router.get("/auth/mfa/status")
def status(request: Request, response: Response):
    user = prepare(request, response)
    with cursor_postgres(dict_cursor=True) as cur:
        cur.execute(
            "SELECT enabled,recovery_hashes FROM inna_auth_mfa WHERE user_id=%s",
            (user["user_id"],),
        )
        row = cur.fetchone()
    return {
        "available": available(),
        "enabled": bool(row and row["enabled"]),
        "recovery_codes_remaining": len(row["recovery_hashes"])
        if row and row["enabled"]
        else 0,
    }


@router.post("/auth/mfa/setup")
def setup(body: Credentials, request: Request, response: Response):
    user = prepare(request, response, True)
    user_id = user["user_id"]
    secret = base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")
    encrypted = seal(user_id, secret)
    with cursor_postgres(dict_cursor=True) as cur:
        lock_user(cur, user_id, body.password.get_secret_value())
        cur.execute("SELECT enabled FROM inna_auth_mfa WHERE user_id=%s", (user_id,))
        row = cur.fetchone()
        if row and row["enabled"]:
            raise HTTPException(409, "O autenticador já está ativado.")
        cur.execute(
            """INSERT INTO inna_auth_mfa(user_id,secret,expires_at)
            VALUES (%s,%s,NOW()+INTERVAL '10 minutes') ON CONFLICT(user_id) DO UPDATE
            SET secret=EXCLUDED.secret,expires_at=EXCLUDED.expires_at,last_step=-1""",
            (user_id, encrypted),
        )
    uri = (
        "otpauth://totp/"
        + quote("Sabino.AI:" + user["email"], safe="")
        + "?"
        + urlencode(
            {
                "secret": secret,
                "issuer": "Sabino.AI",
                "algorithm": "SHA1",
                "digits": 6,
                "period": 30,
            }
        )
    )
    return {
        "secret": secret,
        "uri": uri,
        "qr_data_uri": qr_data_uri(uri),
        "expires_in": 600,
    }


@router.post("/auth/mfa/confirm")
def confirm(body: Credentials, request: Request, response: Response):
    user = prepare(request, response, True)
    user_id = user["user_id"]
    with cursor_postgres(dict_cursor=True) as cur:
        lock_user(cur, user_id, body.password.get_secret_value())
        cur.execute(
            "SELECT *,expires_at>NOW() AS valid FROM inna_auth_mfa WHERE user_id=%s",
            (user_id,),
        )
        row = cur.fetchone()
        if not row or row["enabled"] or not row["valid"]:
            raise HTTPException(
                400, "Configuração inválida ou expirada. Comece novamente."
            )
        step = matching_step(unseal(user_id, row["secret"]), body.code.strip())
        if step is None:
            raise HTTPException(400, "Código inválido ou expirado.")
        codes = [
            "-".join([secrets.token_hex(4).upper() for _ in range(3)]) for _ in range(8)
        ]
        hashes = [recovery_hash(user_id, code) for code in codes]
        cur.execute(
            """UPDATE inna_auth_mfa SET enabled=TRUE,expires_at=NULL,last_step=%s,
            recovery_hashes=%s::jsonb WHERE user_id=%s""",
            (step, json.dumps(hashes), user_id),
        )
        cur.execute(
            "UPDATE inna_auth_sessions SET revoked_at=NOW() WHERE user_id=%s AND revoked_at IS NULL",
            (user_id,),
        )
    return {
        "enabled": True,
        "recovery_codes": codes,
        "message": "Autenticador ativado. Guarde os códigos de recuperação e entre novamente.",
    }


@router.post("/auth/mfa/disable")
def disable(body: Credentials, request: Request, response: Response):
    user = prepare(request, response, True)
    user_id = user["user_id"]
    with cursor_postgres(dict_cursor=True) as cur:
        lock_user(cur, user_id, body.password.get_secret_value())
        cur.execute("SELECT * FROM inna_auth_mfa WHERE user_id=%s", (user_id,))
        row = cur.fetchone()
        if (
            not row
            or not row["enabled"]
            or not consume(cur, user_id, row, body.code.strip())
        ):
            raise HTTPException(401, "Senha e um código válido são necessários.")
        cur.execute("DELETE FROM inna_auth_mfa WHERE user_id=%s", (user_id,))
        cur.execute(
            "UPDATE inna_auth_sessions SET revoked_at=NOW() WHERE user_id=%s AND revoked_at IS NULL",
            (user_id,),
        )
    return {
        "enabled": False,
        "message": "Autenticador desativado. Entre novamente para configurar outro aparelho.",
    }


@router.get("/seguranca-conta", include_in_schema=False)
def security_page():
    return FileResponse(
        Path(__file__).resolve().parents[2] / "static" / "sabino-mfa.html",
        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
    )
