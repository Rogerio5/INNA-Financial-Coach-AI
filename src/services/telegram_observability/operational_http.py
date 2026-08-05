from __future__ import annotations

import json
import math
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .health_readiness import (
    TelegramOperationalSnapshot,
    TelegramOperationalStatus,
)
from .readiness_runtime import (
    TelegramReadinessRuntimeResult,
)


TELEGRAM_OPERATIONAL_SCHEMA_VERSION = "telegram-operational-status.v1"

TELEGRAM_OPERATIONAL_JSON_CONTENT_TYPE = "application/json; charset=utf-8"


class TelegramOperationalProbeKind(
    str,
    Enum,
):
    HEALTH = "health"
    READINESS = "readiness"


class TelegramOperationalVisibility(
    str,
    Enum,
):
    PUBLIC = "public"
    INTERNAL = "internal"


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramOperationalHttpResponse:
    status_code: int
    body: str
    content_type: str
    headers: Mapping[str, str]

    def __post_init__(
        self,
    ) -> None:
        normalized_status_code = int(self.status_code)

        if not (100 <= normalized_status_code <= 599):
            raise ValueError("Código HTTP inválido.")

        normalized_content_type = str(self.content_type).strip()

        if not normalized_content_type:
            raise ValueError("Content-Type obrigatório.")

        object.__setattr__(
            self,
            "status_code",
            normalized_status_code,
        )

        object.__setattr__(
            self,
            "body",
            str(self.body),
        )

        object.__setattr__(
            self,
            "content_type",
            normalized_content_type,
        )

        object.__setattr__(
            self,
            "headers",
            MappingProxyType(
                {str(name): str(value) for name, value in self.headers.items()}
            ),
        )


def _finite_number(
    value: object,
) -> float:
    try:
        normalized = float(value)
    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    if math.isnan(normalized) or math.isinf(normalized):
        return 0.0

    return normalized


def _status_code_for(
    status: TelegramOperationalStatus,
) -> int:
    if status is TelegramOperationalStatus.UNREADY:
        return 503

    return 200


def _safe_headers(
    *,
    status: TelegramOperationalStatus,
) -> Mapping[str, str]:
    return MappingProxyType(
        {
            "Cache-Control": "no-store",
            "X-Content-Type-Options": ("nosniff"),
            "X-INNA-Schema-Version": (TELEGRAM_OPERATIONAL_SCHEMA_VERSION),
            "X-INNA-Operational-Status": (status.value),
        }
    )


def _serialize_payload(
    payload: Mapping[
        str,
        object,
    ],
) -> str:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            allow_nan=False,
        )
        + "\n"
    )


def _public_runtime_payload(
    result: TelegramReadinessRuntimeResult,
    *,
    probe: TelegramOperationalProbeKind,
) -> dict[str, object]:
    return {
        "schema_version": (TELEGRAM_OPERATIONAL_SCHEMA_VERSION),
        "probe": probe.value,
        "status": (result.snapshot.status.value),
        "ready": result.ready,
        "sequence": result.sequence,
        "cache_hit": result.cache_hit,
        "reason": result.reason,
    }


def _internal_runtime_payload(
    result: TelegramReadinessRuntimeResult,
    *,
    probe: TelegramOperationalProbeKind,
) -> dict[str, object]:
    operational = result.snapshot.to_safe_dict()

    operational["checked_at_epoch_seconds"] = _finite_number(
        operational.get("checked_at_epoch_seconds")
    )

    operational["total_latency_seconds"] = _finite_number(
        operational.get("total_latency_seconds")
    )

    return {
        "schema_version": (TELEGRAM_OPERATIONAL_SCHEMA_VERSION),
        "probe": probe.value,
        "status": (result.snapshot.status.value),
        "ready": result.ready,
        "runtime": {
            "sequence": result.sequence,
            "cache_hit": (result.cache_hit),
            "cache_age_seconds": (_finite_number(result.cache_age_seconds)),
            "generated_at_epoch_seconds": (
                _finite_number(result.generated_at_epoch_seconds)
            ),
            "reason": result.reason,
        },
        "operational": operational,
    }


