from __future__ import annotations

from .models import (
    OrganizationMember,
    OrganizationRole,
)


REIMBURSEMENT_REVIEW_ROLES = {
    OrganizationRole.FINANCE_APPROVER,
    OrganizationRole.ORGANIZATION_ADMIN,
}


MEMBER_MANAGEMENT_ROLES = {
    OrganizationRole.ORGANIZATION_ADMIN,
}


REIMBURSEMENT_PAYMENT_ROLES = {
    OrganizationRole.FINANCE_APPROVER,
    OrganizationRole.ORGANIZATION_ADMIN,
}


def can_review_reimbursements(
    member: OrganizationMember | None,
) -> bool:

    if member is None:
        return False

    if not member.active:
        return False

    return (
        member.role
        in REIMBURSEMENT_REVIEW_ROLES
    )


def can_manage_members(
    member: OrganizationMember | None,
) -> bool:

    if member is None:
        return False

    if not member.active:
        return False

    return (
        member.role
        in MEMBER_MANAGEMENT_ROLES
    )


def assert_can_review_reimbursements(
    member: OrganizationMember | None,
) -> None:

    if not can_review_reimbursements(
        member
    ):
        raise PermissionError(
            "REIMBURSEMENT_REVIEW_FORBIDDEN"
        )


def can_manage_reimbursement_payments(
    member: OrganizationMember | None,
) -> bool:

    if member is None:
        return False

    if not member.active:
        return False

    return (
        member.role
        in REIMBURSEMENT_PAYMENT_ROLES
    )


def assert_can_manage_reimbursement_payments(
    member: OrganizationMember | None,
) -> None:

    if not can_manage_reimbursement_payments(
        member
    ):

        raise PermissionError(
            "REIMBURSEMENT_PAYMENT_FORBIDDEN"
        )
