"""Real PostgreSQL tests. Never fall back to the application's DATABASE_URL."""
import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from threading import Barrier
from uuid import uuid4

import psycopg2
import pytest
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from src.inna_platform.services.finance import credit_wallet as wallet


@pytest.fixture
def database(monkeypatch):
    dsn = os.getenv("INNA_CREDITS_TEST_DSN")
    if not dsn:
        pytest.skip("Use scripts/test-credit-wallet-postgres.ps1 for isolated PostgreSQL")
    schema = "credit_test_" + uuid4().hex
    admin = psycopg2.connect(dsn, connect_timeout=5)
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    try:
        @contextmanager
        def cursor(*, dict_cursor=False, commit_automatico=False):
            conn = psycopg2.connect(dsn, connect_timeout=5)
            try:
                with conn.cursor() as setup:
                    setup.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
                    setup.execute("SET statement_timeout TO '8s'")
                    setup.execute("SET lock_timeout TO '5s'")
                with conn.cursor(cursor_factory=RealDictCursor if dict_cursor else None) as cur:
                    yield cur
                if commit_automatico:
                    conn.commit()
                else:
                    conn.rollback()
            except BaseException:
                conn.rollback()
                raise
            finally:
                conn.close()

        migration = Path(__file__).resolve().parents[3] / "migrations/20260924_001_credit_wallet.sql"
        with cursor(commit_automatico=True) as cur:
            cur.execute(migration.read_text(encoding="utf-8-sig"))
        with cursor(commit_automatico=True) as cur:
            cur.execute((migration.parent / "20260924_002_credit_reviews.sql").read_text(encoding="utf-8-sig"))
        monkeypatch.setenv("INNA_CREDITS_ENABLED", "true")
        monkeypatch.setattr(wallet, "cursor_postgres", cursor)
        yield cursor
    finally:
        with admin.cursor() as cur:
            cur.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
        admin.close()


def grant(amount=10):
    return wallet.start("alice", "grant-1", amount, kind="grant", source="included")


def reserve(operation="analysis-1", amount=5):
    return wallet.start("alice", operation, amount, kind="usage", source="analysis")


def parallel(*calls):
    barrier = Barrier(len(calls))

    def run(call):
        barrier.wait(timeout=5)
        try:
            return call()
        except (wallet.InsufficientCredits, wallet.CreditConflict) as exc:
            return exc

    with ThreadPoolExecutor(max_workers=len(calls)) as executor:
        futures = [executor.submit(run, call) for call in calls]
        return [future.result(timeout=15) for future in futures]


def test_migration_rerunnable(database):
    migration = Path(__file__).resolve().parents[3] / "migrations/20260924_001_credit_wallet.sql"
    with database(commit_automatico=True) as cur:
        cur.execute(migration.read_text(encoding="utf-8-sig"))
    assert grant()["balance"] == 10


def test_reserve_complete_and_replay(database):
    grant()
    assert reserve()["balance"] == 5
    assert reserve()["replayed"] is True
    assert wallet.finish("alice", "analysis-1", success=True)["balance"] == 5
    assert wallet.finish("alice", "analysis-1", success=True)["replayed"] is True
    snapshot = wallet.snapshot("alice")
    assert snapshot["balance"] == 5
    assert len(snapshot["history"]) == 3


def test_concurrent_reservations_cannot_overdraw(database):
    grant(5)
    results = parallel(lambda: reserve("a"), lambda: reserve("b"))
    assert sum(isinstance(r, wallet.InsufficientCredits) for r in results) == 1
    assert wallet.snapshot("alice")["balance"] == 0
    assert len(wallet.snapshot("alice")["history"]) == 2


def test_concurrent_duplicate_grant_only_once(database):
    results = parallel(grant, grant)
    assert sorted(r["replayed"] for r in results) == [False, True]
    assert wallet.snapshot("alice")["balance"] == 10
    assert len(wallet.snapshot("alice")["history"]) == 1


