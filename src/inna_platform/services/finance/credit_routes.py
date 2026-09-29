"""Read-only authenticated wallet API; demo cannot mutate real credit balances."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.inna_platform.services.finance import credit_wallet
from src.inna_platform.services.finance.finance_auth_routes import (
    get_authenticated_user,
)

router = APIRouter(prefix="/api/platform/credits", tags=["credits"])
logger = logging.getLogger(__name__)


@router.get("/wallet")
def wallet(user: Annotated[dict, Depends(get_authenticated_user)]):
    identity = str(user.get("user_id") or "").strip()
    if not identity:
        raise HTTPException(status_code=401, detail="Identidade inválida")
    if not credit_wallet.enabled():
        raise HTTPException(status_code=503, detail="Carteira real ainda não habilitada")
    try:
        return {"mode": "real", **credit_wallet.snapshot(identity)}
    except Exception:
        logger.error("Credit wallet lookup unavailable")
        raise HTTPException(status_code=503, detail="Não foi possível consultar a carteira") from None
