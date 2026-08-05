"""Saúde consolidada da infraestrutura da INNA."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .neon_runtime import (
    NeonRuntimeStatus,
    collect_neon_runtime_status,
)
from .phoenix_runtime import (
    PhoenixRuntimeStatus,
    get_phoenix_runtime_status,
)
from .render_runtime import (
    RenderRuntimeStatus,
    collect_render_runtime_status,
)


@dataclass(frozen=True, slots=True)
class InfrastructureHealth:
    status: str
    neon: NeonRuntimeStatus
    phoenix: PhoenixRuntimeStatus
    render: RenderRuntimeStatus
    unavailable_components: tuple[str, ...]
    degraded_components: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _phoenix_available(
    status: PhoenixRuntimeStatus,
) -> bool:
    return bool(status.initialized and status.enabled and status.ready)


def collect_infrastructure_health() -> InfrastructureHealth:
    """
    Consolida os componentes sem interromper o dashboard.

    Estados:
    - operational: todos os componentes necessários saudáveis;
    - degraded: existe componente opcional ou parcial com falha;
    - unavailable: banco de dados indisponível.
    """

    neon = collect_neon_runtime_status()
    phoenix = get_phoenix_runtime_status()
    render = collect_render_runtime_status()

    unavailable: list[str] = []
    degraded: list[str] = []

    if not neon.available:
        unavailable.append("neon")

    if not _phoenix_available(phoenix):
        degraded.append("phoenix")

    if render.running_on_render and render.status != "operational":
        degraded.append("render")

    if unavailable:
        overall_status = "unavailable"
    elif degraded:
        overall_status = "degraded"
    else:
        overall_status = "operational"

    return InfrastructureHealth(
        status=overall_status,
        neon=neon,
        phoenix=phoenix,
        render=render,
        unavailable_components=tuple(unavailable),
        degraded_components=tuple(degraded),
    )


__all__ = [
    "InfrastructureHealth",
    "collect_infrastructure_health",
]
