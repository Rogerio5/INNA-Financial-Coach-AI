"""Native support: authenticated ownership, explicit administration, immutable messages."""
from contextlib import contextmanager
from pathlib import Path
from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field

from src.database.connection import cursor_postgres
from .finance.finance_auth_routes import get_authenticated_user
from .sabino_onboarding import identity, is_admin, administrator

router = APIRouter(tags=['sabino-support'])
STATIC = Path(__file__).resolve().parents[1] / 'static'
State = Literal['new', 'in_progress', 'resolved']
Category = Literal['technical', 'access', 'question', 'suggestion']


def ensure_schema():
    with cursor_postgres(commit_automatico=True) as cur:
        cur.execute('SELECT pg_advisory_xact_lock(173025104)')
        cur.execute('''CREATE TABLE IF NOT EXISTS sabino_support_tickets (
            id UUID PRIMARY KEY, user_id TEXT NOT NULL REFERENCES inna_auth_users(user_id),
            request_id UUID NOT NULL, category TEXT NOT NULL,
            subject TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'new'
            CHECK(state IN ('new','in_progress','resolved')),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), UNIQUE(user_id,request_id))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS sabino_support_messages (
            id BIGSERIAL PRIMARY KEY, ticket_id UUID NOT NULL REFERENCES sabino_support_tickets(id),
            actor_id TEXT NOT NULL REFERENCES inna_auth_users(user_id),
            actor_role TEXT NOT NULL CHECK(actor_role IN ('customer','admin')),
            request_id UUID NOT NULL, body TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), UNIQUE(actor_id,request_id))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS sabino_support_events (
            id BIGSERIAL PRIMARY KEY, ticket_id UUID NOT NULL REFERENCES sabino_support_tickets(id),
            actor_id TEXT NOT NULL REFERENCES inna_auth_users(user_id),
            state TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())''')
        cur.execute('CREATE INDEX IF NOT EXISTS sabino_support_owner ON sabino_support_tickets(user_id,updated_at DESC)')
        cur.execute('CREATE INDEX IF NOT EXISTS sabino_support_recent ON sabino_support_tickets(updated_at DESC)')
        cur.execute('CREATE INDEX IF NOT EXISTS sabino_support_thread ON sabino_support_messages(ticket_id,id)')


@contextmanager
def transaction():
    try:
        ensure_schema()
        with cursor_postgres(dict_cursor=True, commit_automatico=True) as cur:
            yield cur
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, 'Não foi possível acessar o suporte. Tente novamente.') from None


def guard(request: Request, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    if request.method != 'GET':
        origin = request.headers.get('origin')
        if (request.headers.get('X-Sabino-Support') != '1'
                or request.headers.get('sec-fetch-site') == 'cross-site'
                or (origin and origin != str(request.base_url).rstrip('/'))):
            raise HTTPException(403, 'Origem inválida.')


router.dependencies.append(Depends(guard))


class TicketInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    request_id: UUID
    category: Category
    subject: str = Field(min_length=5, max_length=120)
    body: str = Field(min_length=10, max_length=5000)


class MessageInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    request_id: UUID
    body: str = Field(min_length=1, max_length=5000)


class StateInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    state: State


def scope(user, admin):
    uid = identity(user)
    if admin and not is_admin(uid):
        raise HTTPException(403, 'Acesso restrito à administração.')
    return uid


def owned(cur, ticket_id, uid, admin, lock=False):
    cur.execute('SELECT * FROM sabino_support_tickets WHERE id=%s' + (' FOR UPDATE' if lock else ''), (str(ticket_id),))
    row = cur.fetchone()
    if not row or (not admin and row['user_id'] != uid):
        raise HTTPException(404, 'Chamado não encontrado.')
    return row


def public_ticket(row):
    return {k: str(v) if k == 'id' else v for k, v in dict(row).items() if k not in ('request_id', 'user_id')}


def actor_lock(cur, uid):
    cur.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,173025105))', (uid,))


@router.get('/suporte', include_in_schema=False)
def customer_page(user=Depends(get_authenticated_user)):
    return FileResponse(STATIC / 'sabino-support.html', headers={'Cache-Control':'no-store'})


@router.get('/admin/atendimentos', include_in_schema=False)
def admin_page(admin=Depends(administrator)):
    return FileResponse(STATIC / 'sabino-support.html', headers={'Cache-Control':'no-store'})


@router.get('/api/sabino/support')
def tickets(admin: bool = False, state: State | None = None,
            offset: int = Query(0, ge=0), user=Depends(get_authenticated_user)):
    uid = scope(user, admin)
    with transaction() as cur:
        where = 'TRUE' if admin else 't.user_id=%s'
        args = [] if admin else [uid]
        if state:
            where += ' AND t.state=%s'
            args.append(state)
        cur.execute('SELECT COUNT(*) AS total FROM sabino_support_tickets t WHERE ' + where, args)
        total = cur.fetchone()['total']
        cur.execute('''SELECT t.id,t.category,t.subject,t.state,t.created_at,t.updated_at,u.email
            FROM sabino_support_tickets t JOIN inna_auth_users u ON u.user_id=t.user_id
            WHERE ''' + where + ' ORDER BY t.updated_at DESC,t.id LIMIT 25 OFFSET %s', [*args, offset])
        rows = [public_ticket(r) for r in cur.fetchall()]
        if not admin:
            for row in rows:
                row.pop('email', None)
        return {'tickets':rows, 'total':total, 'is_admin':is_admin(uid)}


