from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from test_credit_wallet_postgres import database, pix_database, pix_review

from src.inna_platform.services import sabino_onboarding as onboarding
from src.inna_platform.services.finance import finance_pilot
from src.inna_platform.services.finance.finance_auth_routes import get_authenticated_user


@pytest.fixture
def setup(pix_review, database, monkeypatch):
    monkeypatch.setattr(onboarding, 'cursor_postgres', database)
    monkeypatch.setattr(finance_pilot, 'cursor_postgres', database)
    monkeypatch.setenv('SABINO_ADMIN_USERS', 'reviewer')
    onboarding.ensure_schema()
    finance_pilot.ensure_schema()
    with database(commit_automatico=True) as cur:
        cur.execute("ALTER TABLE inna_auth_users ADD COLUMN email TEXT")
        cur.execute("UPDATE inna_auth_users SET email=user_id || '@example.test'")
        cur.execute((Path(__file__).resolve().parents[3] / 'migrations/20260927_005_paid_analysis.sql').read_text())
        cur.execute("INSERT INTO inna_finance_pilot_enrollments(user_id) VALUES ('test-alice'),('test-bob')")


def client(user_id='test-alice'):
    app = FastAPI()
    app.include_router(onboarding.router)
    if user_id:
        app.dependency_overrides[get_authenticated_user] = lambda: {'user_id': user_id}
    return TestClient(app)


def complete(c, step='account_reviewed', **extra):
    return c.post('/api/sabino/onboarding', json={'step': step, **extra}, headers={'X-Sabino-Onboarding': '1'})


def test_auth_admin_default_deny_and_csrf(setup, monkeypatch):
    assert client(None).get('/api/sabino/onboarding').status_code == 401
    for path in ('/admin/primeiros-passos', '/api/sabino/admin/onboarding'):
        assert client().get(path).status_code == 403
        assert client('reviewer').get(path).status_code == 200
    monkeypatch.delenv('SABINO_ADMIN_USERS')
    assert client('reviewer').get('/api/sabino/admin/onboarding').status_code == 403
    c = client()
    assert c.post('/api/sabino/onboarding', json={'step':'account_reviewed'}).status_code == 403
    assert c.post('/api/sabino/onboarding', json={'step':'account_reviewed'}, headers={'X-Sabino-Onboarding':'1','Origin':'https://evil.example'}).status_code == 403
    assert c.post('/api/sabino/onboarding', json={'step':'account_reviewed'}, headers={'X-Sabino-Onboarding':'1','sec-fetch-site':'cross-site'}).status_code == 403


def test_steps_are_idempotent_isolated_and_cannot_fake_analysis(setup, database):
    c = client()
    assert complete(c).status_code == 200
    first = c.get('/api/sabino/onboarding').json()
    assert complete(c).status_code == 200
    assert c.get('/api/sabino/onboarding').json() == first
    assert first['completed'] == 1
    assert client('test-bob').get('/api/sabino/onboarding').json()['completed'] == 0
    assert complete(c, user_id='test-bob').status_code == 422
    assert complete(c, 'inna_analysis').status_code == 422
    with database() as cur:
        cur.execute('SELECT COUNT(*) FROM inna_credit_ledger')
        assert cur.fetchone()[0] == 0


def test_admin_real_completed_analysis_and_missing_steps(setup, database):
    with database(commit_automatico=True) as cur:
        cur.execute("""INSERT INTO inna_paid_analyses(user_id,request_id,quote_id,payload_hash,cost,state)
            VALUES ('test-alice',%s,%s,'test',1,'running')""", (str(uuid4()), str(uuid4())))
    admin = client('reviewer')
    def participants(): return {r['user_id']:r for r in admin.get('/api/sabino/admin/onboarding').json()['participants']}
    assert participants()['test-alice']['status'] == 'not_started'
    with database(commit_automatico=True) as cur:
        cur.execute("UPDATE inna_paid_analyses SET state='completed'")
    assert participants()['test-alice']['completed'] == 1
    assert participants()['test-alice']['next_step'] == 'account_reviewed'
    complete(client());complete(client(), 'platforms_explored')
    assert participants()['test-alice']['status'] == 'completed'
    assert participants()['test-bob']['status'] == 'not_started'
    assert admin.get('/api/sabino/admin/onboarding?limit=1&offset=1').json()['total'] == 2
    assert len(admin.get('/api/sabino/admin/onboarding?limit=1&offset=1').json()['participants']) == 1
    assert admin.get('/api/sabino/admin/onboarding?limit=101').status_code == 422


