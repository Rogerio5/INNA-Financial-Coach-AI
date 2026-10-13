"""Invite-only introductory offer. Disabled until recipients are configured."""
import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, StrictBool

from src.database.connection import cursor_postgres
from . import credit_wallet, platform_entitlements
from .finance_auth_routes import get_authenticated_user

PLAN = "piloto_30_dias"
CREDITS = 15
DAYS = 30
router = APIRouter(tags=["finance-pilot"])


def enabled():
    return os.getenv("SABINO_FINANCE_PILOT_ENABLED", "false").lower() == "true"


def invited(user_id):
    # Server-only allowlist: no grant links, editable identity or public self-enrollment.
    return user_id in {value.strip() for value in os.getenv("SABINO_FINANCE_PILOT_USERS", "").split(",") if value.strip()}


def ensure_schema():
    with cursor_postgres(commit_automatico=True) as cur:
        cur.execute("SELECT pg_advisory_xact_lock(173025102)")
        cur.execute("""CREATE TABLE IF NOT EXISTS inna_finance_pilot_enrollments (
            user_id TEXT PRIMARY KEY REFERENCES inna_auth_users(user_id),
            started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW()+INTERVAL '30 days',
            credits INTEGER NOT NULL DEFAULT 15 CHECK(credits=15)
        )""")


def identity(user):
    value = str(user.get("user_id") or "").strip()
    if not value:
        raise HTTPException(401, "Entre na sua conta para consultar o convite.")
    return value


def offer_status(user_id):
    base = {"days": DAYS, "credits": CREDITS, "auto_renew": False}
    if not enabled():
        return {**base, "state": "unavailable", "eligible": False}
    ensure_schema()
    with cursor_postgres(dict_cursor=True) as cur:
        cur.execute("SELECT *, expires_at > NOW() AS active FROM inna_finance_pilot_enrollments WHERE user_id=%s", (user_id,))
        enrollment = cur.fetchone()
        cur.execute("SELECT plan_code FROM inna_user_platform_entitlements WHERE user_id=%s AND platform_code='financeiro'", (user_id,))
        current = cur.fetchone()
    if enrollment:
        state = "converted" if current and current["plan_code"] != PLAN else "active" if enrollment["active"] else "expired"
        return {**base, "state": state, "eligible": False,
                "started_at": enrollment["started_at"], "expires_at": enrollment["expires_at"]}
    return {**base, "state": "existing_plan" if current else "unavailable" if not credit_wallet.enabled() else "invited" if invited(user_id) else "not_invited",
            "eligible": not current and invited(user_id) and credit_wallet.enabled()}


def activate(user_id):
    if not enabled() or not credit_wallet.enabled():
        raise HTTPException(503, "Novas ativações do piloto não estão disponíveis.")
    if not invited(user_id):
        raise HTTPException(403, "Este piloto está disponível apenas para contas convidadas.")
    ensure_schema()
    platform_entitlements.ensure_entitlement_schema()
    with cursor_postgres(dict_cursor=True, commit_automatico=True) as cur:
        # Same lock order as Pix: account, entitlement, wallet.
        cur.execute("SELECT user_id FROM inna_auth_users WHERE user_id=%s AND active=TRUE FOR UPDATE", (user_id,))
        if not cur.fetchone():
            raise HTTPException(403, "Conta indisponível para ativação.")
        cur.execute("SELECT * FROM inna_finance_pilot_enrollments WHERE user_id=%s", (user_id,))
        previous = cur.fetchone()
        if previous:
            return {"replayed": True, "expires_at": previous["expires_at"], "credits": CREDITS}
        cur.execute("SELECT plan_code FROM inna_user_platform_entitlements WHERE user_id=%s AND platform_code='financeiro' FOR UPDATE", (user_id,))
        if cur.fetchone():
            raise HTTPException(409, "Seu plano existente será preservado. Este piloto é destinado a novas contas do Financeiro.")
        cur.execute("INSERT INTO inna_finance_pilot_enrollments(user_id) VALUES (%s) RETURNING expires_at", (user_id,))
        expiry = cur.fetchone()["expires_at"]
        cur.execute("""INSERT INTO inna_user_platform_entitlements
            (entitlement_id,user_id,platform_code,plan_code,status,activated_at,expires_at)
            VALUES (%s,%s,'financeiro',%s,'active',NOW(),%s)""", (uuid4().hex, user_id, PLAN, expiry))
        cur.execute("INSERT INTO inna_credit_wallets(user_id) VALUES (%s) ON CONFLICT DO NOTHING", (user_id,))
        cur.execute("SELECT balance FROM inna_credit_wallets WHERE user_id=%s FOR UPDATE", (user_id,))
        operation = "finance-pilot:v1:" + user_id
        cur.execute("""INSERT INTO inna_credit_operations(user_id,operation_id,amount,kind,source,state)
            VALUES (%s,%s,15,'grant','included','completed')""", (user_id, operation))
        cur.execute("UPDATE inna_credit_wallets SET balance=balance+15,updated_at=NOW() WHERE user_id=%s", (user_id,))
        cur.execute("INSERT INTO inna_credit_ledger(user_id,operation_id,event,delta) VALUES (%s,%s,'grant',15)", (user_id, operation))
        return {"replayed": False, "expires_at": expiry, "credits": CREDITS}


class Acceptance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activate: StrictBool


@router.get("/piloto-financeiro", include_in_schema=False)
def page(user: dict = Depends(get_authenticated_user)):
    return FileResponse(Path(__file__).resolve().parents[2]/"static"/"sabino-piloto-financeiro.html", headers={"Cache-Control":"no-store"})


@router.get("/api/platform/finance/pilot")
def status(response: Response, user: dict = Depends(get_authenticated_user)):
    response.headers["Cache-Control"] = "no-store"
    try:
        return offer_status(identity(user))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, "Não foi possível consultar o convite agora.") from None


@router.post("/api/platform/finance/pilot/activate")
def redeem(body: Acceptance, request: Request, response: Response, user: dict = Depends(get_authenticated_user)):
    response.headers["Cache-Control"] = "no-store"
    origin = request.headers.get("origin")
    if (request.headers.get("X-Sabino-Pilot") != "activate"
            or request.headers.get("sec-fetch-site") == "cross-site"
            or (origin and origin != str(request.base_url).rstrip("/"))):
        raise HTTPException(403, "Origem inválida.")
    if not body.activate:
        raise HTTPException(422, "Confirme a ativação gratuita para continuar.")
    try:
        return activate(identity(user))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, "Não foi possível confirmar a ativação. Atualize o convite antes de tentar novamente.") from None