def _snapshot_payload(
    snapshot: TelegramOperationalSnapshot,
    *,
    probe: TelegramOperationalProbeKind,
    visibility: (TelegramOperationalVisibility),
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": (TELEGRAM_OPERATIONAL_SCHEMA_VERSION),
        "probe": probe.value,
        "status": snapshot.status.value,
        "ready": snapshot.ready,
    }

    if visibility is TelegramOperationalVisibility.INTERNAL:
        payload["operational"] = snapshot.to_safe_dict()

    return payload


def create_runtime_http_response(
    result: TelegramReadinessRuntimeResult,
    *,
    probe: (TelegramOperationalProbeKind | str) = (
        TelegramOperationalProbeKind.READINESS
    ),
    visibility: (TelegramOperationalVisibility | str) = (
        TelegramOperationalVisibility.PUBLIC
    ),
) -> TelegramOperationalHttpResponse:
    if not isinstance(
        result,
        TelegramReadinessRuntimeResult,
    ):
        raise TypeError("Resultado de readiness inválido.")

    resolved_probe = TelegramOperationalProbeKind(probe)

    resolved_visibility = TelegramOperationalVisibility(visibility)

    if resolved_visibility is TelegramOperationalVisibility.INTERNAL:
        payload = _internal_runtime_payload(
            result,
            probe=resolved_probe,
        )
    else:
        payload = _public_runtime_payload(
            result,
            probe=resolved_probe,
        )

    return TelegramOperationalHttpResponse(
        status_code=(_status_code_for(result.snapshot.status)),
        body=_serialize_payload(payload),
        content_type=(TELEGRAM_OPERATIONAL_JSON_CONTENT_TYPE),
        headers=_safe_headers(status=result.snapshot.status),
    )


def create_snapshot_http_response(
    snapshot: TelegramOperationalSnapshot,
    *,
    probe: (TelegramOperationalProbeKind | str),
    visibility: (TelegramOperationalVisibility | str) = (
        TelegramOperationalVisibility.PUBLIC
    ),
) -> TelegramOperationalHttpResponse:
    if not isinstance(
        snapshot,
        TelegramOperationalSnapshot,
    ):
        raise TypeError("Snapshot operacional inválido.")

    resolved_probe = TelegramOperationalProbeKind(probe)

    resolved_visibility = TelegramOperationalVisibility(visibility)

    payload = _snapshot_payload(
        snapshot,
        probe=resolved_probe,
        visibility=resolved_visibility,
    )

    return TelegramOperationalHttpResponse(
        status_code=(_status_code_for(snapshot.status)),
        body=_serialize_payload(payload),
        content_type=(TELEGRAM_OPERATIONAL_JSON_CONTENT_TYPE),
        headers=_safe_headers(status=snapshot.status),
    )


def create_safe_runtime_http_response(
    result: object,
    *,
    probe: (TelegramOperationalProbeKind | str) = (
        TelegramOperationalProbeKind.READINESS
    ),
    visibility: (TelegramOperationalVisibility | str) = (
        TelegramOperationalVisibility.PUBLIC
    ),
) -> TelegramOperationalHttpResponse:
    try:
        return create_runtime_http_response(
            result,  # type: ignore[arg-type]
            probe=probe,
            visibility=visibility,
        )

    except Exception:
        payload = {
            "schema_version": (TELEGRAM_OPERATIONAL_SCHEMA_VERSION),
            "probe": (TelegramOperationalProbeKind.READINESS.value),
            "status": (TelegramOperationalStatus.UNREADY.value),
            "ready": False,
            "reason": ("response_serialization_failure"),
        }

        return TelegramOperationalHttpResponse(
            status_code=503,
            body=_serialize_payload(payload),
            content_type=(TELEGRAM_OPERATIONAL_JSON_CONTENT_TYPE),
            headers=_safe_headers(status=(TelegramOperationalStatus.UNREADY)),
        )


__all__ = [
    "TELEGRAM_OPERATIONAL_JSON_CONTENT_TYPE",
    "TELEGRAM_OPERATIONAL_SCHEMA_VERSION",
    "TelegramOperationalHttpResponse",
    "TelegramOperationalProbeKind",
    "TelegramOperationalVisibility",
    "create_runtime_http_response",
    "create_safe_runtime_http_response",
    "create_snapshot_http_response",
]
