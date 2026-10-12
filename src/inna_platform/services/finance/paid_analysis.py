"""Durable quotes, atomic reservations and cached results for authenticated INNA."""
import asyncio
import hashlib
import json
import logging
import os
from pathlib import Path
from uuid import uuid4

import httpx

from src.inna_platform.services.finance import credit_wallet as wallet

CONFIG = Path(__file__).resolve().parents[4] / 'config/inna-analysis.json'
logger = logging.getLogger(__name__)


def configuration():
    data = json.loads(CONFIG.read_text(encoding='utf-8-sig'))
    cost = data.get('credits_per_analysis')
    if type(cost) is not int or not 1 <= cost <= 10000:
        raise ValueError('Custo de análise inválido')
    return {'enabled': data.get('enabled') is True and wallet.enabled(), 'cost': cost}


def digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def public(row):
    return {key: str(row[key]) if key == 'quote_id' else row[key]
            for key in ('quote_id', 'cost', 'state')}


def quote(user_id, request_id, payload):
    config = configuration()
    if not config['enabled']:
        raise RuntimeError('Análises com créditos ainda não habilitadas')
    fingerprint = digest(payload)
    with wallet.cursor_postgres(dict_cursor=True, commit_automatico=True) as cur:
        cur.execute('''INSERT INTO inna_paid_analyses(user_id,request_id,quote_id,payload_hash,cost)
            VALUES (%s,%s,%s,%s,%s) ON CONFLICT (user_id,request_id) DO NOTHING''',
            (user_id, str(request_id), str(uuid4()), fingerprint, config['cost']))
        cur.execute('SELECT * FROM inna_paid_analyses WHERE user_id=%s AND request_id=%s', (user_id, str(request_id)))
        row = cur.fetchone()
        if row['payload_hash'] != fingerprint:
            raise wallet.CreditConflict('A referência já pertence a outra pergunta')
        return public(row)


def claim(user_id, quote_id, payload):
    with wallet.locked_wallet(user_id) as (cur, balance):
        cur.execute('SELECT * FROM inna_paid_analyses WHERE user_id=%s AND quote_id=%s FOR UPDATE', (user_id, str(quote_id)))
        row = cur.fetchone()
        if not row:
            raise LookupError('Análise não encontrada')
        if row['payload_hash'] != digest(payload):
            raise wallet.CreditConflict('A pergunta mudou; solicite um novo orçamento')
        if row['state'] != 'quoted':
            return row, False
        config = configuration()
        if not config['enabled']:
            raise RuntimeError('Análises com créditos indisponíveis')
        cur.execute("SELECT created_at < NOW() - INTERVAL '15 minutes' AS expired FROM inna_paid_analyses WHERE quote_id=%s", (str(quote_id),))
        if cur.fetchone()['expired'] or row['cost'] != config['cost']:
            raise wallet.CreditConflict('Orçamento expirado; confirme o custo novamente')
        if balance < row['cost']:
            raise wallet.InsufficientCredits('Saldo insuficiente. Recarregue sua carteira.')
        operation_id = 'inna-analysis:' + str(quote_id)
        cur.execute("INSERT INTO inna_credit_operations(user_id,operation_id,amount,kind,source,state) VALUES (%s,%s,%s,'usage','analysis','reserved')", (user_id, operation_id, row['cost']))
        cur.execute('UPDATE inna_credit_wallets SET balance=balance-%s,updated_at=NOW() WHERE user_id=%s', (row['cost'], user_id))
        cur.execute("INSERT INTO inna_credit_ledger(user_id,operation_id,event,delta) VALUES (%s,%s,'reserve',%s)", (user_id, operation_id, -row['cost']))
        cur.execute("UPDATE inna_paid_analyses SET state='running',updated_at=NOW() WHERE quote_id=%s", (str(quote_id),))
        row['state'] = 'running'
        return row, True


