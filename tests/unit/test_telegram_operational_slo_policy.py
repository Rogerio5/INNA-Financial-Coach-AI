from __future__ import annotations

from types import MappingProxyType

import pytest

from src.services.telegram_observability import (
    TelegramAvailabilitySlo,
    TelegramBacklogSlo,
    TelegramDeadLetterSlo,
    TelegramLatencySlo,
    TelegramMetricFreshnessSlo,
    TelegramOperationalSloPolicy,
    TelegramSloPolicyError,
    TelegramSloSeverity,
    TelegramSloWindows,
    TelegramSuccessRateSlo,
    calculate_burn_rate,
    classify_burn_rate,
    classify_threshold,
)


def test_default_policy_values():
    policy = (
        TelegramOperationalSloPolicy()
    )

    assert (
        policy
        .availability
        .objective_ratio
        == 0.995
    )

    assert (
        policy
        .success_rate
        .objective_ratio
        == 0.99
    )

    assert (
        policy.latency.p95_seconds
        == 2.0
    )

    assert (
        policy.latency.p99_seconds
        == 5.0
    )

    assert (
        policy.backlog.warning_jobs
        == 25
    )

    assert (
        policy.backlog.critical_jobs
        == 100
    )


def test_availability_error_budget():
    slo = TelegramAvailabilitySlo(
        objective_ratio=0.995,
        window_days=30,
    )

    assert (
        slo.error_budget_ratio
        == pytest.approx(
            0.005
        )
    )

    assert (
        slo.window_seconds
        == 2592000
    )

    assert (
        slo.allowed_unavailable_seconds
        == pytest.approx(
            12960.0
        )
    )


def test_success_failure_budget():
    slo = TelegramSuccessRateSlo(
        objective_ratio=0.99
    )

    assert (
        slo.failure_budget_ratio
        == pytest.approx(
            0.01
        )
    )


def test_safe_dict_is_immutable():
    payload = (
        TelegramOperationalSloPolicy()
        .to_safe_dict()
    )

    assert isinstance(
        payload,
        MappingProxyType,
    )

    with pytest.raises(
        TypeError
    ):
        payload[
            "availability"
        ] = {}


def test_safe_dict_has_expected_sections():
    payload = (
        TelegramOperationalSloPolicy()
        .to_safe_dict()
    )

    assert set(
        payload
    ) == {
        "availability",
        "success_rate",
        "latency",
        "backlog",
        "dead_letter",
        "freshness",
        "windows",
    }


@pytest.mark.parametrize(
    (
        "value",
        "expected",
    ),
    [
        (
            0,
            None,
        ),
        (
            24,
            None,
        ),
        (
            25,
            TelegramSloSeverity.WARNING,
        ),
        (
            99,
            TelegramSloSeverity.WARNING,
        ),
        (
            100,
            TelegramSloSeverity.CRITICAL,
        ),
        (
            500,
            TelegramSloSeverity.CRITICAL,
        ),
    ],
)
def test_classify_threshold(
    value,
    expected,
):
    assert (
        classify_threshold(
            value=value,
            warning_threshold=25,
            critical_threshold=100,
        )
        is expected
    )


def test_calculate_burn_rate():
    burn_rate = calculate_burn_rate(
        observed_error_ratio=0.01,
        objective_ratio=0.995,
    )

    assert burn_rate == pytest.approx(
        2.0
    )


@pytest.mark.parametrize(
    (
        "burn_rate",
        "expected",
    ),
    [
        (
            0.5,
            None,
        ),
        (
            1.99,
            None,
        ),
        (
            2.0,
            TelegramSloSeverity.WARNING,
        ),
        (
            5.99,
            TelegramSloSeverity.WARNING,
        ),
        (
            6.0,
            TelegramSloSeverity.CRITICAL,
        ),
    ],
)
def test_classify_burn_rate(
    burn_rate,
    expected,
):
    assert (
        classify_burn_rate(
            burn_rate=burn_rate
        )
        is expected
    )