def test_concurrent_duplicate_reservation_only_once(database):
    grant()
    results = parallel(reserve, reserve)
    assert sorted(r["replayed"] for r in results) == [False, True]
    assert wallet.snapshot("alice")["balance"] == 5


def test_concurrent_refund_only_once(database):
    grant()
    reserve()
    results = parallel(lambda: wallet.finish("alice", "analysis-1", success=False),
                       lambda: wallet.finish("alice", "analysis-1", success=False))
    assert sorted(r["replayed"] for r in results) == [False, True]
    assert wallet.snapshot("alice")["balance"] == 10
    assert len(wallet.snapshot("alice")["history"]) == 3


def test_conflicting_finalization(database):
    grant()
    reserve()
    results = parallel(lambda: wallet.finish("alice", "analysis-1", success=False),
                       lambda: wallet.finish("alice", "analysis-1", success=True))
    assert sum(isinstance(r, wallet.CreditConflict) for r in results) == 1
    assert len(wallet.snapshot("alice")["history"]) == 3


def test_reused_id_with_different_amount_rejected(database):
    grant()
    reserve()
    with pytest.raises(wallet.CreditConflict):
        reserve(amount=6)
    assert wallet.snapshot("alice")["balance"] == 5


def test_user_isolation(database):
    grant()
    reserve()
    assert wallet.snapshot("bob") == {"balance": 0, "history": []}
    with pytest.raises(wallet.CreditConflict):
        wallet.finish("bob", "analysis-1", success=False)
    assert wallet.snapshot("alice")["balance"] == 5


def test_ledger_failure_rolls_back_reservation(database):
    grant()
    with database(commit_automatico=True) as cur:
        cur.execute("""CREATE FUNCTION reject_reserve() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN IF NEW.event='reserve' THEN RAISE EXCEPTION 'test injected failure'; END IF;
        RETURN NEW; END $$""")
        cur.execute("CREATE TRIGGER injected_failure BEFORE INSERT ON inna_credit_ledger FOR EACH ROW EXECUTE FUNCTION reject_reserve()")
    with pytest.raises(psycopg2.Error):
        reserve()
    assert wallet.snapshot("alice")["balance"] == 10
    with database() as cur:
        cur.execute("SELECT COUNT(*) FROM inna_credit_operations WHERE kind='usage'")
        assert cur.fetchone()[0] == 0


def test_insufficient_balance_does_not_record_operation(database):
    with pytest.raises(wallet.InsufficientCredits):
        reserve()
    assert wallet.snapshot("alice") == {"balance": 0, "history": []}

# Pilot integration: real PostgreSQL accounting around a controlled INNA worker.
# No external model request, production balance or public route is used.
@pytest.fixture
def pilot(database, monkeypatch):
    from src.inna_platform.services.finance.credit_execution import run_analysis_pilot
    monkeypatch.setenv("INNA_CREDIT_EXECUTION_PILOT", "true")
    grant(10)
    return run_analysis_pilot


def test_pilot_success_and_replay(pilot):
    import asyncio
    from unittest.mock import AsyncMock
    worker = AsyncMock(return_value={"ok": True, "answer": "Análise de teste"})
    result = asyncio.run(pilot("alice", "pilot-1", worker))
    assert result["executed"] is True
    assert result["accounting"]["balance"] == 5
    replay = asyncio.run(pilot("alice", "pilot-1", worker))
    assert replay["executed"] is False
    assert replay["accounting"]["state"] == "completed"
    assert worker.await_count == 1


def test_pilot_failure_refunds_and_does_not_retry(pilot):
    import asyncio
    from unittest.mock import AsyncMock
    worker = AsyncMock(side_effect=ValueError("worker failure"))
    with pytest.raises(ValueError, match="worker failure"):
        asyncio.run(pilot("alice", "pilot-1", worker))
    assert wallet.snapshot("alice")["balance"] == 10
    replay = asyncio.run(pilot("alice", "pilot-1", worker))
    assert replay["accounting"]["state"] == "refunded"
    assert worker.await_count == 1