def test_missing_analysis_data_is_unknown_not_unused(setup, database):
    with database(commit_automatico=True) as cur:
        cur.execute('DROP TABLE inna_paid_analysis_reviews')
        cur.execute('DROP TABLE inna_paid_analyses')
    row = client('reviewer').get('/api/sabino/admin/onboarding').json()['participants'][0]
    assert row['status'] == 'unknown'
    assert row['analysis_available'] is False


def test_database_errors_do_not_expose_details(setup, monkeypatch):
    def fail(): raise RuntimeError('secret connection details')
    monkeypatch.setattr(onboarding, 'ensure_schema', fail)
    for c,path in ((client(),'/api/sabino/onboarding'),(client('reviewer'),'/api/sabino/admin/onboarding')):
        response=c.get(path)
        assert response.status_code == 503
        assert 'secret' not in response.text


def followup(c, **overrides):
    body = {'user_id':'test-alice','situation':'help','reason':'technical','note':'Erro relatado ao abrir a análise'}
    body.update(overrides)
    return c.post('/api/sabino/admin/onboarding/followup', json=body, headers={'X-Sabino-Onboarding':'1'})


def test_manual_followup_authorization_reason_audit_and_resolution(setup, database):
    admin = client('reviewer')
    assert followup(client()).status_code == 403
    assert followup(admin, situation='withdrawn', note='').status_code == 422
    assert followup(admin, situation='normal').status_code == 422
    assert followup(admin, user_id='missing').status_code == 404
    assert admin.post('/api/sabino/admin/onboarding/followup',json={'user_id':'test-alice','situation':'help','reason':'technical'}).status_code == 403
    assert followup(admin).status_code == 200
    report = admin.get('/api/sabino/admin/onboarding?situation=help').json()
    assert report['total'] == 1
    assert report['summary']['reasons'] == {'technical':1}
    assert report['participants'][0]['followup']['admin_id'] == 'reviewer'
    assert followup(admin,situation='withdrawn',reason='time',note='Participante confirmou que não continuará').status_code == 200
    assert followup(admin,situation='normal',reason='resolved').status_code == 200
    report = admin.get('/api/sabino/admin/onboarding').json()
    assert report['summary']['reasons'] == {}
    assert report['summary']['situations']['not_started'] == 2
    with database() as cur:
        cur.execute('SELECT COUNT(*) FROM sabino_participant_followups')
        assert cur.fetchone()[0] == 3
        cur.execute("SELECT active FROM inna_auth_users WHERE user_id='test-alice'")
        assert cur.fetchone()[0] is True


def test_global_summary_is_not_page_or_search_total(setup, database):
    with database(commit_automatico=True) as cur:
        for i in range(55):
            uid=f'participant-{i}'
            cur.execute('INSERT INTO inna_auth_users(user_id,email) VALUES (%s,%s)',(uid,uid+'@example.test'))
            cur.execute('INSERT INTO inna_finance_pilot_enrollments(user_id) VALUES (%s)',(uid,))
    result=client('reviewer').get('/api/sabino/admin/onboarding?limit=1&search=test-alice').json()
    assert result['total'] == 1
    assert len(result['participants']) == 1
    assert result['summary']['total'] == 57
    assert sum(result['summary']['situations'].values()) == 57


def test_recent_analysis_uses_latest_completion_not_first(setup, database):
    with database(commit_automatico=True) as cur:
        for days in (20,1):
            cur.execute("""INSERT INTO inna_paid_analyses(user_id,request_id,quote_id,payload_hash,cost,state,updated_at)
                VALUES ('test-alice',%s,%s,'test',1,'completed',NOW()-%s*INTERVAL '1 day')""",(str(uuid4()),str(uuid4()),days))
        cur.execute("INSERT INTO sabino_onboarding_steps(user_id,step,completed_at) VALUES ('test-bob','account_reviewed',NOW()-INTERVAL '8 days')")
    result=client('reviewer').get('/api/sabino/admin/onboarding').json()
    assert result['summary']['situations']['active'] == 1
    assert result['summary']['situations']['inactive'] == 1
    assert result['summary']['situations']['withdrawn'] == 0


def test_classification_boundary_and_precedence():
    from datetime import datetime, timedelta, timezone
    now=datetime.now(timezone.utc)
    row={'active':True,'analysis_available':True,'last_activity_at':now-timedelta(days=7)}
    assert onboarding.classify(row,now)=='active'
    row['last_activity_at']-=timedelta(seconds=1)
    assert onboarding.classify(row,now)=='inactive'
    row['active']=False
    assert onboarding.classify(row,now)=='account_inactive'
    row['followup_situation']='blocked'
    assert onboarding.classify(row,now)=='blocked'
