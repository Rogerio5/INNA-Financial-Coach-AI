from __future__ import annotations

import os

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Response,
    status,
)

from pydantic import BaseModel

from src.inna_platform.services.finance.finance_identity import (
    authenticate_user,
    create_session,
    resolve_session_user,
    revoke_session,
)


router = APIRouter()

AUTH_COOKIE_NAME = os.getenv(
    "INNA_AUTH_COOKIE_NAME",
    "inna_session",
)

AUTH_COOKIE_SECURE = (
    os.getenv(
        "INNA_AUTH_COOKIE_SECURE",
        "false",
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)

AUTH_SESSION_MAX_AGE = 12 * 60 * 60


class LoginRequest(BaseModel):
    email: str
    password: str


def get_authenticated_user(
    request: Request,
) -> dict:

    token = request.cookies.get(
        AUTH_COOKIE_NAME
    )

    if not token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
        )

    user = resolve_session_user(
        token
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada",
        )

    return user


@router.post(
    "/auth/login",
)
def finance_auth_login(
    payload: LoginRequest,
    response: Response,
):

    user = authenticate_user(
        email=payload.email,
        password=payload.password,
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    session = create_session(
        user_id=user["user_id"],
    )

    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=session["session_token"],
        max_age=AUTH_SESSION_MAX_AGE,
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite="lax",
        path="/",
    )

    return {
        "authenticated": True,
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
        },
    }


@router.get(
    "/auth/me",
)
def finance_auth_me(
    request: Request,
):

    user = get_authenticated_user(
        request
    )

    return {
        "authenticated": True,
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
        },
    }


@router.post(
    "/auth/logout",
)
def finance_auth_logout(
    request: Request,
    response: Response,
):

    token = request.cookies.get(
        AUTH_COOKIE_NAME
    )

    if token:

        revoke_session(
            token
        )

    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite="lax",
    )

    return {
        "authenticated": False,
        "logged_out": True,
    }


@router.get(
    "/auth/capabilities",
)
def finance_auth_capabilities():

    return {
        "version": "tc4-b3",
        "login": True,
        "logout": True,
        "me": True,
        "registration": False,
        "session_storage": "postgresql",
        "cookie_name": AUTH_COOKIE_NAME,
        "cookie_http_only": True,
        "cookie_same_site": "lax",
        "cookie_secure": AUTH_COOKIE_SECURE,
        "raw_session_token_stored": False,
        "owner_id_from_browser": False,
        "owner_id_from_server_session": True,
        "finance_routes_protected": False,
        "transaction_write_endpoint": False,
    }
# ============================================================
# SABINO_CENTRAL_LOGOUT_COMPAT_V1
# Compatibilidade para paginas que usam href="/logout"
# ============================================================

@router.get(
    "/logout",
    include_in_schema=False,
)
def sabino_central_logout_redirect(
    request: Request,
):
    from fastapi.responses import RedirectResponse

    token = request.cookies.get(
        AUTH_COOKIE_NAME
    )

    if token:
        revoke_session(token)

    response = RedirectResponse(
        url="/",
        status_code=303,
    )

    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=AUTH_COOKIE_SECURE,
        samesite="lax",
    )

    return response