def test_pilot_timeout_refunds(pilot):
    import asyncio

    async def slow():
        await asyncio.sleep(10)

    with pytest.raises(TimeoutError):
        asyncio.run(pilot("alice", "pilot-1", slow, timeout_seconds=0.01))
    assert wallet.snapshot("alice")["balance"] == 10


def test_pilot_cancellation_refunds(pilot):
    import asyncio
    from unittest.mock import AsyncMock
    worker = AsyncMock(side_effect=asyncio.CancelledError)
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(pilot("alice", "pilot-1", worker))
    assert wallet.snapshot("alice")["balance"] == 10


def test_pilot_insufficient_balance_never_executes(pilot):
    import asyncio
    from unittest.mock import AsyncMock
    worker = AsyncMock()
    with pytest.raises(wallet.InsufficientCredits):
        asyncio.run(pilot("bob", "pilot-1", worker))
    worker.assert_not_called()


def test_pilot_simultaneous_repeat_executes_once(pilot):
    import asyncio

    async def scenario():
        started = asyncio.Event()
        release = asyncio.Event()
        calls = []

        async def worker():
            calls.append(1)
            started.set()
            await release.wait()
            return {"ok": True}

        first = asyncio.create_task(pilot("alice", "pilot-1", worker))
        await asyncio.wait_for(started.wait(), timeout=5)
        try:
            replay = await pilot("alice", "pilot-1", worker)
            assert replay["executed"] is False
            assert replay["accounting"]["state"] == "reserved"
        finally:
            release.set()
            await first
        assert len(calls) == 1

    asyncio.run(scenario())
    assert wallet.snapshot("alice")["balance"] == 5


def test_pilot_failed_completion_does_not_refund_success(pilot, monkeypatch):
    import asyncio
    from unittest.mock import AsyncMock

    from src.inna_platform.services.finance.credit_execution import (
        ReconciliationRequired,
    )
    original = wallet.finish

    def broken(*args, **kwargs):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(wallet, "finish", broken)
    with pytest.raises(ReconciliationRequired):
        asyncio.run(pilot("alice", "pilot-1", AsyncMock(return_value={"ok": True})))
    monkeypatch.setattr(wallet, "finish", original)
    assert wallet.snapshot("alice")["balance"] == 5
    worker = AsyncMock()
    assert asyncio.run(pilot("alice", "pilot-1", worker))["executed"] is False
    worker.assert_not_called()


def test_pilot_disabled_never_executes(database, monkeypatch):
    import asyncio
    from unittest.mock import AsyncMock

    from src.inna_platform.services.finance.credit_execution import run_analysis_pilot
    monkeypatch.delenv("INNA_CREDIT_EXECUTION_PILOT", raising=False)
    worker = AsyncMock()
    with pytest.raises(RuntimeError, match="disabled"):
        asyncio.run(run_analysis_pilot("alice", "pilot-1", worker))
    worker.assert_not_called()
    assert wallet.snapshot("alice")["history"] == []


@pytest.fixture
def real_adapter(pilot, monkeypatch):
    from src.inna_platform.services.finance.credit_inna_pilot import analyze_local
    monkeypatch.setenv("INNA_REAL_CREDIT_PILOT", "true")
    return analyze_local


def test_real_adapter_contract_and_replay(real_adapter):
    import asyncio

    import httpx
    calls = []

    def handler(request):
        import json
        assert str(request.url) == "http://127.0.0.1:8000/rag/ask"
        assert json.loads(request.content)["pergunta"] == "Como organizar um orçamento?"
        calls.append(1)
        return httpx.Response(200, json={"resposta": "Resposta controlada"})

    transport = httpx.MockTransport(handler)
    result = asyncio.run(real_adapter("alice", "Como organizar um orçamento?", transport=transport))
    assert result["accounting"]["balance"] == 5
    replay = asyncio.run(real_adapter("alice", "Como organizar um orçamento?", transport=transport))
    assert replay["executed"] is False
    assert len(calls) == 1


