from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .models import (
    AutoApprovalConfiguration,
    utc_now,
)


@dataclass(frozen=True)
class ControlledAutoApprovalGateResult:

    auto_approval_permitted: bool

    eligible_for_auto_approval: bool

    organization_auto_approval_enabled: bool

    organization_config_version: int | None


    organization_amount_limit_minor: int | None


    organization_config_enabled: bool

    amount_within_limit: bool

    self_approval_blocked: bool

    global_execution_enabled: bool

    evaluated_at: datetime

    automatic_approval: bool

    automatic_payment: bool

    requires_human_review: bool

    blocking_reasons: tuple[str, ...]

    evidence: tuple[str, ...]

    version: str = "2b10c5-v1"


    def as_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "auto_approval_permitted":
                self.auto_approval_permitted,

            "eligible_for_auto_approval":
                self.eligible_for_auto_approval,

            "organization_auto_approval_enabled":
                self.organization_auto_approval_enabled,

            "organization_config_version":
                self.organization_config_version,

            "organization_amount_limit_minor":
                self.organization_amount_limit_minor,

            "organization_config_enabled":
                self.organization_config_enabled,

            "amount_within_limit":
                self.amount_within_limit,

            "self_approval_blocked":
                self.self_approval_blocked,

            "global_execution_enabled":
                self.global_execution_enabled,

            "evaluated_at":
                self.evaluated_at.isoformat(),

            "automatic_approval":
                self.automatic_approval,

            "automatic_payment":
                self.automatic_payment,

            "requires_human_review":
                self.requires_human_review,

            "blocking_reasons":
                list(
                    self.blocking_reasons
                ),

            "evidence":
                list(
                    self.evidence
                ),

            # Explicit evidence key.
            "gate_version":
                self.version,

            # Kept for backwards compatibility.
            "version":
                self.version,
        }


def _append_unique(
    values: list[str],
    value: str,
) -> None:

    if value not in values:

        values.append(
            value
        )


def evaluate_controlled_auto_approval_gate(
    *,
    organization_id: str,

    amount_minor: int,

    claimant_user_id: str,

    approval_actor_user_id: str,

    eligible_for_auto_approval: bool,

    config:
        AutoApprovalConfiguration
        |
        None,

    global_execution_enabled: bool = False,
) -> ControlledAutoApprovalGateResult:
    """
    2B10C5 governance decision evidence gate.

    auto_approval_permitted:
        organization governance signal only.

    global_execution_enabled:
        platform execution-control snapshot only.

    This function does NOT:
    - approve;
    - change reimbursement status;
    - initiate payment.

    Human review remains mandatory.
    """

    evaluated_at = utc_now()

    blocking: list[str] = []
    evidence: list[str] = []


    organization_id = str(
        organization_id or ""
    ).strip()

    claimant_user_id = str(
        claimant_user_id or ""
    ).strip()

    approval_actor_user_id = str(
        approval_actor_user_id or ""
    ).strip()


    if not organization_id:

        _append_unique(
            blocking,
            "ORGANIZATION_REQUIRED",
        )


    if amount_minor < 1:

        _append_unique(
            blocking,
            "AMOUNT_INVALID",
        )


    if not eligible_for_auto_approval:

        _append_unique(
            blocking,
            "NOT_ELIGIBLE_FOR_AUTO_APPROVAL",
        )

    else:

        _append_unique(
            evidence,
            "AUTO_APPROVAL_ELIGIBILITY_CONFIRMED",
        )


    # --------------------------------------------------------
    # Snapshot exact organization configuration used
    # in THIS evaluation.
    # --------------------------------------------------------

    if config is None:

        organization_config_version = None

        organization_amount_limit_minor = None

        organization_config_enabled = False

        org_enabled = False

        amount_within_limit = False


        _append_unique(
            blocking,
            "ORG_AUTO_APPROVAL_NOT_CONFIGURED",
        )

    else:

        organization_config_version = (
            int(
                config.version
            )
        )

        organization_amount_limit_minor = (
            config.amount_limit_minor
        )

        organization_config_enabled = (
            config.enabled is True
        )

        org_enabled = (
            organization_config_enabled
        )


        if (
            config.organization_id
            !=
            organization_id
        ):

            _append_unique(
                blocking,
                "AUTO_APPROVAL_CONFIG_ORG_MISMATCH",
            )


        if not org_enabled:

            _append_unique(
                blocking,
                "ORG_AUTO_APPROVAL_DISABLED",
            )

        else:

            _append_unique(
                evidence,
                "ORG_AUTO_APPROVAL_ENABLED",
            )


        limit = (
            organization_amount_limit_minor
        )


        if limit is None:

            amount_within_limit = False

            _append_unique(
                blocking,
                "AUTO_APPROVAL_LIMIT_REQUIRED",
            )

        else:

            amount_within_limit = (
                amount_minor
                <=
                limit
            )


            if amount_within_limit:

                _append_unique(
                    evidence,
                    "AMOUNT_WITHIN_AUTO_APPROVAL_LIMIT",
                )

            else:

                _append_unique(
                    blocking,
                    "AUTO_APPROVAL_AMOUNT_LIMIT_EXCEEDED",
                )


    # --------------------------------------------------------
    # Segregation of duties
    # --------------------------------------------------------

    self_approval_blocked = (
        bool(
            claimant_user_id
        )
        and
        claimant_user_id
        ==
        approval_actor_user_id
    )


    if self_approval_blocked:

        _append_unique(
            blocking,
            "SELF_APPROVAL_FORBIDDEN",
        )

    else:

        _append_unique(
            evidence,
            "SEGREGATION_OF_DUTIES_OK",
        )


    # --------------------------------------------------------
    # Organization-level permission signal.
    #
    # This is NOT an approval.
    # --------------------------------------------------------

    permitted = (
        eligible_for_auto_approval
        and
        config is not None
        and
        config.organization_id
        ==
        organization_id
        and
        org_enabled
        and
        amount_within_limit
        and
        not self_approval_blocked
        and
        not blocking
    )


    if permitted:

        _append_unique(
            evidence,
            "CONTROLLED_AUTO_APPROVAL_GATE_PASSED",
        )


    # --------------------------------------------------------
    # Platform global execution snapshot.
    #
    # Even when True, execution still does not happen
    # in 2B10C5.
    # --------------------------------------------------------

    global_execution_enabled = bool(
        global_execution_enabled
    )


    if global_execution_enabled:

        _append_unique(
            evidence,
            "GLOBAL_AUTO_APPROVAL_EXECUTION_ENABLED",
        )

    else:

        _append_unique(
            evidence,
            "GLOBAL_AUTO_APPROVAL_EXECUTION_DISABLED",
        )


    return ControlledAutoApprovalGateResult(
        auto_approval_permitted=
            permitted,

        eligible_for_auto_approval=
            eligible_for_auto_approval,

        organization_auto_approval_enabled=
            org_enabled,

        organization_config_version=
            organization_config_version,

        organization_amount_limit_minor=
            organization_amount_limit_minor,

        organization_config_enabled=
            organization_config_enabled,

        amount_within_limit=
            amount_within_limit,

        self_approval_blocked=
            self_approval_blocked,

        global_execution_enabled=
            global_execution_enabled,

        evaluated_at=
            evaluated_at,

        automatic_approval=
            False,

        automatic_payment=
            False,

        requires_human_review=
            True,

        blocking_reasons=
            tuple(
                blocking
            ),

        evidence=
            tuple(
                evidence
            ),
    )
