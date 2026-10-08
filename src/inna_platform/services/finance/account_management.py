"""Self-service registration and profile; financial access remains plan-controlled."""

import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from . import password_recovery as recovery
from .finance_identity import cursor_postgres, hash_password, normalize_email

router = APIRouter()
STATIC = Path(__file__).resolve().parents[2] / "static"


class RegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=3, max_length=254)
    password: SecretStr


class ProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=100)


def clean_name(value):
    name = " ".join(value.split())
    if len(name) < 2 or any(ord(c) < 32 for c in name):
        raise HTTPException(400, "Informe um nome com pelo menos 2 caracteres.")
    return name


def protect(request):
    if (
        request.headers.get("origin") != recovery.public_origin()
        or request.headers.get("X-Sabino-Account") != "1"
    ):
        raise HTTPException(403, "Origem inválida.")


def ensure_schema():
    recovery.ensure_schema()
    with cursor_postgres(commit_automatico=True) as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS inna_account_profiles (
            user_id TEXT PRIMARY KEY REFERENCES inna_auth_users(user_id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")


def insert_account(name, email, password):
    salt, hashed = hash_password(password)
    user_id = uuid4().hex
    # Account and profile commit together; a duplicate must never alter credentials.
    with cursor_postgres(dict_cursor=True, commit_automatico=True) as cur:
        cur.execute(
            """INSERT INTO inna_auth_users
            (user_id,email,password_salt,password_hash,active)
            VALUES (%s,%s,%s,%s,TRUE) ON CONFLICT(email) DO NOTHING RETURNING user_id""",
            (user_id, email, salt, hashed),
        )
        if not cur.fetchone():
            return False
        cur.execute(
            "INSERT INTO inna_account_profiles(user_id,name) VALUES (%s,%s)",
            (user_id, name),
        )
    return True


def current_user(request):
    # Lazy import avoids a cycle with the central authentication router.
    from .finance_auth_routes import get_authenticated_user

    return get_authenticated_user(request)


@router.post("/auth/register", status_code=201)
def register(body: RegistrationRequest, request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    try:
        protect(request)
        name = clean_name(body.name)
        email = normalize_email(body.email)
        password = body.password.get_secret_value()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise HTTPException(400, "Informe um e-mail válido.")
        if not 10 <= len(password) <= 128:
            raise HTTPException(400, "Use uma senha de 10 a 128 caracteres.")
        ensure_schema()
        if not recovery.allow("signup:global", 100) or not recovery.allow(
            "signup:email:" + recovery.digest(email), 5
        ):
            raise HTTPException(429, "Muitas tentativas. Tente novamente mais tarde.")
        if not insert_account(name, email, password):
            raise HTTPException(
                409,
                "Não foi possível criar a conta com esse e-mail. Tente entrar ou recuperar sua senha.",
            )
        # No automatic session, credits or paid subscription are granted here.
        return {"message": "Conta criada. Entre com seu e-mail e senha."}
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(400, "Confira os dados informados.") from None
    except Exception:
        raise HTTPException(
            503, "Cadastro temporariamente indisponível. Tente novamente mais tarde."
        ) from None


@router.get("/auth/profile")
def profile(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    try:
        user = current_user(request)
        ensure_schema()
        with cursor_postgres(dict_cursor=True) as cur:
            cur.execute(
                "SELECT name FROM inna_account_profiles WHERE user_id=%s",
                (user["user_id"],),
            )
            row = cur.fetchone()
        return {"user": {"email": user["email"], "name": row["name"] if row else ""}}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            503, "Não foi possível carregar sua conta. Tente novamente."
        ) from None


@router.patch("/auth/profile")
def update_profile(body: ProfileRequest, request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    try:
        protect(request)
        user = current_user(request)
        name = clean_name(body.name)
        ensure_schema()
        with cursor_postgres(commit_automatico=True) as cur:
            cur.execute(
                """INSERT INTO inna_account_profiles(user_id,name) VALUES (%s,%s)
                ON CONFLICT(user_id) DO UPDATE SET name=EXCLUDED.name, updated_at=NOW()""",
                (user["user_id"], name),
            )
        return {
            "user": {"name": name, "email": user["email"]},
            "message": "Nome atualizado.",
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            503, "Não foi possível salvar sua conta. Tente novamente."
        ) from None


@router.get("/cadastro", include_in_schema=False)
@router.get("/minha-conta", include_in_schema=False)
def account_page():
    return FileResponse(
        STATIC / "sabino-conta.html",
        headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "same-origin",
        },
    )