@pytest.mark.parametrize("mode", ["timeout", "invalid", "http_error"])
def test_real_adapter_uncertain_outcome_stays_pending(real_adapter, mode):
    import asyncio

    import httpx

    from src.inna_platform.services.finance.credit_execution import (
        ReconciliationRequired,
    )

    def handler(request):
        if mode == "timeout":
            raise httpx.ReadTimeout("test timeout", request=request)
        return httpx.Response(500 if mode == "http_error" else 200, json={})

    with pytest.raises(ReconciliationRequired):
        asyncio.run(real_adapter("alice", "Pergunta controlada", transport=httpx.MockTransport(handler)))
    assert wallet.snapshot("alice")["balance"] == 5
    pending = wallet.pending_reservations("alice", minimum_age_seconds=0)
    assert len(pending) == 1
    assert wallet.pending_reservations("bob", minimum_age_seconds=0) == []


def test_pending_resolved_without_second_execution(pilot):
    reserve()
    pending = wallet.pending_reservations("alice", minimum_age_seconds=0)
    assert len(pending) == 1
    wallet.finish("alice", pending[0]["operation_id"], success=False)
    assert wallet.pending_reservations("alice", minimum_age_seconds=0) == []
    assert wallet.snapshot("alice")["balance"] == 10


def test_local_inna_live_analysis(real_adapter):
    """Explicit opt-in: calls local INNA, which may incur Gemini provider cost."""
    import asyncio
    if os.getenv("INNA_RUN_LIVE_CREDIT_TEST") != "true":
        pytest.skip("Pass -LiveInna to run one real local INNA analysis")
    result = asyncio.run(real_adapter("alice", "Explique o que é um orçamento pessoal, sem usar dados pessoais."))
    assert result["executed"] is True
    assert result["result"]["analysis"]["resposta"].strip()
    assert result["accounting"]["state"] == "completed"
    assert wallet.snapshot("alice")["balance"] == 5


def review_pending(monkeypatch, *, success=False, reason="Worker confirmed not executed"):
    monkeypatch.setenv("INNA_CREDIT_REVIEWERS", "reviewer-test")
    return wallet.reconcile("alice", "analysis-1", reviewer_id="reviewer-test",
                            success=success, reason=reason, evidence_ref="trace:test-123")


def test_review_authorization(database, monkeypatch):
    grant()
    reserve()
    monkeypatch.delenv("INNA_CREDIT_REVIEWERS", raising=False)
    with pytest.raises(PermissionError):
        wallet.reconcile("alice", "analysis-1", reviewer_id="outsider", success=False,
                         reason="Worker confirmed not executed", evidence_ref="trace:123")
    assert wallet.snapshot("alice")["balance"] == 5


def test_review_audited_and_idempotent(database, monkeypatch):
    grant()
    reserve()
    assert review_pending(monkeypatch)["balance"] == 10
    assert review_pending(monkeypatch)["replayed"] is True
    with database() as cur:
        cur.execute("SELECT reviewer_id,decision,reason,evidence_ref FROM inna_credit_reviews")
        rows = cur.fetchall()
        assert len(rows) == 1
        assert rows[0][0:2] == ("reviewer-test", "refunded")


def test_review_cannot_change_evidence(database, monkeypatch):
    grant()
    reserve()
    review_pending(monkeypatch)
    with pytest.raises(wallet.CreditConflict):
        review_pending(monkeypatch, reason="Changed evidence must not overwrite audit")
    assert wallet.snapshot("alice")["balance"] == 10


def test_review_audit_failure_rolls_back(database, monkeypatch):
    grant()
    reserve()
    with database(commit_automatico=True) as cur:
        cur.execute("ALTER TABLE inna_credit_reviews ADD CONSTRAINT test_failure CHECK (false)")
    with pytest.raises(psycopg2.Error):
        review_pending(monkeypatch)
    assert wallet.snapshot("alice")["balance"] == 5
    assert len(wallet.pending_reservations("alice", minimum_age_seconds=0)) == 1


