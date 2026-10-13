from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from test_credit_wallet_postgres import database, pix_database, pix_review, confirm_pix
from src.inna_platform.services.finance import finance_pilot as pilot, credit_wallet as wallet, platform_entitlements as access
from src.inna_platform.services.finance.finance_auth_routes import get_authenticated_user

@pytest.fixture
def invited(pix_review, database, monkeypatch):
    monkeypatch.setenv('SABINO_FINANCE_PILOT_ENABLED','true')
    monkeypatch.setenv('SABINO_FINANCE_PILOT_USERS','test-alice,test-bob')
    monkeypatch.setattr(pilot,'cursor_postgres',database)
    pilot.ensure_schema()
    return pilot

def test_disabled_offer_never_opens_database(monkeypatch):
    monkeypatch.delenv('SABINO_FINANCE_PILOT_ENABLED',raising=False)
    def forbidden(**kwargs):raise AssertionError('No database changes while disabled')
    monkeypatch.setattr(pilot,'cursor_postgres',forbidden)
    assert pilot.offer_status('alice')['state']=='unavailable'
    with pytest.raises(HTTPException) as exc:pilot.activate('alice')
    assert exc.value.status_code==503

def test_activation_exact_benefits_and_replay(invited,database):
    first=pilot.activate('test-alice');again=pilot.activate('test-alice')
    assert not first['replayed'] and again['replayed']
    assert first['expires_at']==again['expires_at']
    assert wallet.snapshot('test-alice')['balance']==15
    with database() as cur:
        cur.execute("SELECT expires_at-started_at FROM inna_finance_pilot_enrollments WHERE user_id='test-alice'")
        assert cur.fetchone()[0].days==30
    assert pilot.offer_status('test-alice')['state']=='active'
    assert access.has_active_platform_entitlement(user_id='test-alice',platform_code='financeiro')

def test_concurrent_activation_only_grants_once(invited):
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:pilot.activate('test-alice'),range(2)))
    assert sorted(x['replayed'] for x in results)==[False,True]
    assert wallet.snapshot('test-alice')['balance']==15
    assert len(wallet.snapshot('test-alice')['history'])==1

def test_uninvited_account_cannot_activate(invited):
    assert pilot.offer_status('reviewer')['state']=='not_invited'
    with pytest.raises(HTTPException) as exc:pilot.activate('reviewer')
    assert exc.value.status_code==403
    assert wallet.snapshot('reviewer')['balance']==0

@pytest.mark.parametrize('status',['active','expired','pending','cancelled'])
def test_any_existing_plan_is_preserved(invited,database,status):
    with database(commit_automatico=True) as cur:
        cur.execute("INSERT INTO inna_user_platform_entitlements(entitlement_id,user_id,platform_code,plan_code,status) VALUES ('existing','test-alice','financeiro','essencial',%s)",(status,))
    with pytest.raises(HTTPException) as exc:pilot.activate('test-alice')
    assert exc.value.status_code==409
    assert pilot.offer_status('test-alice')['state']=='existing_plan'
    assert wallet.snapshot('test-alice')['balance']==0
    with database() as cur:
        cur.execute("SELECT plan_code,status,expires_at FROM inna_user_platform_entitlements WHERE user_id='test-alice'")
        assert cur.fetchone()==('essencial',status,None)

def test_failed_credit_grant_rolls_back_access(invited,database):
    with database(commit_automatico=True) as cur:cur.execute('ALTER TABLE inna_credit_ledger ADD CONSTRAINT fail_test CHECK(false)')
    with pytest.raises(Exception):pilot.activate('test-alice')
    with database() as cur:
        cur.execute('SELECT COUNT(*) FROM inna_finance_pilot_enrollments');assert cur.fetchone()[0]==0
        cur.execute('SELECT COUNT(*) FROM inna_user_platform_entitlements');assert cur.fetchone()[0]==0
    assert wallet.snapshot('test-alice')['balance']==0

def test_expiry_does_not_renew_or_delete_credits(invited,database):
    pilot.activate('test-alice')
    with database(commit_automatico=True) as cur:
        cur.execute("UPDATE inna_finance_pilot_enrollments SET expires_at=NOW()-INTERVAL '1 second'")
        cur.execute("UPDATE inna_user_platform_entitlements SET expires_at=NOW()-INTERVAL '1 second'")
    assert pilot.offer_status('test-alice')['state']=='expired'
    assert not access.has_active_platform_entitlement(user_id='test-alice',platform_code='financeiro')
    assert pilot.activate('test-alice')['replayed']
    assert wallet.snapshot('test-alice')['balance']==15

def test_paid_upgrade_preserves_trial_days_and_is_once(invited,pix_database,pix_review,database):
    first=pilot.activate('test-alice')
    order=pix_database.create_order('test-alice','essencial')
    confirm_pix(pix_review,order);confirm_pix(pix_review,order)
    assert wallet.snapshot('test-alice')['balance']==115
    assert pilot.offer_status('test-alice')['state']=='converted'
    with database() as cur:
        cur.execute("SELECT plan_code,expires_at > %s+INTERVAL '27 days' FROM inna_user_platform_entitlements WHERE user_id='test-alice'",(first['expires_at'],))
        assert cur.fetchone()==('essencial',True)

def test_pix_preserves_permanent_existing_access(invited,pix_database,pix_review,database):
    with database(commit_automatico=True) as cur:
        cur.execute("INSERT INTO inna_user_platform_entitlements(entitlement_id,user_id,platform_code,plan_code,status) VALUES ('existing','test-alice','financeiro','essencial','active')")
    order=pix_database.create_order('test-alice','essencial')
    with pytest.raises(pix_review.PixConflict):confirm_pix(pix_review,order)
    assert wallet.snapshot('test-alice')['balance']==0
    with database() as cur:
        cur.execute('SELECT expires_at FROM inna_user_platform_entitlements');assert cur.fetchone()[0] is None

def test_http_identity_csrf_and_no_editable_benefits(invited):
    app=FastAPI();app.include_router(pilot.router)
    app.dependency_overrides[get_authenticated_user]=lambda:{'user_id':'test-alice'}
    client=TestClient(app);url='/api/platform/finance/pilot/activate';headers={'X-Sabino-Pilot':'activate'}
    assert client.post(url,json={'activate':True}).status_code==403
    assert client.post(url,json={'activate':True},headers={**headers,'Origin':'https://evil.example'}).status_code==403
    assert client.post(url,json={'activate':True,'credits':1000},headers=headers).status_code==422
    assert client.post(url,json={'activate':False},headers=headers).status_code==422
    assert client.post(url,json={'activate':True},headers=headers).status_code==200
    assert wallet.snapshot('test-alice')['balance']==15
    assert wallet.snapshot('test-bob')['balance']==0