@router.post('/api/sabino/support', status_code=201)
def create(body: TicketInput, user=Depends(get_authenticated_user)):
    uid = identity(user)
    with transaction() as cur:
        actor_lock(cur, uid)
        cur.execute('SELECT * FROM sabino_support_tickets WHERE user_id=%s AND request_id=%s', (uid,str(body.request_id)))
        old = cur.fetchone()
        if old:
            cur.execute('SELECT body FROM sabino_support_messages WHERE ticket_id=%s ORDER BY id LIMIT 1', (str(old['id']),))
            if old['subject'] != body.subject or old['category'] != body.category or cur.fetchone()['body'] != body.body:
                raise HTTPException(409, 'O envio anterior tinha outro conteúdo. Atualize a página antes de enviar novamente.')
            return public_ticket(old)
        cur.execute("SELECT COUNT(*) AS n FROM sabino_support_tickets WHERE user_id=%s AND created_at>NOW()-INTERVAL '1 day'", (uid,))
        if cur.fetchone()['n'] >= 10:
            raise HTTPException(429, 'Limite de 10 novos chamados por dia. Acompanhe seus chamados existentes.')
        tid = str(uuid4())
        cur.execute('INSERT INTO sabino_support_tickets(id,user_id,request_id,category,subject) VALUES (%s,%s,%s,%s,%s) RETURNING *',
                    (tid,uid,str(body.request_id),body.category,body.subject))
        row = public_ticket(cur.fetchone())
        cur.execute("INSERT INTO sabino_support_messages(ticket_id,actor_id,actor_role,request_id,body) VALUES (%s,%s,'customer',%s,%s)",
                    (tid,uid,str(body.request_id),body.body))
        return row


@router.get('/api/sabino/support/{ticket_id}')
def detail(ticket_id: UUID, admin: bool = False, user=Depends(get_authenticated_user)):
    uid = scope(user, admin)
    with transaction() as cur:
        row = public_ticket(owned(cur,ticket_id,uid,admin))
        # Bound every thread response; older messages can be requested through pagination.
        cur.execute('SELECT COUNT(*) AS n FROM sabino_support_messages WHERE ticket_id=%s', (str(ticket_id),))
        row['message_count'] = cur.fetchone()['n']
        cur.execute('SELECT id,actor_role,body,created_at FROM sabino_support_messages WHERE ticket_id=%s ORDER BY id DESC LIMIT 100', (str(ticket_id),))
        row['messages'] = list(reversed([dict(r) for r in cur.fetchall()]))
        return row


@router.get('/api/sabino/support/{ticket_id}/messages')
def older(ticket_id: UUID, before: int = Query(..., gt=0), admin: bool = False, user=Depends(get_authenticated_user)):
    uid = scope(user,admin)
    with transaction() as cur:
        owned(cur,ticket_id,uid,admin)
        cur.execute('SELECT id,actor_role,body,created_at FROM sabino_support_messages WHERE ticket_id=%s AND id<%s ORDER BY id DESC LIMIT 100', (str(ticket_id),before))
        return {'messages':list(reversed([dict(r) for r in cur.fetchall()]))}


@router.post('/api/sabino/support/{ticket_id}/messages')
def reply(ticket_id: UUID, body: MessageInput, admin: bool = False, user=Depends(get_authenticated_user)):
    uid = scope(user, admin)
    with transaction() as cur:
        actor_lock(cur, uid)
        row = owned(cur,ticket_id,uid,admin,lock=True)
        cur.execute('SELECT ticket_id,body FROM sabino_support_messages WHERE actor_id=%s AND request_id=%s', (uid,str(body.request_id)))
        old = cur.fetchone()
        if old:
            if str(old['ticket_id']) != str(ticket_id) or old['body'] != body.body:
                raise HTTPException(409, 'Este envio já foi usado com outro conteúdo.')
            return {'saved':True}
        if row['state'] == 'resolved':
            raise HTTPException(409, 'O chamado está resolvido. A administração precisa reabri-lo para receber novas mensagens.')
        cur.execute("SELECT COUNT(*) AS n FROM sabino_support_messages WHERE actor_id=%s AND created_at>NOW()-INTERVAL '1 hour'", (uid,))
        if cur.fetchone()['n'] >= 60:
            raise HTTPException(429, 'Muitas mensagens. Aguarde antes de enviar novamente.')
        cur.execute('INSERT INTO sabino_support_messages(ticket_id,actor_id,actor_role,request_id,body) VALUES (%s,%s,%s,%s,%s)',
                    (str(ticket_id),uid,'admin' if admin else 'customer',str(body.request_id),body.body))
        cur.execute("UPDATE sabino_support_tickets SET updated_at=NOW(),state=CASE WHEN %s THEN 'in_progress' ELSE state END WHERE id=%s", (admin,str(ticket_id)))
        return {'saved':True}


@router.patch('/api/sabino/support/{ticket_id}/state')
def change_state(ticket_id: UUID, body: StateInput, uid=Depends(administrator)):
    with transaction() as cur:
        owned(cur,ticket_id,uid,True,lock=True)
        cur.execute('UPDATE sabino_support_tickets SET state=%s,updated_at=NOW() WHERE id=%s', (body.state,str(ticket_id)))
        cur.execute('INSERT INTO sabino_support_events(ticket_id,actor_id,state) VALUES (%s,%s,%s)', (str(ticket_id),uid,body.state))
        return {'saved':True}

@router.get('/ajuda', include_in_schema=False)
def help_page():
    return FileResponse(STATIC / 'sabino-support-help.html', headers={'Cache-Control':'no-store'})