def test_review_completion_keeps_charge(database, monkeypatch):
    grant()
    reserve()
    assert review_pending(monkeypatch, success=True)["balance"] == 5
    assert wallet.pending_reservations("alice", minimum_age_seconds=0) == []


@pytest.fixture
def pix_database(database, monkeypatch):
    from src.inna_platform.services.finance import manual_pix
    migration = Path(__file__).resolve().parents[3] / "migrations/20260924_003_manual_pix.sql"
    with database(commit_automatico=True) as cur:
        cur.execute(migration.read_text(encoding="utf-8-sig"))
    with database(commit_automatico=True) as cur:
        cur.execute("CREATE TABLE inna_auth_users(user_id TEXT PRIMARY KEY, active BOOLEAN NOT NULL DEFAULT TRUE)")
        cur.execute((migration.parent / "20260925_004_pix_approval.sql").read_text(encoding="utf-8-sig"))
    from src.inna_platform.services.finance import platform_entitlements
    monkeypatch.setattr(platform_entitlements, "cursor_postgres", database)
    platform_entitlements.ensure_entitlement_schema()
    monkeypatch.setattr(manual_pix, "cursor_postgres", database)
    monkeypatch.setattr(manual_pix, "configuration", lambda: {
        "enabled": True, "key": "+5511999999999", "receiver": "TEST RECEIVER", "city": "TEST CITY",
    })
    return manual_pix


def test_pix_order_persists_exact_instructions(pix_database, database):
    import xml.etree.ElementTree as ET
    order = pix_database.create_order("test-alice", "credits_100")
    assert ET.fromstring(order["svg"]).tag.endswith("svg")
    with database() as cur:
        cur.execute("SELECT user_id,amount_cents,pix_payload,status FROM inna_manual_pix_orders WHERE order_id=%s", (order["order_id"],))
        assert cur.fetchone() == ("test-alice", 1990, order["payload"], "awaiting_manual_verification")
    assert wallet.snapshot("test-alice")["balance"] == 0


def test_pix_key_rotation_preserves_previous_order(pix_database, database, monkeypatch):
    first = pix_database.create_order("test-alice", "credits_100")
    monkeypatch.setattr(pix_database, "configuration", lambda: {
        "enabled": True, "key": "+5511988888888", "receiver": "TEST RECEIVER", "city": "TEST CITY",
    })
    second = pix_database.create_order("test-alice", "credits_100")
    assert first["key"] != second["key"]
    with database() as cur:
        cur.execute("SELECT receiver_key,pix_payload FROM inna_manual_pix_orders WHERE order_id=%s", (first["order_id"],))
        assert cur.fetchone() == (first["key"], first["payload"])


def test_pix_qr_failure_does_not_persist(pix_database, database, monkeypatch):
    def broken(_):
        raise RuntimeError("QR unavailable")
    monkeypatch.setattr(pix_database, "qr_svg", broken)
    with pytest.raises(RuntimeError):
        pix_database.create_order("test-alice", "credits_100")
    with database() as cur:
        cur.execute("SELECT COUNT(*) FROM inna_manual_pix_orders")
        assert cur.fetchone()[0] == 0


def test_pix_insert_failure_rolls_back(pix_database, database):
    with database(commit_automatico=True) as cur:
        cur.execute("ALTER TABLE inna_manual_pix_orders ADD CONSTRAINT injected_pix_failure CHECK(false)")
    with pytest.raises(psycopg2.Error):
        pix_database.create_order("test-alice", "credits_100")
    with database() as cur:
        cur.execute("SELECT COUNT(*) FROM inna_manual_pix_orders")
        assert cur.fetchone()[0] == 0


def pix_client(identity):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from src.inna_platform.services.finance.finance_auth_routes import (
        get_authenticated_user,
    )
    from src.inna_platform.services.finance.manual_pix_routes import router
    app = FastAPI()
    app.include_router(router)
    if identity is not None:
        app.dependency_overrides[get_authenticated_user] = lambda: identity
    return TestClient(app)


