from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    Depends,
)

from src.inna_platform.services.finance.finance_auth_routes import (
    get_authenticated_user,
)

from src.inna_platform.services.finance.platform_entitlements import (
    get_platform_entitlement,
    is_entitlement_active,
)


router = APIRouter(
    prefix="/api/platform/finance",
    tags=["finance-access"],
)


def _serialize_datetime(
    value: Any,
):

    if value is None:
        return None

    if hasattr(
        value,
        "isoformat",
    ):
        return value.isoformat()

    return str(
        value
    )


@router.get(
    "/access-status"
)
def finance_access_status(
    user: dict = Depends(
        get_authenticated_user
    ),
):

    user_id = str(
        user.get(
            "user_id",
            "",
        )
    ).strip()

    entitlement = (
        get_platform_entitlement(
            user_id=user_id,
            platform_code="financeiro",
        )
    )

    active = (
        is_entitlement_active(
            entitlement
        )
    )

    return {
        "ok": True,
        "authenticated": True,
        "platform_code": "financeiro",
        "entitled": active,

        "plan_code": (
            entitlement.get(
                "plan_code"
            )
            if entitlement
            else None
        ),

        "status": (
            entitlement.get(
                "status"
            )
            if entitlement
            else None
        ),

        "activated_at": (
            _serialize_datetime(
                entitlement.get(
                    "activated_at"
                )
            )
            if entitlement
            else None
        ),

        "expires_at": (
            _serialize_datetime(
                entitlement.get(
                    "expires_at"
                )
            )
            if entitlement
            else None
        ),

        "routes": {
            "demo":
                "/financeiro?demo=1",

            "plans":
                "/financeiro/planos",

            "real":
                "/financeiro",
        },

        "browser_can_grant_entitlement":
            False,
    }