from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt

from src.inna_platform.services.finance import manual_pix, manual_pix_review
from src.inna_platform.services.finance.finance_auth_routes import (
    get_authenticated_user,
)

router = APIRouter(prefix="/api/platform/pix", tags=["manual-pix"])


class OrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_code: str


@router.get("/catalog")
def catalog(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return {
        "enabled": manual_pix.configuration().get("enabled") is True,
        "products": manual_pix.products(),
    }


@router.post("/orders")
def create_order(
    body: OrderRequest,
    request: Request,
    response: Response,
    user: Annotated[dict, Depends(get_authenticated_user)],
):
    # Custom header blocks cross-origin form submissions. No permissive CORS here.
    if (
        request.headers.get("X-Sabino-Pix") != "manual"
        or request.headers.get("sec-fetch-site") == "cross-site"
    ):
        raise HTTPException(403, "Solicitação inválida")
    origin = request.headers.get("origin")
    if origin and origin != str(request.base_url).rstrip("/"):
        raise HTTPException(403, "Origem inválida")
    identity = str(user.get("user_id") or "").strip()
    if not identity:
        raise HTTPException(401, "Identidade inválida")
    if body.product_code not in manual_pix.products():
        raise HTTPException(400, "Produto inválido")
    response.headers["Cache-Control"] = "no-store"
    try:
        return manual_pix.create_order(identity, body.product_code)
    except Exception:
        raise HTTPException(
            503,
            "Pix indisponível. Nenhum pagamento deve ser feito sem instruções geradas.",
        ) from None


@router.get("/orders")
def orders(response: Response, user: Annotated[dict, Depends(get_authenticated_user)]):
    response.headers["Cache-Control"] = "no-store"
    return {"orders": manual_pix.user_orders(user["user_id"])}


@router.get("/orders/{order_id}")
def order_detail(
    order_id: str,
    response: Response,
    user: Annotated[dict, Depends(get_authenticated_user)],
):
    response.headers["Cache-Control"] = "no-store"
    try:
        return manual_pix.user_order(user["user_id"], order_id)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from None


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bank_reference: str = Field(min_length=8, max_length=120)
    received_cents: StrictInt = Field(gt=0)
    reason: str = Field(min_length=10, max_length=2000)
    bank_verified: StrictBool


@router.get("/review/pending")
def pending_reviews(
    response: Response, user: Annotated[dict, Depends(get_authenticated_user)]
):
    response.headers["Cache-Control"] = "no-store"
    try:
        return {"orders": manual_pix_review.pending(user["user_id"])}
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from None


@router.post("/review/{order_id}")
def approve_order(
    order_id: str,
    body: ReviewRequest,
    request: Request,
    response: Response,
    user: Annotated[dict, Depends(get_authenticated_user)],
):
    response.headers["Cache-Control"] = "no-store"
    if (
        request.headers.get("X-Sabino-Pix") != "manual"
        or request.headers.get("sec-fetch-site") == "cross-site"
        or (
            request.headers.get("origin")
            and request.headers["origin"] != str(request.base_url).rstrip("/")
        )
    ):
        raise HTTPException(403, "Origem inválida")
    if not body.bank_verified:
        raise HTTPException(422, "Confirme o recebimento diretamente no banco")
    try:
        return manual_pix_review.approve(
            order_id,
            reviewer_id=user["user_id"],
            bank_reference=body.bank_reference,
            received_cents=body.received_cents,
            reason=body.reason,
        )
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from None
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from None
    except manual_pix_review.PixConflict as exc:
        raise HTTPException(409, str(exc)) from None
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    except Exception:
        raise HTTPException(
            503,
            "Conferência indisponível. Consulte o pedido antes de tentar novamente.",
        ) from None
