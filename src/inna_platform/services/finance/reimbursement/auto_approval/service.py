from __future__ import annotations

from .models import (
    AutoApprovalConfiguration,
)

from .persistence import (
    persist_auto_approval_configuration,
)

from .repository import (
    AutoApprovalConfigurationRepository,
)

from ..corporate.audit import (
    CorporateAuditService,
)


class AutoApprovalConfigurationService:

    def __init__(
        self,
        *,
        repository:
            AutoApprovalConfigurationRepository,

        audit:
            CorporateAuditService,
    ) -> None:

        self.repository = repository
        self.audit = audit


    def get(
        self,
        *,
        organization_id: str,
    ) -> AutoApprovalConfiguration | None:

        return self.repository.get(
            organization_id=
                organization_id
        )


    def configure(
        self,
        *,
        organization_id: str,

        actor_user_id: str,

        enabled: bool,

        amount_limit_minor:
            int
            |
            None,

        expected_version:
            int
            |
            None
            =
            None,
    ) -> AutoApprovalConfiguration:

        return (
            persist_auto_approval_configuration(
                repository=
                    self.repository,

                audit=
                    self.audit,

                organization_id=
                    organization_id,

                actor_user_id=
                    actor_user_id,

                enabled=
                    enabled,

                amount_limit_minor=
                    amount_limit_minor,

                expected_version=
                    expected_version,
            )
        )