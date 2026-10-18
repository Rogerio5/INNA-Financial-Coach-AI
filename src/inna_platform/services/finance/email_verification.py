"""Optional email ownership confirmation. Never grants sessions or paid access."""
import logging
import os
import re
import secrets
from email.utils import parseaddr
from html import escape

import requests
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field

from . import password_recovery as recovery
from .finance_identity import cursor_postgres

router = APIRouter()
logger = logging.getLogger(__name__)


def enabled():
    if os.getenv('SABINO_SIGNUP_EMAIL_ENABLED', '').lower().strip() != 'true':
        return False
    try:
        provider, _, sender, _ = recovery.settings()
        return not (provider == 'resend' and parseaddr(sender)[1].lower().endswith('@resend.dev'))
    except Exception:
        return False


def ensure_schema():
    recovery.ensure_schema()
    with cursor_postgres(commit_automatico=True) as cur:
        cur.execute('''CREATE TABLE IF NOT EXISTS inna_email_confirmations (
            user_id TEXT PRIMARY KEY REFERENCES inna_auth_users(user_id) ON DELETE CASCADE,
            email TEXT NOT NULL, verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW())''')
        cur.execute('''CREATE TABLE IF NOT EXISTS inna_email_confirmation_tokens (
            token_hash TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES inna_auth_users(user_id) ON DELETE CASCADE,
            email TEXT NOT NULL, expires_at TIMESTAMPTZ NOT NULL,
            used_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_inna_email_tokens_user ON inna_email_confirmation_tokens(user_id)')


def is_verified(user):
    with cursor_postgres(dict_cursor=True) as cur:
        cur.execute('SELECT user_id FROM inna_email_confirmations WHERE user_id=%s AND email=%s',
                    (user['user_id'], user['email']))
        return bool(cur.fetchone())


def deliver(email):
    """Failure never rolls back an account or writes tokens/addresses to logs."""
    token_hash = None
    try:
        if not enabled():
            return
        ensure_schema()
        provider, key, sender, origin = recovery.settings()
        token = secrets.token_urlsafe(32)
        token_hash = recovery.digest(token)
        with cursor_postgres(dict_cursor=True, commit_automatico=True) as cur:
            cur.execute('SELECT user_id,email FROM inna_auth_users WHERE email=%s AND active=TRUE FOR UPDATE', (email,))
            user = cur.fetchone()
            if not user:
                return
            cur.execute('SELECT user_id FROM inna_email_confirmations WHERE user_id=%s AND email=%s', (user['user_id'], email))
            if cur.fetchone():
                return
            cur.execute('SELECT name FROM inna_account_profiles WHERE user_id=%s', (user['user_id'],))
            profile = cur.fetchone()
            name = profile['name'] if profile else 'Olá'
            cur.execute("DELETE FROM inna_email_confirmation_tokens WHERE expires_at < NOW()-INTERVAL '1 day'")
            cur.execute("INSERT INTO inna_email_confirmation_tokens(token_hash,user_id,email,expires_at) VALUES (%s,%s,%s,NOW()+INTERVAL '24 hours')", (token_hash, user['user_id'], email))
        link = origin + '/confirmar-email#token=' + token
        subject = 'Boas-vindas! Confirme seu e-mail — Sabino.AI'
        text = (f'Olá, {name}!\n\nSua conta Sabino.AI foi criada com o e-mail {email}.\n'
                f'Confirme que este endereço é seu pelo link abaixo, válido por 24 horas:\n{link}\n\n'
                'Depois, entre com seu e-mail e a senha que você definiu. Criar a conta não contrata um plano nem gera cobrança.\n'
                'Nunca enviamos sua senha por e-mail. Se você não fez o cadastro, ignore esta mensagem e não confirme o endereço.\n'
                f'Ajuda: {origin}/ajuda')
        html = (f'<h1>Boas-vindas à Sabino.AI</h1><p>Olá, {escape(name)}!</p>'
                f'<p>Sua conta foi criada com o e-mail <strong>{escape(email)}</strong>.</p>'
                f'<p><a href="{escape(link, quote=True)}">Confirmar meu e-mail</a></p>'
                '<p>O link vale por 24 horas e funciona uma única vez. Depois, entre com seu e-mail e a senha que você definiu.</p>'
                '<p>Criar a conta não contrata um plano nem gera cobrança. Nunca enviamos sua senha por e-mail.</p>'
                '<p>Se você não fez o cadastro, ignore esta mensagem e não confirme o endereço.</p>'
                f'<p><a href="{origin}/ajuda">Ajuda e suporte</a></p>')
        if provider == 'brevo':
            sender_name, address = parseaddr(sender)
            result = requests.post('https://api.brevo.com/v3/smtp/email', headers={'api-key': key},
                json={'sender': {'name': sender_name or 'Sabino.AI', 'email': address},
                      'to': [{'email': email}], 'subject': subject, 'textContent': text, 'htmlContent': html}, timeout=20)
        else:
            result = requests.post('https://api.resend.com/emails', headers={'Authorization': 'Bearer ' + key},
                json={'from': sender, 'to': [email], 'subject': subject, 'text': text, 'html': html}, timeout=20)
        result.raise_for_status()
        logger.info('Signup confirmation accepted by email provider')
    except Exception as exc:
        status = getattr(getattr(exc, 'response', None), 'status_code', None)
        logger.error('Signup confirmation delivery failed: %s status=%s', type(exc).__name__, status)
        if token_hash:
            try:
                with cursor_postgres(commit_automatico=True) as cur:
                    cur.execute('DELETE FROM inna_email_confirmation_tokens WHERE token_hash=%s', (token_hash,))
            except Exception:
                logger.error('Signup confirmation cleanup failed')


def confirm_token(token):
    if not re.fullmatch(r'[A-Za-z0-9_-]{43}', token):
        raise ValueError('Link inválido, expirado ou já utilizado. Entre em Minha conta para solicitar outro.')
    hashed = recovery.digest(token)
    with cursor_postgres(dict_cursor=True, commit_automatico=True) as cur:
        cur.execute('''SELECT user_id,email FROM inna_email_confirmation_tokens
            WHERE token_hash=%s AND used_at IS NULL AND expires_at>NOW()''', (hashed,))
        row = cur.fetchone()
        if not row:
            raise ValueError('Link inválido, expirado ou já utilizado. Entre em Minha conta para solicitar outro.')
        cur.execute('SELECT user_id FROM inna_auth_users WHERE user_id=%s AND email=%s AND active=TRUE FOR UPDATE', (row['user_id'], row['email']))
        if not cur.fetchone():
            raise ValueError('Não foi possível confirmar este endereço.')
        cur.execute('''UPDATE inna_email_confirmation_tokens SET used_at=NOW()
            WHERE token_hash=%s AND used_at IS NULL AND expires_at>NOW() RETURNING user_id''', (hashed,))
        if not cur.fetchone():
            raise ValueError('Link inválido, expirado ou já utilizado.')
        cur.execute('''INSERT INTO inna_email_confirmations(user_id,email) VALUES (%s,%s)
            ON CONFLICT(user_id) DO UPDATE SET email=EXCLUDED.email,verified_at=NOW()''', (row['user_id'], row['email']))
        cur.execute('UPDATE inna_email_confirmation_tokens SET used_at=NOW() WHERE user_id=%s AND used_at IS NULL', (row['user_id'],))


class ConfirmationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    token: str = Field(min_length=43, max_length=43)


@router.post('/auth/email/confirm')
def confirm(body: ConfirmationRequest, request: Request, response: Response):
    from .account_management import protect
    response.headers['Cache-Control'] = 'no-store'
    protect(request)
    try:
        ensure_schema()
        if not recovery.allow('email-confirm:global', 100):
            raise HTTPException(429, 'Muitas tentativas. Tente novamente mais tarde.')
        confirm_token(body.token)
        return {'message': 'E-mail confirmado! Entre na Sabino.AI com seu e-mail e senha.'}
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
    except Exception:
        raise HTTPException(503, 'Não foi possível confirmar agora. Tente novamente.') from None


@router.get('/auth/email/status')
def verification_status(request: Request, response: Response):
    from .account_management import current_user
    response.headers['Cache-Control'] = 'no-store'
    user = current_user(request)
    try:
        ensure_schema()
        return {'verified': is_verified(user), 'sending_enabled': enabled()}
    except Exception:
        raise HTTPException(503, 'Não foi possível consultar a confirmação agora.') from None


@router.post('/auth/email/resend', status_code=202)
def resend(request: Request, response: Response, background: BackgroundTasks):
    from .account_management import current_user, protect
    response.headers['Cache-Control'] = 'no-store'
    protect(request)
    user = current_user(request)
    try:
        if not enabled():
            raise HTTPException(503, 'O envio de confirmação ainda não está disponível. Seu acesso continua funcionando.')
        ensure_schema()
        if is_verified(user):
            return {'message': 'Seu e-mail já está confirmado.'}
        if not recovery.allow('email-send:global', 100) or not recovery.allow('email-send:' + recovery.digest(user['email']), 3):
            raise HTTPException(429, 'Limite de envios atingido. Tente novamente em uma hora.')
        background.add_task(deliver, user['email'])
        return {'message': 'Solicitação recebida. Confira sua caixa de entrada e o spam nos próximos minutos.'}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(503, 'Não foi possível solicitar o envio agora.') from None


PAGE = '''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Confirmar e-mail | Sabino.AI</title>
<style>:root{color-scheme:dark;font-family:system-ui;background:#090c0b;color:#f5f5f1}*{box-sizing:border-box}main{max-width:480px;margin:10vh auto;padding:28px;border:1px solid #30362c;border-radius:18px;background:#111610}h1{font-size:28px}p{line-height:1.7;color:#b7bdb7}a{color:#e8c25f}button{width:100%;padding:15px;border:0;border-radius:9px;background:#e8c25f;color:#171b12;font:inherit;font-weight:700;cursor:pointer}button:disabled{opacity:.6}a:focus-visible,button:focus-visible{outline:2px solid #e8c25f;outline-offset:4px}[hidden]{display:none}body{padding:16px;margin:0}</style></head>
<body><main><a href="/">Sabino.AI</a><h1>Confirme seu e-mail</h1>
<p>Confirme que este endereço pertence a você. Sua senha não será alterada.</p>
<button id="confirm" type="button">Confirmar meu e-mail</button><p id="status" role="status" aria-live="polite"></p>
<p><a href="/">Entrar na Sabino.AI</a> · <a href="/minha-conta">Minha conta</a></p></main>
<script>(()=>{'use strict';let token=new URLSearchParams(location.hash.slice(1)).get('token')||'';history.replaceState(null,'',location.pathname);const button=document.getElementById('confirm'),status=document.getElementById('status');if(!/^[A-Za-z0-9_-]{43}$/.test(token)){button.hidden=true;status.textContent='Abra o link recebido por e-mail. Para solicitar outro, entre em Minha conta.';}button.addEventListener('click',async()=>{button.disabled=true;status.textContent='Confirmando…';try{const response=await fetch('/auth/email/confirm',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json','X-Sabino-Account':'1'},body:JSON.stringify({token})});const data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Não foi possível confirmar agora.');token='';button.hidden=true;status.textContent=data.message;}catch(error){status.textContent=error.message||'Não foi possível conectar. Tente novamente.';button.disabled=false;}});})();</script></body></html>'''


@router.get('/confirmar-email', include_in_schema=False)
def confirmation_page():
    return HTMLResponse(PAGE, headers={'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer',
        'X-Content-Type-Options': 'nosniff', 'Content-Security-Policy': "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"})
