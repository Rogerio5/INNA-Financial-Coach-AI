"""Authenticated paid INNA API. Browser cannot choose identity or price."""
import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from . import paid_analysis as service
from .credit_wallet import CreditConflict, InsufficientCredits
from .finance_auth_routes import get_authenticated_user

router = APIRouter(prefix='/api/inna', tags=['inna-analysis'])
User = Annotated[dict, Depends(get_authenticated_user)]
logger = logging.getLogger(__name__)


class Question(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    pergunta: str = Field(min_length=2, max_length=4000)
    idioma: str = Field(default='pt-BR', pattern=r'^[A-Za-z]{2,3}(?:[-_][A-Za-z0-9]{2,8})*$')
    top_k: int = Field(default=4, ge=1, le=8, strict=True)


class QuoteRequest(Question):
    request_id: UUID


class ExecuteRequest(Question):
    quote_id: UUID


def identity(user):
    value = str(user.get('user_id') or '').strip()
    if not value:
        raise HTTPException(401, 'Entre na sua conta para continuar.')
    return value


def guard(request):
    origin = request.headers.get('origin')
    if (request.headers.get('X-Sabino-Analysis') != 'confirmed'
            or request.headers.get('sec-fetch-site') == 'cross-site'
            or (origin and origin != str(request.base_url).rstrip('/'))):
        raise HTTPException(403, 'Origem da solicitação inválida')


def translate(exc):
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, InsufficientCredits):
        return HTTPException(402, str(exc))
    if isinstance(exc, CreditConflict):
        return HTTPException(409, str(exc))
    if isinstance(exc, LookupError):
        return HTTPException(404, 'Análise não encontrada')
    logger.error('Paid INNA request unavailable: %s', type(exc).__name__)
    return HTTPException(503, 'Não foi possível concluir. Consulte o histórico antes de tentar novamente.')


def render(row):
    info = service.public(row)
    if row['state'] == 'completed':
        return JSONResponse({**row['result'], 'billing': info}, headers={'Cache-Control': 'no-store'})
    messages = {
        'refunded': 'A análise falhou e os créditos foram devolvidos.',
        'needs_review': 'A entrega da resposta não pôde ser confirmada. Os créditos continuam reservados enquanto a análise aguarda conferência. Consulte Minha carteira; consultar não cobra novamente.',
        'running': 'A INNA ainda está analisando. Consultar o resultado não cobra novamente.',
    }
    message = messages.get(row['state'], 'A análise ainda não foi iniciada. Nenhum crédito foi consumido.')
    return JSONResponse({'billing': info, 'detail': message}, status_code=422 if row['state'] == 'refunded' else 202,
                        headers={'Cache-Control': 'no-store'})


@router.get('/pricing')
def pricing(response: Response, user: User):
    identity(user)
    response.headers['Cache-Control'] = 'no-store'
    return service.configuration()


@router.post('/quote')
def quote(body: QuoteRequest, request: Request, response: Response, user: User):
    guard(request)
    response.headers['Cache-Control'] = 'no-store'
    try:
        return service.quote(identity(user), body.request_id, body.model_dump(exclude={'request_id'}))
    except Exception as exc:
        raise translate(exc) from None


@router.post('/ask')
async def ask(body: ExecuteRequest, request: Request, user: User):
    guard(request)
    try:
        return render(await service.execute(identity(user), body.quote_id, body.model_dump(exclude={'quote_id'})))
    except Exception as exc:
        raise translate(exc) from None


@router.get('/analyses')
def history(response: Response, user: User):
    response.headers['Cache-Control'] = 'no-store'
    try:
        return {'analyses': service.history(identity(user))}
    except Exception as exc:
        raise translate(exc) from None


@router.get('/analyses/{quote_id}')
def result(quote_id: UUID, user: User):
    try:
        return render(service.get(identity(user), quote_id))
    except Exception as exc:
        raise translate(exc) from None