def finalize(user_id, quote_id, *, result=None, uncertain=False, review=None):
    """Result, wallet, ledger and final status share one commit."""
    with wallet.locked_wallet(user_id) as (cur, balance):
        cur.execute('SELECT * FROM inna_paid_analyses WHERE user_id=%s AND quote_id=%s FOR UPDATE', (user_id, str(quote_id)))
        row = cur.fetchone()
        allowed = {'running', 'needs_review'} if review else {'running'}
        if not row or row['state'] not in allowed:
            raise wallet.CreditConflict('Análise já finalizada ou não iniciada')
        state = 'needs_review' if uncertain else 'completed' if result is not None else 'refunded'
        if review:
            from .manual_pix_review import assert_reviewer
            assert_reviewer(cur, review['reviewer_id'])
            if uncertain or len(review['reason'].strip()) < 10 or len(review['evidence_ref'].strip()) < 3:
                raise ValueError('Motivo e evidência da conferência são obrigatórios')
            if result is not None and (not isinstance(result, dict) or not isinstance(result.get('resposta'), str) or not result['resposta'].strip()):
                raise ValueError('A conclusão exige uma resposta recuperada válida')
            cur.execute('INSERT INTO inna_paid_analysis_reviews(quote_id,reviewer_id,outcome,reason,evidence_ref) VALUES (%s,%s,%s,%s,%s)',
                        (str(quote_id), review['reviewer_id'], state, review['reason'], review['evidence_ref']))
        if not uncertain:
            operation_id = 'inna-analysis:' + str(quote_id)
            delta = 0 if result is not None else row['cost']
            event = 'complete' if result is not None else 'refund'
            cur.execute('UPDATE inna_credit_operations SET state=%s WHERE user_id=%s AND operation_id=%s AND state=\'reserved\'', (state, user_id, operation_id))
            if cur.rowcount != 1:
                raise wallet.CreditConflict('Reserva inconsistente; requer conferência')
            cur.execute('UPDATE inna_credit_wallets SET balance=balance+%s,updated_at=NOW() WHERE user_id=%s', (delta, user_id))
            cur.execute('INSERT INTO inna_credit_ledger(user_id,operation_id,event,delta) VALUES (%s,%s,%s,%s)', (user_id, operation_id, event, delta))
        cur.execute('UPDATE inna_paid_analyses SET state=%s,result=%s::jsonb,updated_at=NOW() WHERE quote_id=%s', (state, json.dumps(result, ensure_ascii=False) if result is not None else None, str(quote_id)))
        row.update(state=state, result=result)
        return row


def validate_result(data):
    if (not isinstance(data, dict) or not isinstance(data.get('resposta'), str)
            or not data['resposta'].strip() or data.get('ok') is False
            or data.get('fallback') is True or data.get('error')):
        raise ValueError('Resposta válida não entregue')
    return data


async def backend(payload):
    from src.services.financial_scenario import answer_financial_scenario

    calculation = answer_financial_scenario(payload['pergunta'], payload['idioma'])
    if calculation is not None:
        calculation['sabino_global_locale'] = payload['idioma']
        return calculation

    base = os.getenv('INNA_API_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
    url = os.getenv('SABINO_INNA_RAG_URL') or base + '/rag/ask'
    # The existing agent workflow has a 120-second ceiling. Allow its terminal
    # response to arrive instead of abandoning it at the old proxy's 45 seconds.
    timeout = max(10, min(180, float(os.getenv('INNA_PAID_ANALYSIS_TIMEOUT_SECONDS', '135'))))
    async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=5), trust_env=False, follow_redirects=False) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
    validate_result(data)
    data['sabino_global_locale'] = payload['idioma']
    return data


async def execute(user_id, quote_id, payload, worker=None):
    row, started = claim(user_id, quote_id, payload)
    if not started:
        return row
    try:
        result = validate_result(await (worker or backend)(payload))
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.HTTPStatusError, ValueError) as exc:
        # Do not log URLs, payloads or exception messages: they may contain secrets.
        logger.warning('INNA backend failed; refunding: error=%s status=%s',
                       type(exc).__name__,
                       exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None)
        return finalize(user_id, quote_id)
    except asyncio.CancelledError:
        finalize(user_id, quote_id, uncertain=True)
        raise
    except Exception:
        # Preserve the reservation when delivery is uncertain; never rerun it.
        return finalize(user_id, quote_id, uncertain=True)
    return finalize(user_id, quote_id, result=result)


def history(user_id):
    with wallet.cursor_postgres(dict_cursor=True, commit_automatico=False) as cur:
        cur.execute('SELECT quote_id,cost,state,created_at FROM inna_paid_analyses WHERE user_id=%s AND state<>\'quoted\' ORDER BY created_at DESC LIMIT 50', (user_id,))
        return [{**public(row), 'created_at': row['created_at']} for row in cur.fetchall()]


def get(user_id, quote_id):
    with wallet.cursor_postgres(dict_cursor=True, commit_automatico=False) as cur:
        cur.execute('SELECT * FROM inna_paid_analyses WHERE user_id=%s AND quote_id=%s', (user_id, str(quote_id)))
        row = cur.fetchone()
        if not row:
            raise LookupError('Análise não encontrada')
        return row
