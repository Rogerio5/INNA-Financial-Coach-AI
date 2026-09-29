from __future__ import annotations

from src.inna_platform.services.finance.platform_entitlements import (
    grant_platform_entitlement,
    has_active_platform_entitlement,
)


VALID_PLANS = {
    "premium",
}


def activate_verified_finance_purchase(
    *,
    user_id: str,
    plan_code: str,
    verification_reference: str,
) -> dict:

    user_id = str(user_id).strip()
    plan_code = str(plan_code).strip().lower()
    verification_reference = str(
        verification_reference
    ).strip()

    if not user_id:
        raise ValueError("user_id obrigatório")

    if plan_code not in VALID_PLANS:
        raise ValueError("plano inválido")

    if not verification_reference:
        raise ValueError(
            "confirmação de pagamento obrigatória"
        )

    entitlement = grant_platform_entitlement(
        user_id=user_id,
        platform_code="financeiro",
        plan_code=plan_code,
        status="active",
    )

    active = has_active_platform_entitlement(
        user_id=user_id,
        platform_code="financeiro",
    )

    return {
        "activated": bool(active),
        "user_id": user_id,
        "platform_code": "financeiro",
        "plan_code": plan_code,
        "verification_reference":
            verification_reference,
        "entitlement": entitlement,
    }


def purchase_activation_capabilities() -> dict:

    return {
        "version": "tc4-d3a",
        "platform": "financeiro",
        "verified_activation": True,
        "browser_can_activate": False,
        "completion_page_can_activate": False,
        "payment_webhook_connected": False,
        "manual_server_confirmation": True,
    }
