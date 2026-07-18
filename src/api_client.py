from __future__ import annotations

import json
import os
import time
import uuid
from collections.abc import Mapping
from typing import Any

import requests
from dotenv import load_dotenv

from api.security.internal_request import (
    HEADER_REQUEST_ID,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    HEADER_USER_ID,
    InternalRequestConfigurationError,
    InternalRequestSecurityError,
    assinar_requisicao_interna,
)


load_dotenv()


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


class InternalApiClientError(
    RuntimeError
):
    """
    Erro sanitizado do cliente interno da API.
    """


def _request_error_message(
    _error: Exception,
) -> str:
    return (
        "Não foi possível conectar com a API da INNA. "
        "Verifique se a FastAPI está rodando com o "
        "comando: python -m uvicorn api.main:app "
        "--reload --port 8000"
    )


def _serializar_json_canonico(
    payload: Mapping[str, Any],
) -> bytes:
    if not isinstance(
        payload,
        Mapping,
    ):
        raise InternalApiClientError(
            "O conteúdo da requisição é inválido."
        )

    try:
        serialized = json.dumps(
            dict(
                payload
            ),
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            allow_nan=False,
        )

    except (
        TypeError,
        ValueError,
    ):
        raise InternalApiClientError(
            "O conteúdo da requisição é inválido."
        ) from None

    return serialized.encode(
        "utf-8"
    )


def gerar_request_id_interno(
    *,
    origem: str = "web",
) -> str:
    normalized_origin = str(
        origem or ""
    ).strip().lower()

    if (
        not normalized_origin
        or not normalized_origin.replace(
            "-",
            "",
        ).replace(
            "_",
            "",
        ).isalnum()
        or len(normalized_origin) > 20
    ):
        raise InternalApiClientError(
            "A origem da requisição é inválida."
        )

    return (
        f"{normalized_origin}-"
        f"{uuid.uuid4().hex}"
    )


def preparar_requisicao_interna_json(
    *,
    method: str,
    path: str,
    payload: Mapping[str, Any],
    usuario_id_confiavel: str,
    request_id: str | None = None,
    timestamp: int | None = None,
) -> tuple[
    bytes,
    dict[str, str],
    str,
]:
    """
    Serializa e assina exatamente os bytes que serão
    enviados para a FastAPI.
    """
    body = _serializar_json_canonico(
        payload
    )

    effective_request_id = (
        str(
            request_id
        ).strip()
        if request_id is not None
        else gerar_request_id_interno(
            origem="web"
        )
    )

    effective_timestamp = int(
        time.time()
        if timestamp is None
        else timestamp
    )

    try:
        signature = (
            assinar_requisicao_interna(
                method=method,
                path=path,
                user_id=(
                    usuario_id_confiavel
                ),
                request_id=(
                    effective_request_id
                ),
                timestamp=(
                    effective_timestamp
                ),
                body=body,
            )
        )

    except (
        InternalRequestConfigurationError,
        InternalRequestSecurityError,
    ):
        raise InternalApiClientError(
            "Não foi possível autenticar a "
            "comunicação interna com a API."
        ) from None

    headers = {
        "Content-Type": (
            "application/json; charset=utf-8"
        ),
        HEADER_USER_ID: str(
            usuario_id_confiavel
        ).strip(),
        HEADER_REQUEST_ID: (
            effective_request_id
        ),
        HEADER_TIMESTAMP: str(
            effective_timestamp
        ),
        HEADER_SIGNATURE: signature,
    }

    return (
        body,
        headers,
        effective_request_id,
    )


def verificar_api_online() -> bool:
    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=5,
        )

        return response.status_code == 200

    except requests.RequestException:
        return False


def gerar_diagnostico_api(
    payload: Mapping[str, Any],
    *,
    usuario_id_confiavel: str,
    request_id: str | None = None,
) -> dict[str, Any]:
    path = "/diagnostico"

    body, headers, _effective_request_id = (
        preparar_requisicao_interna_json(
            method="POST",
            path=path,
            payload=payload,
            usuario_id_confiavel=(
                usuario_id_confiavel
            ),
            request_id=request_id,
        )
    )

    try:
        response = requests.post(
            f"{API_BASE_URL}{path}",
            data=body,
            headers=headers,
            timeout=60,
        )

        response.raise_for_status()

        result = response.json()

        if not isinstance(
            result,
            dict,
        ):
            raise InternalApiClientError(
                "A API retornou uma resposta inválida."
            )

        return result

    except requests.ConnectionError as error:
        raise RuntimeError(
            _request_error_message(
                error
            )
        ) from error

    except requests.Timeout as error:
        raise RuntimeError(
            "A API da INNA demorou muito para "
            "responder. Tente novamente em alguns "
            "instantes."
        ) from error

    except requests.HTTPError as error:
        status_code = getattr(
            response,
            "status_code",
            "desconhecido",
        )

        raise RuntimeError(
            "A API da INNA retornou um erro HTTP "
            f"{status_code}. Verifique sua sessão "
            "e os dados enviados."
        ) from error

    except InternalApiClientError:
        raise

    except (
        requests.RequestException,
        ValueError,
    ) as error:
        raise RuntimeError(
            _request_error_message(
                error
            )
        ) from error


