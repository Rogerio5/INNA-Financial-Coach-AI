import asyncio
import os
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from test_credit_wallet_postgres import database, parallel
from src.inna_platform.services.finance import credit_wallet as wallet
from src.inna_platform.services.finance import paid_analysis as service
from src.inna_platform.services.finance import paid_analysis_routes as routes
from src.inna_platform.services.finance.finance_auth_routes import get_authenticated_user

PAYLOAD = {'pergunta': 'Como organizar um orçamento?', 'idioma': 'pt-BR', 'top_k': 4}
HEADERS = {'X-Sabino-Analysis': 'confirmed'}


@pytest.fixture
def paid(database, monkeypatch):
    with database(commit_automatico=True) as cur:
        cur.execute((Path(__file__).resolve().parents[3] / 'migrations/20260927_005_paid_analysis.sql').read_text())
    monkeypatch.setattr(service, 'configuration', lambda: {'enabled': True, 'cost': 5})
    wallet.start('alice', 'funds', 100, kind='grant', source='purchased')
    return service


def client(identity='alice'):
    app = FastAPI(); app.include_router(routes.router)
    if identity:
        app.dependency_overrides[get_authenticated_user] = lambda: {'user_id': identity}
    return TestClient(app)


def make_quote():
    return service.quote('alice', uuid4(), PAYLOAD)['quote_id']


def test_success_and_cached_replay_charge_once(paid):
    quote_id = make_quote(); calls = []
    async def worker(payload):
        calls.append(payload); return {'resposta': 'Uma resposta útil.', 'fontes': []}
    first = asyncio.run(service.execute('alice', quote_id, PAYLOAD, worker))
    second = asyncio.run(service.execute('alice', quote_id, PAYLOAD, worker))
    assert first['result'] == second['result']
    assert len(calls) == 1
    assert wallet.snapshot('alice')['balance'] == 95
    assert service.get('alice', quote_id)['state'] == 'completed'


@pytest.mark.parametrize('error', [httpx.ConnectError('offline'), ValueError('invalid answer')])
def test_confirmed_failure_refunds_once(paid, error):
    quote_id = make_quote()
    async def worker(payload): raise error
    assert asyncio.run(service.execute('alice', quote_id, PAYLOAD, worker))['state'] == 'refunded'
    assert asyncio.run(service.execute('alice', quote_id, PAYLOAD, worker))['state'] == 'refunded'
    assert wallet.snapshot('alice')['balance'] == 100


def test_timeout_never_reruns_or_silently_refunds(paid):
    quote_id = make_quote(); calls = []
    async def worker(payload): calls.append(1); raise httpx.ReadTimeout('uncertain')
    with pytest.raises(httpx.ReadTimeout): asyncio.run(service.execute('alice', quote_id, PAYLOAD, worker))
    assert asyncio.run(service.execute('alice', quote_id, PAYLOAD, worker))['state'] == 'needs_review'
    assert calls == [1]
    assert wallet.snapshot('alice')['balance'] == 95


def test_concurrent_claim_is_atomic(paid):
    quote_id = make_quote()
    results = parallel(lambda: service.claim('alice', quote_id, PAYLOAD), lambda: service.claim('alice', quote_id, PAYLOAD))
    assert sum(started for row, started in results) == 1
    assert wallet.snapshot('alice')['balance'] == 95


def test_other_user_and_changed_question_cannot_execute(paid):
    quote_id = make_quote()
    with pytest.raises(LookupError): service.claim('bob', quote_id, PAYLOAD)
    with pytest.raises(wallet.CreditConflict): service.claim('alice', quote_id, {**PAYLOAD, 'pergunta':'Outra pergunta'})
    with pytest.raises(LookupError): service.get('bob', quote_id)
    assert wallet.snapshot('alice')['balance'] == 100


def test_quote_replay_payload_binding_and_no_debit(paid):
    key = uuid4()
    first = service.quote('alice', key, PAYLOAD)
    assert service.quote('alice', key, PAYLOAD) == first
    with pytest.raises(wallet.CreditConflict): service.quote('alice', key, {**PAYLOAD,'top_k':3})
    assert wallet.snapshot('alice')['balance'] == 100


def test_insufficient_balance_and_expired_quote(paid, database):
    q = service.quote('bob', uuid4(), PAYLOAD)['quote_id']
    with pytest.raises(wallet.InsufficientCredits): service.claim('bob', q, PAYLOAD)
    q = make_quote()
    with database(commit_automatico=True) as cur:
        cur.execute("UPDATE inna_paid_analyses SET created_at=NOW()-INTERVAL '1 hour' WHERE quote_id=%s", (q,))
    with pytest.raises(wallet.CreditConflict): service.claim('alice', q, PAYLOAD)
    assert wallet.snapshot('alice')['balance'] == 100


