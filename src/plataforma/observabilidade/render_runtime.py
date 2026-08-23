"""Metadados seguros do ambiente local e Render da INNA."""

from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass
from typing import Any

from src.compartilhado.observabilidade.phoenix.privacy import hash_identifier

_PROCESS_STARTED_AT = time.monotonic()


@dataclass(frozen=True, slots=True)
class RenderRuntimeStatus:
    running_on_render: bool
    environment: str
    service_name: str
    service_type: str
    region: str
    external_url_configured: bool
    deploy_commit: str
    instance_hash: str
    uptime_seconds: float
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safe_text(
    value: str | None,
    *,
    default: str = "",
    max_length: int = 120,
) -> str:
    normalized = str(value or "").strip()

    if not normalized:
        return default

    return normalized[:max_length]


def _short_commit(value: str | None) -> str:
    normalized = _safe_text(value)

    if not normalized:
        return ""

    return normalized[:12]


def collect_render_runtime_status() -> RenderRuntimeStatus:
    """
    Coleta somente metadados técnicos não sensíveis.

    A URL externa e o identificador da instância nunca são
    retornados em formato original.
    """

    render_flag = _safe_text(
        os.getenv("RENDER"),
    ).lower()

    running_on_render = (
        render_flag in {"true", "1", "yes"}
        or bool(os.getenv("RENDER_SERVICE_ID"))
        or bool(os.getenv("RENDER_INSTANCE_ID"))
    )

    environment = _safe_text(
        os.getenv("APP_ENV"),
        default=(
            "production"
            if running_on_render
            else "local"
        ),
    )

    service_name = _safe_text(
        os.getenv("RENDER_SERVICE_NAME"),
        default="inna-financial-coach-ai",
    )

    service_type = _safe_text(
        os.getenv("RENDER_SERVICE_TYPE"),
        default=(
            "web"
            if running_on_render
            else "local-process"
        ),
    )

    region = _safe_text(
        os.getenv("RENDER_REGION"),
        default=(
            "unknown"
            if running_on_render
            else "local"
        ),
    )

    instance_id = _safe_text(
        os.getenv("RENDER_INSTANCE_ID"),
    )

    uptime_seconds = round(
        max(
            0.0,
            time.monotonic()
            - _PROCESS_STARTED_AT,
        ),
        3,
    )

    return RenderRuntimeStatus(
        running_on_render=running_on_render,
        environment=environment,
        service_name=service_name,
        service_type=service_type,
        region=region,
        external_url_configured=bool(
            os.getenv("RENDER_EXTERNAL_URL")
        ),
        deploy_commit=_short_commit(
            os.getenv("RENDER_GIT_COMMIT")
        ),
        instance_hash=(
            hash_identifier(instance_id)
            if instance_id
            else ""
        ),
        uptime_seconds=uptime_seconds,
        status=(
            "operational"
            if running_on_render
            else "local"
        ),
    )


__all__ = [
    "RenderRuntimeStatus",
    "collect_render_runtime_status",
]
