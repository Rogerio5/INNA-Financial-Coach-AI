from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from api.security.human_review_admin import (
    require_human_review_admin_context,
)


def _context(
    user_id: str = "admin-local",
):
    return SimpleNamespace(
        user_id=user_id,
        request_id="request-admin-123456",
    )


def test_admin_context_accepts_authorized_user(
) -> None:
    context = _context()

    with patch(
        "api.security.human_review_admin."
        "_configured_admin_user_ids",
        return_value=frozenset({
            "admin-local",
        }),
    ):
        result = (
            require_human_review_admin_context(
                context
            )
        )

    assert result is context


def test_admin_context_rejects_unauthorized_user(
) -> None:
    context = _context(
        user_id="regular-user"
    )

    with patch(
        "api.security.human_review_admin."
        "_configured_admin_user_ids",
        return_value=frozenset({
            "admin-local",
        }),
    ):
        with pytest.raises(
            HTTPException
        ) as exc_info:
            require_human_review_admin_context(
                context
            )

    assert exc_info.value.status_code == 403


def test_admin_context_rejects_missing_configuration(
) -> None:
    context = _context()

    with patch(
        "api.security.human_review_admin."
        "_configured_admin_user_ids",
        return_value=frozenset(),
    ):
        with pytest.raises(
            HTTPException
        ) as exc_info:
            require_human_review_admin_context(
                context
            )

    assert exc_info.value.status_code == 503


def test_configured_admin_ids_are_normalized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "INNA_HITL_ADMIN_USER_IDS",
        " admin-1,admin-2, admin-1 ,,",
    )

    from api.security.human_review_admin import (
        _configured_admin_user_ids,
    )

    assert _configured_admin_user_ids() == (
        frozenset({
            "admin-1",
            "admin-2",
        })
    )
