from __future__ import annotations

from .agent.agent import ReimbursementAgent
from .agent.analyzer import (
    enrich_analysis_with_receipt_validation,
)
from .audit.audit_service import (
    ReimbursementAuditService,
)
from .models import (
    ReimbursementRequest,
    ReimbursementStatus,
    utc_now,
)
from .repository import (
    PostgresReimbursementRepository,
    ReimbursementRepository,
)
from .schemas import ReimbursementCreate
from .receipts.repository import (
    PostgresReceiptRepository,
    ReceiptRepository,
)

from .receipts.storage import (
    LocalReceiptStorage,
)

from .receipts.integrity import (
    bind_receipt_integrity_to_validation_metadata,
    verify_persisted_receipt_integrity,
)

from .workflow import (
    ReimbursementTransitionError,
    assert_transition,
)

from .workflow_persistence import (
    persist_workflow_transition,
)


from .receipts.verification import (
    verify_receipt_document,
)


from .decision_governance import (
    evaluate_auto_approval_eligibility,
)


from .auto_approval.gate import (
    evaluate_controlled_auto_approval_gate,
)

from .auto_approval.execution_control import (
    is_global_auto_approval_execution_enabled,
)

from .auto_approval.repository import (
    AutoApprovalConfigurationRepository,
)


from .analysis_persistence import (
    persist_analysis_outcome,
)


AUTO_APPROVAL_SYSTEM_ACTOR = (
    "system:auto-approval"
)


