"""Account-wide onboarding in Sabino's central dashboard; no benefit grants."""
import os
from collections import Counter
from datetime import timedelta
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.database.connection import cursor_postgres
from .finance.finance_auth_routes import get_authenticated_user

router = APIRouter(tags=["sabino-onboarding"])
STATIC = Path(__file__).resolve().parents[1] / "static"
STEPS = ("account_reviewed", "platforms_explored", "inna_analysis")


def identity(user):
    value = str(user.get("user_id") or "").strip()
    if not value:
        raise HTTPException(401, "Entre na sua conta.")
    return value


def is_admin(user_id):
    # Explicit central-platform administrators, not all Pix reviewers.
    return user_id in {x.strip() for x in os.getenv("SABINO_ADMIN_USERS", "").split(",") if x.strip()}


def administrator(user=Depends(get_authenticated_user)):
    user_id = identity(user)
    if not is_admin(user_id):
        raise HTTPException(403, "Acesso restrito à administração da Sabino.AI.")
    return user_id


def ensure_schema():
    with cursor_postgres(commit_automatico=True) as cur:
        cur.execute("SELECT pg_advisory_xact_lock(173025103)")
        cur.execute("""CREATE TABLE IF NOT EXISTS sabino_onboarding_steps (
            user_id TEXT NOT NULL REFERENCES inna_auth_users(user_id) ON DELETE CASCADE,
            step TEXT NOT NULL CHECK(step IN ('account_reviewed','platforms_explored')),
            completed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            PRIMARY KEY(user_id,step)
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS sabino_participant_followups (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES inna_auth_users(user_id) ON DELETE CASCADE,
            admin_id TEXT NOT NULL REFERENCES inna_auth_users(user_id),
            situation TEXT NOT NULL CHECK(situation IN ('normal','help','withdrawn','blocked')),
            reason TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )""")
        cur.execute("CREATE INDEX IF NOT EXISTS sabino_followups_latest ON sabino_participant_followups(user_id,id DESC)")


def progress(cur, user_ids):
    result = {uid: {} for uid in user_ids}
    if not user_ids:
        return result
    cur.execute("SELECT user_id,step,completed_at FROM sabino_onboarding_steps WHERE user_id=ANY(%s)", (user_ids,))
    for row in cur.fetchall():
        result[row["user_id"]][row["step"]] = row["completed_at"]
    # Older deployments can lack the analysis migration. Unknown is not unused.
    cur.execute("SELECT to_regclass('inna_paid_analyses') AS relation")
    available = cur.fetchone()["relation"] is not None
    if available:
        cur.execute("""SELECT user_id,MIN(updated_at) AS completed_at FROM inna_paid_analyses
            WHERE user_id=ANY(%s) AND state='completed' GROUP BY user_id""", (user_ids,))
        for row in cur.fetchall():
            result[row["user_id"]]["inna_analysis"] = row["completed_at"]
    return {uid: summarize(done, available) for uid, done in result.items()}


def summarize(done, analysis_available):
    completed = len(done)
    return {"steps": [{"id": step, "completed": step in done,
                        "completed_at": done.get(step),
                        "source": "system" if step == "inna_analysis" else "user_confirmation"}
                       for step in STEPS],
            "completed": completed, "total": len(STEPS),
            "next_step": next((step for step in STEPS if step not in done), None),
            "analysis_available": analysis_available,
            "last_progress_at": max(done.values()) if done else None,
            "status": "completed" if completed == len(STEPS) else
                      "unknown" if not analysis_available else "not_started" if completed == 0 else "in_progress"}


@router.get("/api/sabino/onboarding")
def own_progress(response: Response, user=Depends(get_authenticated_user)):
    response.headers["Cache-Control"] = "no-store"
    user_id = identity(user)
    try:
        ensure_schema()
        with cursor_postgres(dict_cursor=True) as cur:
            return {**progress(cur, [user_id])[user_id], "is_admin": is_admin(user_id)}
    except Exception:
        raise HTTPException(503, "Não foi possível carregar seus primeiros passos.") from None


class Completion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    step: Literal["account_reviewed", "platforms_explored"]


@router.post("/api/sabino/onboarding")
def complete_step(body: Completion, request: Request, response: Response, user=Depends(get_authenticated_user)):
    response.headers["Cache-Control"] = "no-store"
    user_id = identity(user)
    origin = request.headers.get("origin")
    if (request.headers.get("X-Sabino-Onboarding") != "1"
            or request.headers.get("sec-fetch-site") == "cross-site"
            or (origin and origin != str(request.base_url).rstrip("/"))):
        raise HTTPException(403, "Origem inválida.")
    try:
        ensure_schema()
        with cursor_postgres(commit_automatico=True) as cur:
            cur.execute("""INSERT INTO sabino_onboarding_steps(user_id,step) VALUES (%s,%s)
                ON CONFLICT(user_id,step) DO NOTHING""", (user_id, body.step))
        return {"saved": True}
    except Exception:
        raise HTTPException(503, "Não foi possível salvar. Tente novamente.") from None


@router.get("/admin/primeiros-passos", include_in_schema=False)
def admin_page(admin=Depends(administrator)):
    return FileResponse(STATIC / "sabino-admin-onboarding.html", headers={"Cache-Control": "no-store"})


SITUATIONS = ('active', 'not_started', 'inactive', 'help', 'withdrawn', 'blocked', 'account_inactive', 'unknown')


def classify(row, now):
    if row.get('followup_situation') in ('help', 'withdrawn', 'blocked'):
        return row['followup_situation']
    if not row['active']:
        return 'account_inactive'
    if not row['analysis_available']:
        return 'unknown'
    last = row.get('last_activity_at')
    if last is None:
        return 'not_started'
    return 'active' if last >= now - timedelta(days=7) else 'inactive'


