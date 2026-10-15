from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from test_credit_wallet_postgres import database
from src.inna_platform.services import sabino_support as support
from src.inna_platform.services.finance.finance_auth_routes import get_authenticated_user

H={'X-Sabino-Support':'1'}

@pytest.fixture
def setup(database,monkeypatch):
    monkeypatch.setattr(support,'cursor_postgres',database)
    monkeypatch.setenv('SABINO_ADMIN_USERS','admin')
    with database(commit_automatico=True) as cur:
        cur.execute('CREATE TABLE inna_auth_users(user_id TEXT PRIMARY KEY,email TEXT)')
        cur.execute("INSERT INTO inna_auth_users VALUES ('alice','alice@example.test'),('bob','bob@example.test'),('admin','admin@example.test')")
    support.ensure_schema()


def client(uid='alice'):
    app=FastAPI();app.include_router(support.router)
    if uid:app.dependency_overrides[get_authenticated_user]=lambda:{'user_id':uid}
    return TestClient(app)


def payload():return {'request_id':str(uuid4()),'category':'technical','subject':'Teste de atendimento','body':'Preciso de ajuda com minha conta.'}
def create(c=None,p=None):return (c or client()).post('/api/sabino/support',json=p or payload(),headers=H)


def test_scope_and_csrf(setup,monkeypatch):
    assert client(None).get('/api/sabino/support').status_code==401
    assert client().get('/admin/atendimentos').status_code==403
    assert client().get('/api/sabino/support?admin=true').status_code==403
    assert client('admin').get('/admin/atendimentos').status_code==200
    assert client(None).get('/ajuda').status_code==200
    assert client().post('/api/sabino/support',json=payload()).status_code==403
    assert client().post('/api/sabino/support',json=payload(),headers={**H,'Origin':'https://evil.test'}).status_code==403
    monkeypatch.delenv('SABINO_ADMIN_USERS')
    assert client('admin').get('/admin/atendimentos').status_code==403


def test_ownership_and_admin_messages(setup):
    tid=create().json()['id'];base='/api/sabino/support/'+tid
    assert client('bob').get(base).status_code==404
    assert client('bob').post(base+'/messages',json={'request_id':str(uuid4()),'body':'intrusion'},headers=H).status_code==404
    assert client('bob').get('/api/sabino/support').json()['total']==0
    assert client().patch(base+'/state',json={'state':'resolved'},headers=H).status_code==403
    admin=client('admin');assert admin.get('/api/sabino/support?admin=true').json()['total']==1
    assert admin.post(base+'/messages?admin=true',json={'request_id':str(uuid4()),'body':'Resposta da equipe'},headers=H).status_code==200
    data=client().get(base).json();assert data['state']=='in_progress';assert data['messages'][-1]['actor_role']=='admin'
    assert 'user_id' not in data and 'actor_id' not in data['messages'][0]
    assert admin.patch(base+'/state',json={'state':'resolved'},headers=H).status_code==200
    assert client().post(base+'/messages',json={'request_id':str(uuid4()),'body':'Mensagem'},headers=H).status_code==409
    assert admin.patch(base+'/state',json={'state':'in_progress'},headers=H).status_code==200


def test_retry_and_validation(setup):
    p=payload();tid=create(p=p).json()['id'];assert create(p=p).json()['id']==tid
    assert client().get('/api/sabino/support').json()['total']==1
    p['body']='Outro conteúdo no envio';assert create(p=p).status_code==409
    p=payload();p['user_id']='bob';assert create(p=p).status_code==422
    p=payload();p['subject']='     ';assert create(p=p).status_code==422
    p=payload();p['body']='x'*5001;assert create(p=p).status_code==422
    data={'request_id':str(uuid4()),'body':'Minha mensagem'};path='/api/sabino/support/'+tid+'/messages'
    assert client().post(path,json=data,headers=H).status_code==200
    assert client().post(path,json=data,headers=H).status_code==200
    assert client().get('/api/sabino/support/'+tid).json()['message_count']==2


def test_parallel_duplicate_and_quota(setup):
    p=payload()
    with ThreadPoolExecutor(max_workers=2) as pool:
        ids=list(pool.map(lambda _:create(p=p).json()['id'],range(2)))
    assert len(set(ids))==1
    for _ in range(9):assert create().status_code==201
    assert create().status_code==429
    assert create(p=p).status_code==201


def test_errors_are_private(setup,monkeypatch):
    def fail():raise RuntimeError('secret database value')
    monkeypatch.setattr(support,'ensure_schema',fail)
    r=client().get('/api/sabino/support');assert r.status_code==503;assert 'secret' not in r.text


def test_pagination_and_history(setup,database):
    tid=create().json()['id']
    with database(commit_automatico=True) as cur:
        for _ in range(105):cur.execute("INSERT INTO sabino_support_messages(ticket_id,actor_id,actor_role,request_id,body) VALUES (%s,'alice','customer',%s,'Teste histórico')",(tid,str(uuid4())))
    data=client().get('/api/sabino/support/'+tid).json();assert len(data['messages'])==100;assert data['message_count']==106
    before=data['messages'][0]['id'];r=client().get('/api/sabino/support/'+tid+'/messages?before='+str(before));assert len(r.json()['messages'])==6
    assert client('bob').get('/api/sabino/support/'+tid+'/messages?before='+str(before)).status_code==404
    assert client().get('/api/sabino/support').headers['cache-control']=='no-store'
