from __future__ import annotations

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from src.inna_platform.services.finance.finance_auth_routes import (
    get_authenticated_user,
)

from src.inna_platform.services.finance.platform_entitlements import (
    has_active_platform_entitlement,
)


FINANCEIRO_PLATFORM_CODE = "financeiro"


def get_financeiro_entitled_user(
    user: dict = Depends(
        get_authenticated_user
    ),
) -> dict:

    user_id = str(
        user.get(
            "user_id",
            "",
        )
    ).strip()

    if not user_id:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identidade autenticada inválida",
        )

    allowed = (
        has_active_platform_entitlement(
            user_id=user_id,
            platform_code=FINANCEIRO_PLATFORM_CODE,
        )
    )

    if not allowed:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Financeiro não contratado ou inativo",
        )

    return user


def finance_access_capabilities() -> dict:

    return {
        "version": "tc4-d2b",
        "platform_code": "financeiro",
        "real_page_requires_login": True,
        "real_page_requires_entitlement": True,
        "demo_requires_login": False,
        "demo_requires_entitlement": False,
        "transaction_api_requires_login": True,
        "transaction_api_requires_entitlement": True,
        "browser_can_grant_entitlement": False,
        "checkout_activation_connected": False,
    }