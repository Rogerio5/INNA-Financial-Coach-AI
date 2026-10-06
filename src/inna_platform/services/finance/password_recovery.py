"""Email recovery: hashed single-use tokens; atomic password/session revocation."""
import hashlib
import logging
import os
import re
import secrets
from urllib.parse import urlsplit
from email.utils import parseaddr
from pathlib import Path

import requests
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field
from .finance_identity import cursor_postgres, hash_password, normalize_email, ensure_identity_schema

router = APIRouter()
logger = logging.getLogger(__name__)
MESSAGE = 'Se o e-mail estiver cadastrado, você receberá um link válido por 20 minutos. Confira também o spam.'


def public_origin():
    origin = os.getenv('SABINO_PUBLIC_URL', 'https://sabino-ai-plataforma-inna.onrender.com').rstrip('/')
    parsed = urlsplit(origin)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise RuntimeError('Recovery origin configuration unavailable')
    return origin


def settings():
    provider = os.getenv('RECOVERY_EMAIL_PROVIDER', 'resend').strip().lower()
    if provider not in {'resend', 'brevo'}:
        raise RuntimeError('Unsupported recovery email provider')
    key = os.getenv('RESEND_API_KEY' if provider == 'resend' else 'BREVO_API_KEY', '').strip()
    sender = os.getenv('EMAIL_FROM', '').strip()
    origin = public_origin()
    if not key or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', parseaddr(sender)[1]) or '\n' in sender or '\r' in sender:
        raise RuntimeError('Recovery email configuration unavailable')
    return provider, key, sender, origin


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def ensure_schema():
    ensure_identity_schema()
    with cursor_postgres(commit_automatico=True) as cur:
        cur.execute('''CREATE TABLE IF NOT EXISTS inna_password_resets (
            token_hash TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES inna_auth_users(user_id) ON DELETE CASCADE,
            expires_at TIMESTAMPTZ NOT NULL,
            used_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_inna_resets_user ON inna_password_resets(user_id)')
        cur.execute('''CREATE TABLE IF NOT EXISTS inna_password_reset_limits (
            bucket TEXT PRIMARY KEY, started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            attempts INTEGER NOT NULL DEFAULT 1)''')


def allow(bucket, maximum):
    """Atomic fixed-hour limit shared across workers and restarts."""
    with cursor_postgres(dict_cursor=True, commit_automatico=True) as cur:
        cur.execute('''INSERT INTO inna_password_reset_limits(bucket) VALUES (%s)
            ON CONFLICT(bucket) DO UPDATE SET
              attempts=CASE WHEN inna_password_reset_limits.started_at < NOW()-INTERVAL '1 hour' THEN 1 ELSE inna_password_reset_limits.attempts+1 END,
              started_at=CASE WHEN inna_password_reset_limits.started_at < NOW()-INTERVAL '1 hour' THEN NOW() ELSE inna_password_reset_limits.started_at END
            RETURNING attempts''', (bucket,))
        return cur.fetchone()['attempts'] <= maximum


def deliver(email):
    token = secrets.token_urlsafe(32)
    token_hash = digest(token)
    try:
        provider, key, sender, origin = settings()
        with cursor_postgres(dict_cursor=True, commit_automatico=True) as cur:
            cur.execute('SELECT user_id, email FROM inna_auth_users WHERE email=%s AND active=TRUE', (email,))
            user = cur.fetchone()
            if not user:
                return
            cur.execute("DELETE FROM inna_password_resets WHERE expires_at < NOW()-INTERVAL '1 day'")
            cur.execute("INSERT INTO inna_password_resets(token_hash,user_id,expires_at) VALUES (%s,%s,NOW()+INTERVAL '20 minutes')", (token_hash, user['user_id']))
        # Fragment keeps the bearer token out of HTTP access logs and referrers.
        link = origin + '/recuperar-senha#token=' + token
        subject = 'Redefina sua senha — Sabino.AI'
        message = 'Recebemos um pedido para redefinir sua senha na Sabino.AI.\n\nAbra este link em até 20 minutos:\n' + link + '\n\nEle funciona uma única vez. Se não foi você, ignore esta mensagem; sua senha não mudou. Nunca compartilhe este link.'
        if provider == 'brevo':
            name, address = parseaddr(sender)
            result = requests.post('https://api.brevo.com/v3/smtp/email',
                headers={'api-key': key, 'Content-Type': 'application/json'},
                json={'sender': {'name': name or 'Sabino.AI', 'email': address},
                      'to': [{'email': user['email']}], 'subject': subject, 'textContent': message}, timeout=20)
        else:
            result = requests.post('https://api.resend.com/emails',
                headers={'Authorization': 'Bearer ' + key, 'Content-Type':'application/json'},
                json={'from':sender, 'to':[user['email']], 'subject':subject, 'text':message}, timeout=20)
        result.raise_for_status()
    except Exception as exc:
        # No email, token, provider body or credentials in logs.
        logger.error('Password recovery delivery failed: %s', type(exc).__name__)
        try:
            with cursor_postgres(commit_automatico=True) as cur:
                cur.execute('DELETE FROM inna_password_resets WHERE token_hash=%s', (token_hash,))
        except Exception:
            logger.error('Password recovery token cleanup failed')


def change_password(token, password):
    if not re.fullmatch(r'[A-Za-z0-9_-]{43}', token):
        raise ValueError('Link inválido ou expirado. Solicite outro link.')
    with cursor_postgres(dict_cursor=True, commit_automatico=True) as cur:
        cur.execute('''SELECT user_id FROM inna_password_resets
            WHERE token_hash=%s AND used_at IS NULL AND expires_at>NOW()''', (digest(token),))
        reset = cur.fetchone()
        if not reset:
            raise ValueError('Link inválido ou expirado. Solicite outro link.')
        cur.execute('SELECT user_id FROM inna_auth_users WHERE user_id=%s AND active=TRUE FOR UPDATE', (reset['user_id'],))
        if not cur.fetchone():
            raise ValueError('Link inválido ou expirado. Solicite outro link.')
        cur.execute('''UPDATE inna_password_resets SET used_at=NOW()
            WHERE token_hash=%s AND used_at IS NULL AND expires_at>NOW() RETURNING user_id''', (digest(token),))
        if not cur.fetchone():
            raise ValueError('Link inválido ou expirado. Solicite outro link.')
        salt, hashed = hash_password(password)
        cur.execute('UPDATE inna_auth_users SET password_salt=%s,password_hash=%s,updated_at=NOW() WHERE user_id=%s', (salt, hashed, reset['user_id']))
        cur.execute('UPDATE inna_password_resets SET used_at=NOW() WHERE user_id=%s AND used_at IS NULL', (reset['user_id'],))
        cur.execute('UPDATE inna_auth_sessions SET revoked_at=NOW() WHERE user_id=%s AND revoked_at IS NULL', (reset['user_id'],))


class RecoveryRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: str = Field(min_length=3, max_length=254)


class ResetRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    token: str = Field(min_length=43, max_length=43)
    password: str = Field(min_length=10, max_length=128)


def protect(request):
    origin = public_origin()
    if request.headers.get('origin') != origin or request.headers.get('X-Sabino-Recovery') != '1':
        raise HTTPException(403, 'Origem inválida.')


@router.post('/auth/password/forgot', status_code=202)
def forgot(body: RecoveryRequest, request: Request, background: BackgroundTasks):
    try:
        protect(request)
        settings()
        email = normalize_email(body.email)
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            raise ValueError('Informe um e-mail válido.')
        ensure_schema()
        # Global limit also protects deployments behind a shared reverse proxy.
        if allow('request:global', 100) and allow('email:' + digest(email), 3):
            background.add_task(deliver, email)
        return {'message': MESSAGE}
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(400, 'Informe um e-mail válido.') from None
    except Exception:
        raise HTTPException(503, 'Recuperação temporariamente indisponível. Tente novamente mais tarde.') from None


@router.post('/auth/password/reset')
def reset(body: ResetRequest, request: Request):
    try:
        protect(request)
        ensure_schema()
        if not allow('reset:global', 100):
            raise HTTPException(429, 'Muitas tentativas. Tente novamente mais tarde.')
        change_password(body.token, body.password)
        return {'message':'Senha alterada. Entre novamente com sua nova senha.'}
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
    except Exception:
        raise HTTPException(503, 'Não foi possível alterar a senha agora. Tente novamente.') from None


@router.get('/recuperar-senha', include_in_schema=False)
def recovery_page():
    return FileResponse(Path(__file__).resolve().parents[2] / 'static' / 'sabino-recuperar-senha.html',
        headers={'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer',
                 'X-Content-Type-Options': 'nosniff'})
