"""Authenticated subscription navigation; checkout is configured separately."""
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from src.inna_platform.services.finance.finance_auth_routes import get_authenticated_user

router = APIRouter(tags=["finance-subscription"])


@router.get("/financeiro/meu-plano", include_in_schema=False)
def my_finance_plan(user: dict = Depends(get_authenticated_user)):
    page = Path(__file__).resolve().parents[2] / "static" / "financeiro-meu-plano.html"
    return FileResponse(page, headers={"Cache-Control": "no-store"})
