from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrganizationRole(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    FINANCE_APPROVER = "finance_approver"
    ORGANIZATION_ADMIN = "organization_admin"


@dataclass(frozen=True)
class OrganizationMember:
    organization_id: str
    user_id: str
    role: OrganizationRole
    active: bool
    created_at: datetime
    updated_at: datetime