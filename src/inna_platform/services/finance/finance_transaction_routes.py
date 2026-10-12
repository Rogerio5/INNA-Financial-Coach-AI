from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from src.inna_platform.services.finance.finance_access_gate import (
    get_financeiro_entitled_user,
)

from src.inna_platform.services.finance.transaction_repository import (
    update_financial_transaction,
    create_financial_transaction,
    delete_financial_transaction,
    get_financial_transaction,
    list_financial_transactions,
    transaction_repository_capabilities,
)


router = APIRouter(
    prefix="/api/platform/finance/transactions",
    tags=["Finance Transactions"],
)


class TransactionCreateRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    amount: Decimal = Field(
        gt=0,
    )

    description: str = Field(
        min_length=1,
        max_length=500,
    )

    category: str = Field(
        min_length=1,
        max_length=120,
    )

    transaction_type: Literal[
        "Despesa"
    ] = "Despesa"

    currency: str = Field(
        default="BRL",
        min_length=3,
        max_length=3,
    )

    transaction_date: date | None = None

    merchant: str = Field(
        default="",
        max_length=200,
    )

    subcategory: str = Field(
        default="",
        max_length=120,
    )

    classification_strategy: str = Field(
        default="manual",
        max_length=120,
    )

    classification_confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    semantic_similarity: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    semantic_margin: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )


def _owner_id_from_user(
    user: dict,
) -> str:

    owner_id = str(
        user.get(
            "user_id",
            "",
        )
    ).strip()

    if not owner_id:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identidade autenticada inválida",
        )

    return owner_id


@router.get(
    "/auth-capabilities",
)
def authenticated_transaction_capabilities(
    user: dict = Depends(
        get_financeiro_entitled_user
    ),
):

    _owner_id_from_user(
        user
    )

    repository = (
        transaction_repository_capabilities()
    )

    return {
        "ok": True,
        "version": "tc4-c",
        "authenticated": True,
        "owner_identity_source": "server_session",
        "browser_owner_id_allowed": False,
        "browser_transaction_id_allowed": False,
        "browser_source_allowed": False,
        "browser_confirmation_flag_allowed": False,
        "create": True,
        "list": True,
        "get": True,
        "delete": True,
        "update": True,
        "expense_transactions": True,
        "income_transactions": False,
        "source_for_created_transactions": "financeiro_ui",
        "classification_confirmed_on_create": True,
        "repository": repository,
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_authenticated_transaction(
    payload: TransactionCreateRequest,
    user: dict = Depends(
        get_financeiro_entitled_user
    ),
):

    owner_id = _owner_id_from_user(
        user
    )

    try:

        transaction = (
            create_financial_transaction(
                owner_id=owner_id,
                amount=payload.amount,
                description=payload.description,
                category=payload.category,
                transaction_type=(
                    payload.transaction_type
                ),
                currency=payload.currency,
                transaction_date=(
                    payload.transaction_date
                ),
                merchant=payload.merchant,
                subcategory=payload.subcategory,
                classification_strategy=(
                    payload.classification_strategy
                ),
                classification_confidence=(
                    payload.classification_confidence
                ),
                semantic_similarity=(
                    payload.semantic_similarity
                ),
                semantic_margin=(
                    payload.semantic_margin
                ),
                classification_confirmed=True,
                source="financeiro_ui",
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return {
        "ok": True,
        "transaction": transaction,
    }


@router.get(
    "",
)
def list_authenticated_transactions(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    user: dict = Depends(
        get_financeiro_entitled_user
    ),
):

    owner_id = _owner_id_from_user(
        user
    )

    transactions = (
        list_financial_transactions(
            owner_id=owner_id,
            limit=limit,
        )
    )

    return {
        "ok": True,
        "count": len(
            transactions
        ),
        "transactions": transactions,
    }


@router.get(
    "/{transaction_id}",
)
def get_authenticated_transaction(
    transaction_id: str = Path(
        min_length=1,
        max_length=128,
    ),
    user: dict = Depends(
        get_financeiro_entitled_user
    ),
):

    owner_id = _owner_id_from_user(
        user
    )

    transaction = (
        get_financial_transaction(
            owner_id=owner_id,
            transaction_id=transaction_id,
        )
    )

    if transaction is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada",
        )

    return {
        "ok": True,
        "transaction": transaction,
    }


@router.delete(
    "/{transaction_id}",
)
def delete_authenticated_transaction(
    transaction_id: str = Path(
        min_length=1,
        max_length=128,
    ),
    user: dict = Depends(
        get_financeiro_entitled_user
    ),
):

    owner_id = _owner_id_from_user(
        user
    )

    deleted = (
        delete_financial_transaction(
            owner_id=owner_id,
            transaction_id=transaction_id,
        )
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transação não encontrada",
        )

    return {
        "ok": True,
        "deleted": True,
        "transaction_id": transaction_id,
    }

class TransactionEditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: Decimal = Field(gt=0, lt=1000000000000, decimal_places=2)
    description: str = Field(min_length=1, max_length=500)
    category: str = Field(min_length=1, max_length=120)
    transaction_date: date


@router.put("/{transaction_id}")
def update_authenticated_transaction(
    payload: TransactionEditRequest,
    transaction_id: str = Path(min_length=1, max_length=128),
    user: dict = Depends(get_financeiro_entitled_user),
):
    owner_id = _owner_id_from_user(user)
    try:
        transaction = update_financial_transaction(
            owner_id=owner_id, transaction_id=transaction_id, **payload.model_dump()
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if transaction is None:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return {"ok": True, "transaction": transaction}
