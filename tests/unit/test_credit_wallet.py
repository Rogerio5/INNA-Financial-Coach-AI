from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.inna_platform.services.finance import credit_routes, credit_wallet
from src.inna_platform.services.finance.finance_auth_routes import (
    get_authenticated_user,
)


@pytest.mark.parametrize("amount", [True, 0, -1, 1.5, "5", 1_000_000_001])
def test_invalid_amount_never_touches_database(amount):
    with patch.object(credit_wallet, "cursor_postgres") as db:
        with pytest.raises(ValueError):
            credit_wallet.start("user-a", "op", amount, kind="usage", source="analysis")
        db.assert_not_called()


def test_disabled_accounting_cannot_mutate(monkeypatch):
    monkeypatch.delenv("INNA_CREDITS_ENABLED", raising=False)
    with patch.object(credit_wallet, "cursor_postgres") as db:
        with pytest.raises(RuntimeError):
            credit_wallet.start("user-a", "op", 5, kind="usage", source="analysis")
        db.assert_not_called()


def client_for(identity):
    app = FastAPI()
    app.include_router(credit_routes.router)
    app.dependency_overrides[get_authenticated_user] = lambda: identity
    return TestClient(app)


def test_wallet_uses_authenticated_identity_not_query(monkeypatch):
    monkeypatch.setenv("INNA_CREDITS_ENABLED", "true")
    with patch.object(credit_wallet, "snapshot", return_value={"balance": 7, "history": []}) as read:
        response = client_for({"user_id": "user-a"}).get("/api/platform/credits/wallet?user_id=user-b")
        assert response.status_code == 200
        assert response.json()["balance"] == 7
        read.assert_called_once_with("user-a")


def test_no_public_mutation_endpoint():
    assert client_for({"user_id": "user-a"}).post("/api/platform/credits/wallet", json={"balance": 1000}).status_code == 405


def test_disabled_wallet_never_returns_demo_balance(monkeypatch):
    monkeypatch.delenv("INNA_CREDITS_ENABLED", raising=False)
    response = client_for({"user_id": "user-a"}).get("/api/platform/credits/wallet")
    assert response.status_code == 503
    assert "balance" not in response.json()


def test_authentication_required():
    app = FastAPI()
    app.include_router(credit_routes.router)

    def denied():
        raise HTTPException(status_code=401)

    app.dependency_overrides[get_authenticated_user] = denied
    assert TestClient(app).get("/api/platform/credits/wallet").status_code == 401


@pytest.mark.parametrize("reviewers", ["", "another-reviewer"])
def test_unauthorized_review_never_opens_transaction(monkeypatch, reviewers):
    monkeypatch.setenv("INNA_CREDIT_REVIEWERS", reviewers)
    with patch.object(credit_wallet, "locked_wallet") as transaction:
        with pytest.raises(PermissionError):
            credit_wallet.reconcile(
                "user-a", "operation-1", reviewer_id="outsider", success=False,
                reason="A sufficiently detailed reason", evidence_ref="trace:123",
            )
        transaction.assert_not_called()