def gerar_diagnostico_telegram_api(
    payload: Mapping[str, Any],
    *,
    usuario_id_confiavel: str,
    request_id: str,
) -> dict[str, Any]:
    """
    Envia um diagnóstico do bot polling para a rota
    interna exclusiva do Telegram.
    """
    path = (
        "/internal/telegram/diagnostico"
    )

    body, headers, _effective_request_id = (
        preparar_requisicao_interna_json(
            method="POST",
            path=path,
            payload=payload,
            usuario_id_confiavel=(
                usuario_id_confiavel
            ),
            request_id=request_id,
        )
    )

    try:
        response = requests.post(
            f"{API_BASE_URL}{path}",
            data=body,
            headers=headers,
            timeout=90,
        )

        response.raise_for_status()

        result = response.json()

        if not isinstance(
            result,
            dict,
        ):
            raise InternalApiClientError(
                "A API retornou uma resposta inválida."
            )

        return result

    except requests.Timeout as error:
        raise RuntimeError(
            "A API da INNA demorou muito para "
            "responder."
        ) from error

    except requests.RequestException as error:
        raise RuntimeError(
            "Não foi possível processar o "
            "diagnóstico Telegram."
        ) from error

    except (
        InternalApiClientError,
        ValueError,
    ):
        raise InternalApiClientError(
            "A resposta do diagnóstico "
            "Telegram é inválida."
        ) from None


def enviar_feedback_api(
    payload: dict,
) -> dict:
    try:
        response = requests.post(
            f"{API_BASE_URL}/feedback",
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        raise RuntimeError(
            "Não foi possível enviar o feedback "
            "para a API da INNA."
        ) from error


def baixar_relatorio_pdf_api(
    diagnostico_id: int,
) -> bytes:
    try:
        response = requests.get(
            (
                f"{API_BASE_URL}/diagnosticos/"
                f"{diagnostico_id}/relatorio"
            ),
            timeout=60,
        )

        response.raise_for_status()

        return response.content

    except requests.RequestException as error:
        raise RuntimeError(
            "Não foi possível baixar o relatório "
            "PDF pela API da INNA."
        ) from error


def buscar_historico_usuario_api(
    nome: str,
    limit: int = 10,
) -> list[dict]:
    """
    Fluxo legado. Será substituído pelo histórico
    autenticado durante a fase F.
    """
    try:
        response = requests.get(
            (
                f"{API_BASE_URL}/diagnosticos/"
                f"usuario/{nome}"
            ),
            params={
                "limit": limit,
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        raise RuntimeError(
            "Não foi possível buscar o histórico "
            "pela API."
        ) from error


def enviar_relatorio_email(
    diagnostico_id: int,
    email: str,
    idioma: str = "pt",
    moeda: str = "BRL",
    simbolo_moeda: str = "R$",
):
    """
    Fluxo legado. Será autenticado e protegido por
    usuário na etapa específica de e-mail.
    """
    url = (
        f"{API_BASE_URL}/diagnosticos/"
        f"{diagnostico_id}/enviar-email"
    )

    response = requests.post(
        url,
        json={
            "email": email,
            "idioma": idioma,
            "moeda": moeda,
            "simbolo_moeda": (
                simbolo_moeda
            ),
        },
        timeout=60,
    )

    if response.status_code >= 400:
        raise RuntimeError(
            "Não foi possível enviar o relatório "
            "por e-mail."
        )

    return response.json()


__all__ = [
    "API_BASE_URL",
    "InternalApiClientError",
    "baixar_relatorio_pdf_api",
    "buscar_historico_usuario_api",
    "enviar_feedback_api",
    "enviar_relatorio_email",
    "gerar_diagnostico_api",
    "gerar_diagnostico_telegram_api",
    "gerar_request_id_interno",
    "preparar_requisicao_interna_json",
    "verificar_api_online",
]