def test_http_auth_csrf_identity_and_cached_result(paid, monkeypatch):
    c = client()
    body = {**PAYLOAD, 'request_id':str(uuid4())}
    assert client(None).post('/api/inna/quote',json=body,headers=HEADERS).status_code == 401
    assert c.post('/api/inna/quote',json=body).status_code == 403
    assert c.post('/api/inna/quote',json=body,headers={**HEADERS,'Origin':'https://evil.example'}).status_code == 403
    for field in ('cost','user_id'):
        assert c.post('/api/inna/quote',json={**body, field:1},headers=HEADERS).status_code == 422
    q = c.post('/api/inna/quote',json=body,headers=HEADERS).json()['quote_id']
    async def worker(payload): return {'resposta':'Resposta em cache'}
    monkeypatch.setattr(service,'backend',worker)
    result = c.post('/api/inna/ask',json={**PAYLOAD,'quote_id':q},headers=HEADERS)
    assert result.status_code == 200
    assert result.headers['cache-control'] == 'no-store'
    assert c.get('/api/inna/analyses/'+q).json()['resposta'] == 'Resposta em cache'
    assert client('bob').get('/api/inna/analyses/'+q).status_code == 404
    assert c.get('/api/inna/analyses').json()['analyses'][0]['state'] == 'completed'


def test_finalization_failure_rolls_back_all(paid, database):
    q = make_quote(); service.claim('alice', q, PAYLOAD)
    with database(commit_automatico=True) as cur:
        cur.execute("ALTER TABLE inna_paid_analyses ADD CONSTRAINT test_no_complete CHECK(state <> 'completed')")
    with pytest.raises(Exception): service.finalize('alice', q, result={'resposta':'ok'})
    assert service.get('alice', q)['state'] == 'running'
    assert wallet.snapshot('alice')['balance'] == 95
    assert [e['event'] for e in wallet.snapshot('alice')['history']] == ['reserve','grant']


def test_manual_reconciliation_authorized_audited_once(paid, database):
    q = make_quote(); service.claim('alice', q, PAYLOAD)
    service.finalize('alice', q, uncertain=True)
    with database(commit_automatico=True) as cur:
        cur.execute('CREATE TABLE inna_auth_users(user_id TEXT PRIMARY KEY, active BOOLEAN)')
        cur.execute('CREATE TABLE inna_pix_reviewers(user_id TEXT PRIMARY KEY)')
        cur.execute("INSERT INTO inna_auth_users VALUES ('admin',TRUE)")
        cur.execute("INSERT INTO inna_pix_reviewers VALUES ('admin')")
    review = {'reviewer_id':'outsider','reason':'Falha confirmada pelos registros','evidence_ref':'trace:test'}
    with pytest.raises(PermissionError): service.finalize('alice',q,review=review)
    assert wallet.snapshot('alice')['balance'] == 95
    review['reviewer_id'] = 'admin'
    assert service.finalize('alice',q,review=review)['state'] == 'refunded'
    with pytest.raises(wallet.CreditConflict): service.finalize('alice',q,review=review)
    assert wallet.snapshot('alice')['balance'] == 100
    with database() as cur:
        cur.execute('SELECT COUNT(*) FROM inna_paid_analysis_reviews'); assert cur.fetchone()[0] == 1


def test_changed_price_disabled_and_missing_quote_are_safe(paid, monkeypatch):
    q = make_quote()
    monkeypatch.setattr(service,'configuration',lambda:{'enabled':True,'cost':10})
    with pytest.raises(wallet.CreditConflict): service.claim('alice',q,PAYLOAD)
    monkeypatch.setattr(service,'configuration',lambda:{'enabled':False,'cost':5})
    with pytest.raises(RuntimeError): service.claim('alice',q,PAYLOAD)
    assert client().post('/api/inna/ask',json=PAYLOAD,headers=HEADERS).status_code == 422
    assert wallet.snapshot('alice')['balance'] == 100


@pytest.mark.parametrize('response', [{'resposta':''}, {'resposta':'fallback','fallback':True}, {'resposta':'erro','ok':False}, {'error':'bad','resposta':'bad'}])
def test_invalid_backend_response_refunds(paid, monkeypatch, response):
    real_client = httpx.AsyncClient
    transport = httpx.MockTransport(lambda request:httpx.Response(200,json=response))
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kwargs:real_client(transport=transport,**kwargs))
    q = make_quote()
    assert asyncio.run(service.execute('alice',q,PAYLOAD))['state'] == 'refunded'
    assert wallet.snapshot('alice')['balance'] == 100


def test_live_paid_analysis_isolated_wallet(paid):
    if os.getenv('INNA_RUN_LIVE_CREDIT_TEST') != 'true':
        pytest.skip('Enable LiveInna to call the real local INNA with an isolated wallet')
    q = make_quote()
    result = client().post('/api/inna/ask', json={**PAYLOAD,'quote_id':q}, headers=HEADERS)
    assert result.status_code == 200, result.text
    assert result.json()['resposta'].strip()
    assert result.json()['billing']['state'] == 'completed'
    assert wallet.snapshot('alice')['balance'] == 95
    cached = client().get('/api/inna/analyses/'+q)
    assert cached.json()['resposta'] == result.json()['resposta']
    assert wallet.snapshot('alice')['balance'] == 95