def participant_report(cur):
    cur.execute("SELECT to_regclass('inna_finance_pilot_enrollments') AS relation")
    if cur.fetchone()['relation'] is None:
        return [], None, False
    cur.execute('SELECT NOW() AS now')
    now = cur.fetchone()['now']
    cur.execute("""SELECT p.user_id,u.email,u.active,p.started_at,p.expires_at
        FROM inna_finance_pilot_enrollments p JOIN inna_auth_users u USING(user_id)
        ORDER BY p.started_at DESC,p.user_id""")
    rows = [dict(row) for row in cur.fetchall()]
    ids = [row['user_id'] for row in rows]
    states = progress(cur, ids)
    latest = {}
    if ids:
        cur.execute("""SELECT DISTINCT ON(user_id) user_id,situation,reason,note,created_at,admin_id
            FROM sabino_participant_followups WHERE user_id=ANY(%s)
            ORDER BY user_id,id DESC""", (ids,))
        latest = {row['user_id']: dict(row) for row in cur.fetchall()}
    activity = {}
    if ids and states[ids[0]]['analysis_available']:
        cur.execute("""SELECT user_id,MAX(updated_at) AS last_activity_at FROM inna_paid_analyses
            WHERE user_id=ANY(%s) AND state='completed' GROUP BY user_id""", (ids,))
        activity = {row['user_id']: row['last_activity_at'] for row in cur.fetchall()}
    converted = set()
    cur.execute("SELECT to_regclass('inna_user_platform_entitlements') AS relation")
    if ids and cur.fetchone()['relation'] is not None:
        cur.execute("""SELECT user_id FROM inna_user_platform_entitlements WHERE user_id=ANY(%s)
            AND platform_code='financeiro' AND plan_code<>'piloto_30_dias' AND status='active'
            AND (expires_at IS NULL OR expires_at>NOW())""", (ids,))
        converted = {row['user_id'] for row in cur.fetchall()}
    for row in rows:
        uid = row['user_id']
        row.update(states[uid])
        followup = latest.get(uid)
        row['followup'] = followup
        row['followup_situation'] = followup['situation'] if followup else 'normal'
        times = [t for t in (row['last_progress_at'], activity.get(uid)) if t is not None]
        row['last_activity_at'] = max(times) if times else None
        row['situation'] = classify(row, now)
        row['has_paid_plan'] = uid in converted
    return rows, now, True


@router.get("/api/sabino/admin/onboarding")
def admin_progress(response: Response, admin=Depends(administrator),
                   offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100),
                   situation: str = Query('all'), search: str = Query('', max_length=254)):
    response.headers["Cache-Control"] = "no-store"
    if situation not in ('all', *SITUATIONS):
        raise HTTPException(422, 'Situação inválida.')
    try:
        ensure_schema()
        with cursor_postgres(dict_cursor=True) as cur:
            # All summary queries share one database snapshot.
            cur.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
            rows, now, available = participant_report(cur)
        counts = Counter(row['situation'] for row in rows)
        reasons = Counter(row['followup']['reason'] for row in rows
                          if row['followup_situation'] != 'normal')
        summary = {'total': len(rows), 'situations': {key: counts[key] for key in SITUATIONS},
                   'reasons': dict(reasons), 'completed': sum(row['completed'] == 3 for row in rows),
                   'paid_plan': sum(row['has_paid_plan'] for row in rows), 'as_of': now}
        filtered = [row for row in rows if (situation == 'all' or row['situation'] == situation)
                    and search.strip().casefold() in (row['email'] or '').casefold()]
        return {'participants': filtered[offset:offset+limit], 'total': len(filtered),
                'offset': offset, 'pilot_available': available, 'summary': summary}
    except Exception:
        raise HTTPException(503, "Não foi possível consultar o acompanhamento.") from None


class Followup(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    user_id: str = Field(min_length=1, max_length=200)
    situation: Literal['normal', 'help', 'withdrawn', 'blocked']
    reason: Literal['resolved', 'difficulty', 'technical', 'time', 'price', 'access', 'other']
    note: str = Field(default='', max_length=1000)

    @model_validator(mode='after')
    def meaningful_reason(self):
        if (self.situation == 'normal') != (self.reason == 'resolved'):
            raise ValueError('Use acompanhamento resolvido apenas ao retornar à situação automática.')
        if self.situation in ('withdrawn', 'blocked') or self.reason == 'other':
            if len(self.note) < 5:
                raise ValueError('Registre o contexto da confirmação ou do impedimento.')
        return self


@router.post('/api/sabino/admin/onboarding/followup')
def save_followup(body: Followup, request: Request, response: Response, admin=Depends(administrator)):
    response.headers['Cache-Control'] = 'no-store'
    origin = request.headers.get('origin')
    if (request.headers.get('X-Sabino-Onboarding') != '1'
            or request.headers.get('sec-fetch-site') == 'cross-site'
            or (origin and origin != str(request.base_url).rstrip('/'))):
        raise HTTPException(403, 'Origem inválida.')
    try:
        ensure_schema()
        with cursor_postgres(commit_automatico=True) as cur:
            cur.execute('SELECT user_id FROM inna_finance_pilot_enrollments WHERE user_id=%s FOR UPDATE', (body.user_id,))
            if not cur.fetchone():
                raise HTTPException(404, 'Participante não encontrado.')
            cur.execute('''INSERT INTO sabino_participant_followups(user_id,admin_id,situation,reason,note)
                VALUES (%s,%s,%s,%s,%s)''', (body.user_id, admin, body.situation, body.reason, body.note))
        return {'saved': True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, 'Não foi possível salvar o acompanhamento.') from None