@pytest.mark.parametrize(
    "objective",
    [
        0.0,
        0.5,
        0.899,
        1.0,
        1.1,
        float("nan"),
        float("inf"),
    ],
)
def test_invalid_availability_objective(
    objective,
):
    with pytest.raises(
        TelegramSloPolicyError
    ):
        TelegramAvailabilitySlo(
            objective_ratio=objective
        )


def test_critical_burn_must_exceed_warning():
    with pytest.raises(
        TelegramSloPolicyError
    ):
        TelegramAvailabilitySlo(
            warning_burn_rate=6,
            critical_burn_rate=6,
        )


def test_p99_must_not_be_below_p95():
    with pytest.raises(
        TelegramSloPolicyError
    ):
        TelegramLatencySlo(
            p95_seconds=5,
            p99_seconds=2,
        )


def test_backlog_critical_must_exceed_warning():
    with pytest.raises(
        TelegramSloPolicyError
    ):
        TelegramBacklogSlo(
            warning_jobs=100,
            critical_jobs=100,
        )


def test_dead_letter_critical_must_exceed_warning():
    with pytest.raises(
        TelegramSloPolicyError
    ):
        TelegramDeadLetterSlo(
            warning_count=5,
            critical_count=5,
        )


def test_freshness_critical_must_exceed_warning():
    with pytest.raises(
        TelegramSloPolicyError
    ):
        TelegramMetricFreshnessSlo(
            warning_seconds=300,
            critical_seconds=120,
        )


def test_windows_must_be_ordered():
    with pytest.raises(
        TelegramSloPolicyError
    ):
        TelegramSloWindows(
            short_window_seconds=3600,
            medium_window_seconds=300,
            long_window_seconds=100,
        )


@pytest.mark.parametrize(
    "value",
    [
        -1,
        float("nan"),
        float("inf"),
        "invalid",
    ],
)
def test_classification_rejects_invalid_value(
    value,
):
    with pytest.raises(
        TelegramSloPolicyError
    ):
        classify_threshold(
            value=value,
            warning_threshold=25,
            critical_threshold=100,
        )


def test_classification_rejects_invalid_threshold_order():
    with pytest.raises(
        TelegramSloPolicyError
    ):
        classify_threshold(
            value=10,
            warning_threshold=100,
            critical_threshold=25,
        )


@pytest.mark.parametrize(
    (
        "error_ratio",
        "objective",
    ),
    [
        (
            -0.1,
            0.995,
        ),
        (
            1.1,
            0.995,
        ),
        (
            0.1,
            1.0,
        ),
        (
            float("nan"),
            0.995,
        ),
    ],
)
def test_invalid_burn_rate_input(
    error_ratio,
    objective,
):
    with pytest.raises(
        TelegramSloPolicyError
    ):
        calculate_burn_rate(
            observed_error_ratio=(
                error_ratio
            ),
            objective_ratio=objective,
        )


def test_policy_has_no_secret_fields():
    rendered = repr(
        TelegramOperationalSloPolicy()
        .to_safe_dict()
    ).lower()

    forbidden = {
        "token",
        "password",
        "payload",
        "chat_id",
        "update_id",
        "claim_token",
    }

    for value in forbidden:
        assert value not in rendered

def test_calculated_burn_rate_at_warning_boundary():
    burn_rate = calculate_burn_rate(
        observed_error_ratio=0.01,
        objective_ratio=0.995,
    )

    assert burn_rate == pytest.approx(
        2.0
    )

    assert (
        classify_burn_rate(
            burn_rate=burn_rate
        )
        is TelegramSloSeverity.WARNING
    )


def test_float_value_immediately_below_boundary_within_tolerance():
    value = 1.9999999999999998

    assert (
        classify_threshold(
            value=value,
            warning_threshold=2.0,
            critical_threshold=6.0,
        )
        is TelegramSloSeverity.WARNING
    )


def test_value_materially_below_boundary_remains_normal():
    value = 1.999

    assert (
        classify_threshold(
            value=value,
            warning_threshold=2.0,
            critical_threshold=6.0,
        )
        is None
    )

