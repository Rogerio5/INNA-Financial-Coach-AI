from __future__ import annotations

import os

from collections.abc import Mapping


AUTO_APPROVAL_EXECUTION_ENV = (
    "SABINO_AUTO_APPROVAL_EXECUTION_ENABLED"
)


_TRUE_VALUES = {
    "1",
    "true",
    "yes",
    "on",
    "enabled",
}


def is_global_auto_approval_execution_enabled(
    *,
    environ: Mapping[str, str] | None = None,
) -> bool:
    """
    Global production kill switch.

    Fail-closed:
    - missing -> False
    - empty -> False
    - unknown -> False

    Even when True, 2B10C4 does not execute approval.
    """

    source = (
        os.environ
        if environ is None
        else environ
    )

    raw = source.get(
        AUTO_APPROVAL_EXECUTION_ENV
    )

    if raw is None:
        return False

    value = str(
        raw
    ).strip().lower()

    return value in _TRUE_VALUES


def auto_approval_execution_capabilities(
    *,
    environ: Mapping[str, str] | None = None,
) -> dict:

    global_enabled = (
        is_global_auto_approval_execution_enabled(
            environ=environ,
        )
    )

    return {
        "version":
            "reimbursement-2b10c4",

        "global_execution_enabled":
            global_enabled,

        "default_disabled":
            True,

        "fail_closed":
            True,

        "automatic_approval":
            False,

        "auto_transition_to_approved":
            False,

        "automatic_payment":
            False,

        "human_review_required":
            True,
    }