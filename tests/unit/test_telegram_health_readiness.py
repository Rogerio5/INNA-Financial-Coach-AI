from __future__ import annotations

from types import MappingProxyType

import pytest

from src.services.telegram_observability import (
    CallableTelegramProbe,
    TelegramOperationalStatus,
    TelegramOperationalStatusService,
    TelegramProbeResult,
    TelegramProbeSeverity,
    TelegramProbeStatus,
    create_process_health_service,
)


class SequenceClock:
    def __init__(
        self,
        *values,
    ):
        self._values = iter(values)

    def __call__(
        self,
    ):
        return next(self._values)


def probe(
    *,
    name,
    severity,
    passed,
    error_category="dependency",
):
    return CallableTelegramProbe(
        name=name,
        severity=severity,
        check=lambda: passed,
        error_category=error_category,
        clock=SequenceClock(
            10.0,
            10.25,
        ),
    )


def test_probe_pass_result():
    result = probe(
        name="database",
        severity="required",
        passed=True,
    ).run()

    assert result.status is TelegramProbeStatus.PASS

    assert result.severity is TelegramProbeSeverity.REQUIRED

    assert result.error_category == "none"

    assert result.latency_seconds == 0.25


def test_probe_failure_result():
    result = probe(
        name="database",
        severity="required",
        passed=False,
        error_category="database",
    ).run()

    assert result.status is TelegramProbeStatus.FAIL

    assert result.error_category == "database"


def test_probe_exception_is_safe():
    def broken():
        raise RuntimeError("private database password")

    result = CallableTelegramProbe(
        name="database",
        severity="required",
        check=broken,
        error_category="database",
        clock=SequenceClock(
            5.0,
            5.1,
        ),
    ).run()

    rendered = repr(result.to_safe_dict())

    assert result.status is TelegramProbeStatus.FAIL

    assert "private database password" not in rendered

    assert result.details == {
        "exception": True,
    }


def test_mapping_result_supports_details():
    result = CallableTelegramProbe(
        name="queue",
        severity="optional",
        check=lambda: {
            "passed": True,
            "mode": "durable",
            "workers": 1,
        },
    ).run()

    assert result.passed
    assert result.details == {
        "mode": "durable",
        "workers": 1,
    }


def test_details_are_immutable():
    result = TelegramProbeResult(
        name="process",
        status="pass",
        severity="required",
        latency_seconds=0,
        error_category="none",
        details={
            "mode": "worker",
        },
    )

    assert isinstance(
        result.details,
        MappingProxyType,
    )

    with pytest.raises(TypeError):
        result.details["mode"] = "changed"


def test_invalid_error_category_becomes_unknown():
    result = TelegramProbeResult(
        name="process",
        status="fail",
        severity="required",
        latency_seconds=0,
        error_category=("private-user-data"),
        details={},
    )

    assert result.error_category == "unknown"


@pytest.mark.parametrize(
    "latency",
    [
        -1,
        float("nan"),
        float("inf"),
        "invalid",
    ],
)
def test_invalid_latency_becomes_zero(
    latency,
):
    result = TelegramProbeResult(
        name="process",
        status="pass",
        severity="required",
        latency_seconds=latency,
        error_category="none",
        details={},
    )

    assert result.latency_seconds == 0.0


def test_all_pass_is_healthy():
    service = TelegramOperationalStatusService(
        probes=(
            probe(
                name="process",
                severity="required",
                passed=True,
            ),
            probe(
                name="metrics",
                severity="optional",
                passed=True,
            ),
        ),
        wall_clock=lambda: 1000.0,
        monotonic_clock=(
            SequenceClock(
                1.0,
                1.5,
            )
        ),
    )

    snapshot = service.evaluate()

    assert snapshot.status is TelegramOperationalStatus.HEALTHY

    assert snapshot.ready is True

    assert snapshot.checked_at_epoch_seconds == 1000.0

    assert snapshot.total_latency_seconds == 0.5


def test_optional_failure_is_degraded():
    service = TelegramOperationalStatusService(
        probes=(
            probe(
                name="process",
                severity="required",
                passed=True,
            ),
            probe(
                name="metrics",
                severity="optional",
                passed=False,
            ),
        )
    )

    snapshot = service.evaluate()

    assert snapshot.status is TelegramOperationalStatus.DEGRADED

    assert snapshot.ready is True


def test_required_failure_is_unready():
    service = TelegramOperationalStatusService(
        probes=(
            probe(
                name="database",
                severity="required",
                passed=False,
                error_category="database",
            ),
            probe(
                name="metrics",
                severity="optional",
                passed=False,
            ),
        )
    )

    snapshot = service.evaluate()

    assert snapshot.status is TelegramOperationalStatus.UNREADY

    assert snapshot.ready is False


def test_informational_failure_does_not_degrade():
    service = TelegramOperationalStatusService(
        probes=(
            probe(
                name="process",
                severity="required",
                passed=True,
            ),
            probe(
                name="version",
                severity="informational",
                passed=False,
            ),
        )
    )

    snapshot = service.evaluate()

    assert snapshot.status is TelegramOperationalStatus.HEALTHY


def test_snapshot_safe_dict():
    service = TelegramOperationalStatusService(
        probes=(
            probe(
                name="process",
                severity="required",
                passed=True,
            ),
        ),
        wall_clock=lambda: 123.0,
    )

    payload = service.evaluate().to_safe_dict()

    assert payload["status"] == "healthy"

    assert payload["ready"] is True

    assert payload["checked_at_epoch_seconds"] == 123.0

    assert len(payload["checks"]) == 1


def test_process_health_service_is_healthy():
    snapshot = create_process_health_service().evaluate()

    assert snapshot.status is TelegramOperationalStatus.HEALTHY


def test_process_health_service_can_fail_safely():
    snapshot = create_process_health_service(
        clock_check=lambda: False,
    ).evaluate()

    assert snapshot.status is TelegramOperationalStatus.UNREADY


def test_empty_probe_collection_is_healthy():
    snapshot = TelegramOperationalStatusService(probes=()).evaluate()

    assert snapshot.status is TelegramOperationalStatus.HEALTHY


def test_probe_result_name_is_required():
    with pytest.raises(ValueError):
        TelegramProbeResult(
            name="",
            status="pass",
            severity="required",
            latency_seconds=0,
            error_category="none",
            details={},
        )


def test_callable_probe_name_is_required():
    with pytest.raises(ValueError):
        CallableTelegramProbe(
            name=" ",
            severity="required",
            check=lambda: True,
        )