def test_pix_api_uses_server_price_and_identity(pix_database, database):
    client = pix_client({"user_id": "test-alice"})
    response = client.post("/api/platform/pix/orders", headers={"X-Sabino-Pix": "manual"}, json={"product_code": "credits_100"})
    assert response.status_code == 200
    assert response.json()["amount_cents"] == 1990
    manipulated = client.post("/api/platform/pix/orders", headers={"X-Sabino-Pix": "manual"}, json={"product_code": "credits_100", "amount_cents": 1, "user_id": "bob"})
    assert manipulated.status_code == 422
    with database() as cur:
        cur.execute("SELECT user_id,amount_cents FROM inna_manual_pix_orders")
        assert cur.fetchall() == [("test-alice", 1990)]


def test_pix_authentication_and_origin_blocked(pix_database, database):
    assert pix_client(None).post("/api/platform/pix/orders", json={"product_code": "credits_100"}).status_code == 401
    response = pix_client({"user_id": "test-alice"}).post("/api/platform/pix/orders", headers={"X-Sabino-Pix": "manual", "Origin": "https://untrusted.example"}, json={"product_code": "credits_100"})
    assert response.status_code == 403
    with database() as cur:
        cur.execute("SELECT COUNT(*) FROM inna_manual_pix_orders")
        assert cur.fetchone()[0] == 0

@pytest.fixture
def pix_review(pix_database, database, monkeypatch):
    from src.inna_platform.services.finance import manual_pix_review
    monkeypatch.setattr(manual_pix_review, 'cursor_postgres', database)
    with database(commit_automatico=True) as cur:
        cur.execute("INSERT INTO inna_auth_users(user_id) VALUES ('test-alice'),('test-bob'),('reviewer')")
        cur.execute("INSERT INTO inna_pix_reviewers(user_id) VALUES ('reviewer')")
    return manual_pix_review


def confirm_pix(review, order, reference='E1234567890123456789012345678901', **kwargs):
    args = dict(reviewer_id='reviewer', bank_reference=reference,
                received_cents=order['amount_cents'], reason='Recebimento conferido no extrato bancário')
    args.update(kwargs)
    return review.approve(order['order_id'], **args)


def test_pix_approval_once_concurrent(pix_review, pix_database, database):
    order=pix_database.create_order('test-alice','credits_100')
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _: confirm_pix(pix_review,order),range(2)))
    assert sorted(r['replayed'] for r in results)==[False,True]
    assert wallet.snapshot('test-alice')['balance']==100
    assert len(wallet.snapshot('test-alice')['history'])==1
    with database() as cur:
        cur.execute('SELECT COUNT(*) FROM inna_manual_pix_reviews')
        assert cur.fetchone()[0]==1


def test_pix_duplicate_receipt_rejected(pix_review,pix_database):
    a=pix_database.create_order('test-alice','credits_100')
    b=pix_database.create_order('test-bob','credits_100')
    confirm_pix(pix_review,a)
    with pytest.raises(pix_review.PixConflict):
        confirm_pix(pix_review,b)
    assert wallet.snapshot('test-bob')['balance']==0


def test_pix_wrong_amount_and_unauthorized(pix_review,pix_database):
    order=pix_database.create_order('test-alice','credits_100')
    with pytest.raises(PermissionError):
        confirm_pix(pix_review,order,reviewer_id='test-alice')
    with pytest.raises(pix_review.PixConflict):
        confirm_pix(pix_review,order,received_cents=1)
    assert wallet.snapshot('test-alice')['balance']==0


