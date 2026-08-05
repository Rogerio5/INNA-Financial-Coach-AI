from src.observability import infrastructure_health
from src.observability.neon_runtime import (
    NeonRuntimeStatus,
)
from src.observability.phoenix_runtime import (
    PhoenixRuntimeStatus,
)
from src.observability.render_runtime import (
    RenderRuntimeStatus,
)


def _neon(
    *,
    available=True,
):
    return NeonRuntimeStatus(
        configured=True,
        available=available,
        latency_ms=100.0,
        server_version="16",
        pool_status=("healthy" if available else "degraded"),
        pool_size=1,
        pool_available=1,
        pool_waiting=0,
        error_type=None,
    )


def _phoenix(
    *,
    ready=True,
):
    return PhoenixRuntimeStatus(
        initialized=True,
        enabled=True,
        ready=ready,
        project_name="inna-production",
        environment="test",
        sample_rate=0.1,
        capture_content=False,
        processor="BatchSpanProcessor",
        error=None,
    )


def _render():
    return RenderRuntimeStatus(
        running_on_render=False,
        environment="development",
        service_name="inna-financial-coach-ai",
        service_type="local-process",
        region="local",
        external_url_configured=False,
        deploy_commit="",
        instance_hash="",
        uptime_seconds=1.0,
        status="local",
    )


def test_infrastructure_health_operational(
    monkeypatch,
):
    monkeypatch.setattr(
        infrastructure_health,
        "collect_neon_runtime_status",
        lambda: _neon(),
    )
    monkeypatch.setattr(
        infrastructure_health,
        "get_phoenix_runtime_status",
        lambda: _phoenix(),
    )
    monkeypatch.setattr(
        infrastructure_health,
        "collect_render_runtime_status",
        _render,
    )

    health = infrastructure_health.collect_infrastructure_health()

    assert health.status == "operational"
    assert health.unavailable_components == ()
    assert health.degraded_components == ()


def test_infrastructure_health_degraded_without_phoenix(
    monkeypatch,
):
    monkeypatch.setattr(
        infrastructure_health,
        "collect_neon_runtime_status",
        lambda: _neon(),
    )
    monkeypatch.setattr(
        infrastructure_health,
        "get_phoenix_runtime_status",
        lambda: _phoenix(ready=False),
    )
    monkeypatch.setattr(
        infrastructure_health,
        "collect_render_runtime_status",
        _render,
    )

    health = infrastructure_health.collect_infrastructure_health()

    assert health.status == "degraded"
    assert health.degraded_components == ("phoenix",)


def test_infrastructure_health_unavailable_without_neon(
    monkeypatch,
):
    monkeypatch.setattr(
        infrastructure_health,
        "collect_neon_runtime_status",
        lambda: _neon(available=False),
    )
    monkeypatch.setattr(
        infrastructure_health,
        "get_phoenix_runtime_status",
        lambda: _phoenix(),
    )
    monkeypatch.setattr(
        infrastructure_health,
        "collect_render_runtime_status",
        _render,
    )

    health = infrastructure_health.collect_infrastructure_health()

    assert health.status == "unavailable"
    assert health.unavailable_components == ("neon",)
