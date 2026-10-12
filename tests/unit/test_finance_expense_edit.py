from contextlib import contextmanager
from datetime import date
from decimal import Decimal
import sqlite3
import pytest
from fastapi import HTTPException
from src.inna_platform.services.finance import transaction_repository as repo
from src.inna_platform.services.finance import finance_transaction_routes as routes

@pytest.fixture
def database(monkeypatch):
    db=sqlite3.connect(':memory:')
    columns=', '.join(c+' '+('NUMERIC' if c=='amount' else 'TEXT') for c in repo._RETURNING_COLUMNS)
    db.execute(f'CREATE TABLE {repo.TRANSACTION_TABLE} ({columns})')
    for owner, ident, value in [('alice','a','10.10'),('bob','b','20.20')]:
        db.execute(f'INSERT INTO {repo.TRANSACTION_TABLE} (owner_id,transaction_id,amount,description,category,transaction_date,transaction_type,currency) VALUES (?,?,?,?,?,?,?,?)',(owner,ident,value,'Original','Alimentação','2026-10-12','Despesa','BRL'))
    class Cursor:
        def execute(self, sql, args):
            self.cursor=db.execute(sql.replace('%s','?'),tuple(str(x) if isinstance(x,(Decimal,date)) else x for x in args))
        def fetchone(self): return self.cursor.fetchone()
        @property
        def rowcount(self): return self.cursor.rowcount
    @contextmanager
    def cursor(**kwargs):
        yield Cursor()
        db.commit()
    monkeypatch.setattr(repo,'cursor_postgres',cursor)
    return db

def edit(owner='alice',ident='a',**kwargs):
    payload=dict(amount='15.35',description='Mercado',category='Alimentação',transaction_date='2026-09-30')
    payload.update(kwargs)
    return repo.update_financial_transaction(owner_id=owner,transaction_id=ident,**payload)

def test_edit_moves_month_and_preserves_other_account(database):
    assert edit()['description']=='Mercado'
    rows=database.execute(f'SELECT owner_id,amount,transaction_date FROM {repo.TRANSACTION_TABLE} ORDER BY owner_id').fetchall()
    assert rows==[('alice',15.35,'2026-09-30'),('bob',20.2,'2026-10-12')]

def test_cross_account_edit_and_delete_do_nothing(database):
    assert edit(ident='b') is None
    assert not repo.delete_financial_transaction(owner_id='alice',transaction_id='b')
    assert database.execute(f'SELECT COUNT(*) FROM {repo.TRANSACTION_TABLE}').fetchone()[0]==2

def test_delete_updates_total_and_repeat_is_not_found(database):
    assert repo.delete_financial_transaction(owner_id='alice',transaction_id='a')
    assert not repo.delete_financial_transaction(owner_id='alice',transaction_id='a')
    assert database.execute(f"SELECT COALESCE(SUM(amount),0) FROM {repo.TRANSACTION_TABLE} WHERE owner_id='alice'").fetchone()[0]==0

@pytest.mark.parametrize('amount',['NaN','Infinity','-Infinity','0','-1','1000000000000','999999999999.999','1e9999'])
def test_bad_amount_rejected(amount):
    with pytest.raises(ValueError): repo._normalize_amount(amount)

@pytest.mark.parametrize('fields',[{'description':' '},{'category':'inexistente'},{'transaction_date':'2026-02-30'}])
def test_bad_edit_rejected(database,fields):
    with pytest.raises(ValueError): edit(**fields)

def test_edit_route_uses_session_owner_and_404(database):
    payload=routes.TransactionEditRequest(amount='2.30',description='Teste',category='Alimentação',transaction_date='2026-10-12')
    result=routes.update_authenticated_transaction(payload,'a',{'user_id':'alice'})
    assert result['transaction']['owner_id']=='alice'
    with pytest.raises(HTTPException) as exc: routes.update_authenticated_transaction(payload,'b',{'user_id':'alice'})
    assert exc.value.status_code==404

def test_cent_rounding():
    assert repo._normalize_amount('10.105')==Decimal('10.11')