def test_pix_failure_rolls_back_access_credits_and_audit(pix_review,pix_database,database):
    order=pix_database.create_order('test-alice','essencial')
    with database(commit_automatico=True) as cur:
        cur.execute('ALTER TABLE inna_credit_ledger ADD CONSTRAINT injected_failure CHECK(false)')
    with pytest.raises(psycopg2.Error):
        confirm_pix(pix_review,order)
    assert wallet.snapshot('test-alice')['balance']==0
    with database() as cur:
        cur.execute('SELECT COUNT(*) FROM inna_manual_pix_reviews')
        assert cur.fetchone()[0]==0
        cur.execute('SELECT COUNT(*) FROM inna_user_platform_entitlements')
        assert cur.fetchone()[0]==0
        cur.execute('SELECT status FROM inna_manual_pix_orders')
        assert cur.fetchone()[0]=='awaiting_manual_verification'


def test_pix_plan_grants_and_renews_month(pix_review,pix_database,database):
    first=pix_database.create_order('test-alice','essencial')
    confirm_pix(pix_review,first)
    with database() as cur:
        cur.execute("SELECT plan_code,status,expires_at FROM inna_user_platform_entitlements WHERE user_id='test-alice'")
        plan,status,expires=cur.fetchone()
    assert (plan,status)==('essencial','active')
    second=pix_database.create_order('test-alice','essencial')
    confirm_pix(pix_review,second,reference='E2222222222222222222222222222222')
    with database() as cur:
        cur.execute("SELECT expires_at > %s + INTERVAL '27 days' FROM inna_user_platform_entitlements WHERE user_id='test-alice'",(expires,))
        assert cur.fetchone()[0] is True
    assert wallet.snapshot('test-alice')['balance']==200


def test_pix_snapshot_survives_catalog_change(pix_review,pix_database,monkeypatch):
    order=pix_database.create_order('test-alice','credits_100')
    monkeypatch.setattr(pix_database,'products',lambda: {})
    confirm_pix(pix_review,order)
    assert wallet.snapshot('test-alice')['balance']==100


def test_pix_customer_order_isolation(pix_review,pix_database):
    order=pix_database.create_order('test-alice','credits_100')
    bob=pix_client({'user_id':'test-bob'})
    assert bob.get('/api/platform/pix/orders').json()=={'orders':[]}
    assert bob.get('/api/platform/pix/orders/'+order['order_id']).status_code==404
    alice=pix_client({'user_id':'test-alice'})
    assert alice.get('/api/platform/pix/orders/'+order['order_id']).json()['payload']==order['payload']


def test_pix_review_api_permissions_and_csrf(pix_review,pix_database):
    order=pix_database.create_order('test-alice','credits_100')
    path='/api/platform/pix/review/'+order['order_id']
    body=dict(bank_reference='E1234567890123456789012345678901',received_cents=1990,
              reason='Conferido no extrato do banco',bank_verified=True)
    reviewer=pix_client({'user_id':'reviewer'})
    assert reviewer.post(path,json=body).status_code==403
    assert reviewer.post(path,json=body,headers={'X-Sabino-Pix':'manual','Origin':'https://evil.example'}).status_code==403
    outsider=pix_client({'user_id':'test-alice'})
    assert outsider.get('/api/platform/pix/review/pending').status_code==403
    assert outsider.post(path,json=body,headers={'X-Sabino-Pix':'manual'}).status_code==403
    assert reviewer.post(path,json={**body,'bank_verified':False},headers={'X-Sabino-Pix':'manual'}).status_code==422
    assert reviewer.post(path,json={**body,'reviewer_id':'reviewer'},headers={'X-Sabino-Pix':'manual'}).status_code==422
    assert reviewer.post(path,json=body,headers={'X-Sabino-Pix':'manual'}).status_code==200
    assert wallet.snapshot('test-alice')['balance']==100


def test_pix_legacy_order_not_silently_granted(pix_review,pix_database,database):
    order=pix_database.create_order('test-alice','credits_100')
    with database(commit_automatico=True) as cur:
        cur.execute('UPDATE inna_manual_pix_orders SET fulfillment=NULL')
    with pytest.raises(pix_review.PixConflict):
        confirm_pix(pix_review,order)
    assert wallet.snapshot('test-alice')['balance']==0
