from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, HTTPException, status

from api.security.internal_request import (
    TrustedRequestContext,
    require_trusted_request_context,
)


def _configured_admin_user_ids() -> frozenset[str]:
    raw_value = os.getenv(
        "INNA_HITL_ADMIN_USER_IDS",
        "",
    )

    return frozenset(
        item.strip()
        for item in raw_value.split(",")
        if item.strip()
    )


def require_human_review_admin_context(
    context: Annotated[
        TrustedRequestContext,
        Depends(require_trusted_request_context),
    ],
) -> TrustedRequestContext:
    allowed_user_ids = (
        _configured_admin_user_ids()
    )

    if not allowed_user_ids:
        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "A autorização administrativa "
                "HITL não está configurada."
            ),
        )

    if context.user_id not in allowed_user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "A identidade autenticada não possui "
                "permissão administrativa HITL."
            ),
        )

    return context


HumanReviewAdminContextDependency = Annotated[
    TrustedRequestContext,
    Depends(require_human_review_admin_context),
]


__all__ = [
    "HumanReviewAdminContextDependency",
    "require_human_review_admin_context",
]