class ReimbursementService:

    def __init__(
        self,
        *,
        repository: ReimbursementRepository,
        audit: ReimbursementAuditService,
        agent: ReimbursementAgent,
        receipt_repository: ReceiptRepository | None = None,
        receipt_storage: LocalReceiptStorage | None = None,
        auto_approval_repository: AutoApprovalConfigurationRepository | None = None,
    ) -> None:

        self.repository = repository
        self.audit = audit
        self.agent = agent

        if (
            receipt_repository is None
            and
            isinstance(
                repository,
                PostgresReimbursementRepository,
            )
        ):
            receipt_repository = (
                PostgresReceiptRepository()
            )

        if (
            receipt_storage is None
            and
            isinstance(
                repository,
                PostgresReimbursementRepository,
            )
        ):
            receipt_storage = (
                LocalReceiptStorage()
            )

        self.receipt_repository = (
            receipt_repository
        )

        self.receipt_storage = (
            receipt_storage
        )

        self.auto_approval_repository = (
            auto_approval_repository
        )


    def create(
        self,
        payload: ReimbursementCreate,
    ) -> ReimbursementRequest:

        reimbursement = ReimbursementRequest(
            tenant_id=payload.tenant_id,
            user_id=payload.user_id,
            amount=payload.amount,
            currency=payload.currency.upper(),
            category=payload.category,
            description=payload.description,
            merchant=payload.merchant,
            expense_date=payload.expense_date,
            receipt_reference=payload.receipt_reference,
            source_type=payload.source_type,
            source_reference=payload.source_reference,
        )

        self.repository.save(
            reimbursement
        )

        self.audit.record(
            tenant_id=reimbursement.tenant_id,
            reimbursement_id=reimbursement.id,
            action="reimbursement.created",
            actor_id=reimbursement.user_id,
        )

        return reimbursement


    def submit(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
        actor_id: str,
        idempotency_key: str | None = None,
    ) -> ReimbursementRequest:

        #
        # Legacy calls without an idempotency key retain
        # the original early validation contract.
        #
        if idempotency_key is None:

            reimbursement = self._require(
                tenant_id=tenant_id,
                reimbursement_id=reimbursement_id,
            )

            if (
                reimbursement.status
                !=
                ReimbursementStatus.DRAFT
            ):
                raise ValueError(
                    "REIMBURSEMENT_NOT_DRAFT"
                )

        try:

            return persist_workflow_transition(
                repository=
                    self.repository,

                audit=
                    self.audit,

                tenant_id=
                    tenant_id,

                reimbursement_id=
                    reimbursement_id,

                actor_id=
                    actor_id,

                target_status=
                    ReimbursementStatus.SUBMITTED,

                details=None,

                idempotency_key=
                    idempotency_key,

                idempotency_operation=
                    "submit",

                idempotency_payload=
                    {},
            )

        except ReimbursementTransitionError as exc:

            raise ValueError(
                "REIMBURSEMENT_NOT_DRAFT"
            ) from exc

    def analyze(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
        actor_id: str,
    ):

        reimbursement = self._require(
            tenant_id=tenant_id,
            reimbursement_id=reimbursement_id,
        )

        assert_transition(
            current_status=
                reimbursement.status,

            target_status=
                ReimbursementStatus.ANALYZING,
        )

        reimbursement.status = (
            ReimbursementStatus.ANALYZING
        )

        persisted_receipt_present = False

        persisted_receipts = []

        if self.receipt_repository is not None:

            persisted_receipts = (
                self.receipt_repository
                .list_for_reimbursement(
                    tenant_id=tenant_id,
                    reimbursement_id=
                        reimbursement.id,
                )
            )

            persisted_receipt_present = bool(
                persisted_receipts
            )

        receipt_integrity = None

        if self.receipt_storage is not None:

            receipt_integrity = (
                verify_persisted_receipt_integrity(
                    tenant_id=
                        tenant_id,

                    reimbursement_id=
                        reimbursement.id,

                    receipts=
                        persisted_receipts,

                    storage=
                        self.receipt_storage,
                )
            )

            reimbursement.metadata[
                "receipt_integrity"
            ] = (
                receipt_integrity.as_dict()
            )

        receipt_validation_metadata = (
            reimbursement.metadata.get(
                "receipt_validation"
            )
            if isinstance(
                reimbursement.metadata,
                dict,
            )
            else None
        )

        receipt_validation_metadata = (
            bind_receipt_integrity_to_validation_metadata(
                validation_metadata=
                    receipt_validation_metadata,

                integrity_result=
                    receipt_integrity,
            )
        )

        document_verification = (
            verify_receipt_document(
                persisted_receipt_present=
                    persisted_receipt_present,

                validation_metadata=
                    receipt_validation_metadata,
            )
        )

        reimbursement.metadata[
            "document_verification"
        ] = (
            document_verification.as_dict()
        )

        analysis = self.agent.analyze(
            reimbursement,
            persisted_receipt_present=
                persisted_receipt_present,
        )

        analysis = (
            enrich_analysis_with_receipt_validation(
                analysis=analysis,

                reimbursement_metadata=
                    reimbursement.metadata,
            )
        )

        decision_governance = (
            evaluate_auto_approval_eligibility(
                persisted_receipt_present=
                    persisted_receipt_present,

                document_verification=
                    reimbursement.metadata.get(
                        "document_verification"
                    ),

                policy_id=
                    analysis.policy_id,

                policy_version=
                    analysis.policy_version,

                policy_findings=
                    analysis.policy_findings,

                risk_flags=
                    analysis.risk_flags,

                missing_fields=
                    analysis.missing_fields,
            )
        )

        analysis = analysis.model_copy(
            update={
                "eligible_for_auto_approval":
                    decision_governance
                    .eligible_for_auto_approval,

                "automatic_approval":
                    False,

                "requires_human_review":
                    True,
            }
        )

        reimbursement.metadata[
            "decision_governance"
        ] = (
            decision_governance.as_dict()
        )

        auto_approval_config = None

        if (
            self.auto_approval_repository
            is not None
        ):

            auto_approval_config = (
                self.auto_approval_repository.get(
                    organization_id=
                        tenant_id
                )
            )


        auto_approval_gate = (
            evaluate_controlled_auto_approval_gate(
                organization_id=
                    tenant_id,

                amount_minor=
                    reimbursement.amount,

                claimant_user_id=
                    reimbursement.user_id,

                approval_actor_user_id=
                    AUTO_APPROVAL_SYSTEM_ACTOR,

                eligible_for_auto_approval=
                    analysis
                    .eligible_for_auto_approval,

                config=
                    auto_approval_config,

                global_execution_enabled=
                    is_global_auto_approval_execution_enabled(),
            )
        )


        analysis = analysis.model_copy(
            update={
                "auto_approval_permitted":
                    auto_approval_gate
                    .auto_approval_permitted,

                "automatic_approval":
                    False,

                "requires_human_review":
                    True,
            }
        )


        reimbursement.metadata[
            "auto_approval_gate"
        ] = (
            auto_approval_gate.as_dict()
        )


        if analysis.missing_fields:

            reimbursement.status = (
                ReimbursementStatus.NEEDS_INFORMATION
            )

        else:

            reimbursement.status = (
                ReimbursementStatus.AWAITING_HUMAN_REVIEW
            )

        reimbursement.requires_human_review = True

        reimbursement.metadata[
            "analysis"
        ] = analysis.model_dump(mode="json")

        reimbursement.touch()

        persist_analysis_outcome(
            repository=
                self.repository,

            audit=
                self.audit,

            reimbursement=
                reimbursement,

            gate_actor_id=
                AUTO_APPROVAL_SYSTEM_ACTOR,

            gate_details={
                "receipt_integrity_verified":
                    (
                        receipt_integrity
                        .integrity_verified
                        if
                        receipt_integrity
                        is not None
                        else None
                    ),

                "eligible_for_auto_approval":
                    analysis
                    .eligible_for_auto_approval,

                "auto_approval_permitted":
                    auto_approval_gate
                    .auto_approval_permitted,

                "organization_auto_approval_enabled":
                    auto_approval_gate
                    .organization_auto_approval_enabled,

                "organization_config_version":
                    auto_approval_gate
                    .organization_config_version,

                "organization_amount_limit_minor":
                    auto_approval_gate
                    .organization_amount_limit_minor,

                "organization_config_enabled":
                    auto_approval_gate
                    .organization_config_enabled,

                "global_execution_enabled":
                    auto_approval_gate
                    .global_execution_enabled,

                "amount_within_limit":
                    auto_approval_gate
                    .amount_within_limit,

                "blocking_reasons":
                    list(
                        auto_approval_gate
                        .blocking_reasons
                    ),

                "gate_version":
                    auto_approval_gate.version,

                "evaluated_at":
                    auto_approval_gate
                    .evaluated_at
                    .isoformat(),

                "automatic_approval":
                    False,

                "automatic_payment":
                    False,

                "requires_human_review":
                    True,
            },

            analysis_actor_id=
                actor_id,

            analysis_details={
                "recommendation":
                    analysis.recommendation.value,

                "policy_id":
                    analysis.policy_id,

                "policy_version":
                    analysis.policy_version,

                "requires_human_review":
                    analysis.requires_human_review,
            },
        )


        return analysis

    def _require(
        self,
        *,
        tenant_id: str,
        reimbursement_id: str,
    ) -> ReimbursementRequest:

        reimbursement = self.repository.get(
            tenant_id=tenant_id,
            reimbursement_id=reimbursement_id,
        )

        if reimbursement is None:
            raise LookupError(
                "REIMBURSEMENT_NOT_FOUND"
            )

        return reimbursement