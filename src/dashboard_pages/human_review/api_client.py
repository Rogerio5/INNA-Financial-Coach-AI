from __future__ import annotations

import json
import time
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import quote

import requests

from api.security.internal_request import (
    HEADER_REQUEST_ID,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    HEADER_USER_ID,
    InternalRequestConfigurationError,
    InternalRequestSecurityError,
    assinar_requisicao_interna,
)
from src.api_client import (
    API_BASE_URL,
    gerar_request_id_interno,
)

from .models import (
    HumanReviewDashboardMetrics,
    HumanReviewDashboardPage,
    HumanReviewDashboardRecord,
    HumanReviewDashboardResolution,
)


ADMIN_PREFIX = (
    "/internal/human-reviews/admin"
)


class HumanReviewDashboardApiError(
    RuntimeError
):
    """Erro seguro do cliente administrativo HITL."""


def _canonical_json_bytes(
    payload: Mapping[str, Any],
) -> bytes:
    try:
        return json.dumps(
            dict(payload),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")

    except (
        TypeError,
        ValueError,
    ):
        raise HumanReviewDashboardApiError(
            "O conteúdo da operação HITL é inválido."
        ) from None


def _signed_headers(
    *,
    method: str,
    path: str,
    admin_user_id: str,
    body: bytes = b"",
    request_id: str | None = None,
    timestamp: int | None = None,
) -> dict[str, str]:
    normalized_admin_id = str(
        admin_user_id or ""
    ).strip()

    if not normalized_admin_id:
        raise HumanReviewDashboardApiError(
            "A identidade administrativa "
            "não está disponível."
        )

    effective_request_id = (
        str(request_id).strip()
        if request_id is not None
        else gerar_request_id_interno(
            origem="hitl-admin"
        )
    )

    effective_timestamp = int(
        time.time()
        if timestamp is None
        else timestamp
    )

    try:
        signature = assinar_requisicao_interna(
            method=method,
            path=path,
            user_id=normalized_admin_id,
            request_id=effective_request_id,
            timestamp=effective_timestamp,
            body=body,
        )

    except (
        InternalRequestConfigurationError,
        InternalRequestSecurityError,
    ):
        raise HumanReviewDashboardApiError(
            "Não foi possível autenticar a "
            "comunicação administrativa."
        ) from None

    return {
        HEADER_USER_ID: normalized_admin_id,
        HEADER_REQUEST_ID: (
            effective_request_id
        ),
        HEADER_TIMESTAMP: str(
            effective_timestamp
        ),
        HEADER_SIGNATURE: signature,
    }


def _raise_safe_response_error(
    response: requests.Response,
) -> None:
    if response.ok:
        return

    status_code = response.status_code

    messages = {
        401: (
            "A autenticação interna do painel "
            "foi recusada."
        ),
        403: (
            "O usuário atual não possui permissão "
            "administrativa HITL."
        ),
        404: (
            "A revisão humana solicitada "
            "não foi encontrada."
        ),
        409: (
            "A revisão foi alterada ou assumida "
            "por outro administrador."
        ),
        422: (
            "Os filtros ou dados enviados "
            "são inválidos."
        ),
        503: (
            "O serviço HITL está temporariamente "
            "indisponível."
        ),
    }

    raise HumanReviewDashboardApiError(
        messages.get(
            status_code,
            "Não foi possível concluir a "
            "operação administrativa HITL.",
        )
    )


def _get_json(
    *,
    path: str,
    admin_user_id: str,
    params: Sequence[
        tuple[str, str | int]
    ] | Mapping[str, Any] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    headers = _signed_headers(
        method="GET",
        path=path,
        admin_user_id=admin_user_id,
        body=b"",
    )

    try:
        response = requests.get(
            f"{API_BASE_URL}{path}",
            params=params,
            headers=headers,
            timeout=timeout,
        )

        _raise_safe_response_error(response)

        result = response.json()

    except HumanReviewDashboardApiError:
        raise

    except (
        requests.RequestException,
        ValueError,
    ):
        raise HumanReviewDashboardApiError(
            "Não foi possível conectar ao serviço "
            "administrativo HITL."
        ) from None

    if not isinstance(result, dict):
        raise HumanReviewDashboardApiError(
            "A API HITL retornou uma resposta "
            "inválida."
        )

    return result


def _post_json(
    *,
    path: str,
    admin_user_id: str,
    payload: Mapping[str, Any],
    timeout: int = 60,
) -> dict[str, Any]:
    body = _canonical_json_bytes(payload)

    headers = _signed_headers(
        method="POST",
        path=path,
        admin_user_id=admin_user_id,
        body=body,
    )

    headers["Content-Type"] = (
        "application/json; charset=utf-8"
    )

    try:
        response = requests.post(
            f"{API_BASE_URL}{path}",
            data=body,
            headers=headers,
            timeout=timeout,
        )

        _raise_safe_response_error(response)

        result = response.json()

    except HumanReviewDashboardApiError:
        raise

    except (
        requests.RequestException,
        ValueError,
    ):
        raise HumanReviewDashboardApiError(
            "Não foi possível conectar ao serviço "
            "administrativo HITL."
        ) from None

    if not isinstance(result, dict):
        raise HumanReviewDashboardApiError(
            "A API HITL retornou uma resposta "
            "inválida."
        )

    return result


def listar_revisoes_hitl_api(
    *,
    admin_user_id: str,
    statuses: Sequence[str] = (),
    risk_levels: Sequence[str] = (),
    requested_by: str = "",
    reviewer_id: str = "",
    thread_id: str = "",
    search: str = "",
    created_from: str = "",
    created_to: str = "",
    limit: int = 50,
    offset: int = 0,
) -> HumanReviewDashboardPage:
    params: list[
        tuple[str, str | int]
    ] = []

    params.extend(
        ("statuses", status)
        for status in statuses
    )

    params.extend(
        ("risk_levels", risk)
        for risk in risk_levels
    )

    optional_parameters = {
        "requested_by": requested_by,
        "reviewer_id": reviewer_id,
        "thread_id": thread_id,
        "search": search,
        "created_from": created_from,
        "created_to": created_to,
    }

    params.extend(
        (key, value)
        for key, value
        in optional_parameters.items()
        if str(value).strip()
    )

    params.extend([
        ("limit", int(limit)),
        ("offset", int(offset)),
    ])

    result = _get_json(
        path=f"{ADMIN_PREFIX}/reviews",
        admin_user_id=admin_user_id,
        params=params,
    )

    return HumanReviewDashboardPage.from_dict(
        result
    )


def obter_revisao_hitl_api(
    *,
    admin_user_id: str,
    review_id: str,
) -> HumanReviewDashboardRecord:
    normalized_review_id = str(
        review_id or ""
    ).strip()

    if not normalized_review_id:
        raise HumanReviewDashboardApiError(
            "O identificador da revisão "
            "é obrigatório."
        )

    safe_review_id = quote(
        normalized_review_id,
        safe="",
    )

    result = _get_json(
        path=(
            f"{ADMIN_PREFIX}/reviews/"
            f"{safe_review_id}"
        ),
        admin_user_id=admin_user_id,
    )

    return HumanReviewDashboardRecord.from_dict(
        result
    )


def obter_metricas_hitl_api(
    *,
    admin_user_id: str,
    created_from: str = "",
    created_to: str = "",
) -> HumanReviewDashboardMetrics:
    params = {
        key: value
        for key, value in {
            "created_from": created_from,
            "created_to": created_to,
        }.items()
        if str(value).strip()
    }

    result = _get_json(
        path=f"{ADMIN_PREFIX}/metrics",
        admin_user_id=admin_user_id,
        params=params,
    )

    return HumanReviewDashboardMetrics.from_dict(
        result
    )


def recuperar_claims_hitl_api(
    *,
    admin_user_id: str,
    timeout_seconds: int = 300,
) -> tuple[str, ...]:
    result = _post_json(
        path=f"{ADMIN_PREFIX}/recover-stale",
        admin_user_id=admin_user_id,
        payload={
            "timeout_seconds": int(
                timeout_seconds
            ),
        },
    )

    return tuple(
        str(review_id)
        for review_id in (
            result.get(
                "recovered_review_ids"
            )
            or []
        )
    )


def resolver_revisao_hitl_api(
    *,
    admin_user_id: str,
    review_id: str,
    thread_id: str,
    action: str,
    comment: str = "",
    reason: str = "",
    corrections: Mapping[
        str,
        Any,
    ] | None = None,
) -> HumanReviewDashboardResolution:
    normalized_review_id = str(
        review_id or ""
    ).strip()

    normalized_thread_id = str(
        thread_id or ""
    ).strip()

    normalized_action = str(
        action or ""
    ).strip().lower()

    allowed_actions = {
        "approve",
        "correct",
        "reject",
        "cancel",
    }

    if not normalized_review_id:
        raise HumanReviewDashboardApiError(
            "O identificador da revisão "
            "é obrigatório."
        )

    if not normalized_thread_id:
        raise HumanReviewDashboardApiError(
            "A conversa vinculada à revisão "
            "não está disponível."
        )

    if normalized_action not in allowed_actions:
        raise HumanReviewDashboardApiError(
            "A decisão HITL é inválida."
        )

    normalized_corrections = dict(
        corrections or {}
    )

    if (
        normalized_action == "correct"
        and not normalized_corrections
    ):
        raise HumanReviewDashboardApiError(
            "Informe pelo menos uma correção."
        )

    normalized_reason = str(
        reason or ""
    ).strip()

    if (
        normalized_action == "reject"
        and not normalized_reason
    ):
        raise HumanReviewDashboardApiError(
            "Informe o motivo da rejeição."
        )

    safe_review_id = quote(
        normalized_review_id,
        safe="",
    )

    result = _post_json(
        path=(
            "/internal/human-reviews/"
            f"{safe_review_id}/resolve"
        ),
        admin_user_id=admin_user_id,
        payload={
            "thread_id": normalized_thread_id,
            "action": normalized_action,
            "comment": str(
                comment or ""
            ).strip(),
            "reason": normalized_reason,
            "corrections": (
                normalized_corrections
            ),
        },
        timeout=90,
    )

    return (
        HumanReviewDashboardResolution
        .from_dict(result)
    )


__all__ = [
    "HumanReviewDashboardApiError",
    "listar_revisoes_hitl_api",
    "obter_metricas_hitl_api",
    "obter_revisao_hitl_api",
    "recuperar_claims_hitl_api",
    "resolver_revisao_hitl_api",
]
