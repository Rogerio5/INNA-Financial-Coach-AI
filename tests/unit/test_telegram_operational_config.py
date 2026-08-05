from __future__ import annotations

from types import MappingProxyType

import pytest

from src.services.telegram_observability import (
    INTERNAL_OPERATIONS_TOKEN_ENV,
    INTERNAL_ROUTE_ENABLED_ENV,
    READINESS_CACHE_TTL_ENV,
    READINESS_CONCURRENT_WAIT_ENV,
    READINESS_EVALUATION_BUDGET_ENV,
    TelegramOperationalConfiguration,
    TelegramOperationalConfigurationError,
    load_telegram_operational_configuration,
)


STRONG_TOKEN = "Inna-Operations-2026-A8f9K2m4Q7x1Z6p3"


def test_defaults_are_secure():
    configuration = load_telegram_operational_configuration({})

    assert configuration.internal_route_enabled is False

    assert configuration.internal_operations_token is None

    assert configuration.readiness_cache_ttl_seconds == 1.0


def test_loads_valid_environment():
    configuration = load_telegram_operational_configuration(
        {
            INTERNAL_ROUTE_ENABLED_ENV: ("true"),
            INTERNAL_OPERATIONS_TOKEN_ENV: (STRONG_TOKEN),
            READINESS_CACHE_TTL_ENV: ("3"),
            READINESS_CONCURRENT_WAIT_ENV: ("0.5"),
            READINESS_EVALUATION_BUDGET_ENV: ("5"),
        }
    )

    assert configuration.internal_route_enabled is True

    assert configuration.internal_operations_token == STRONG_TOKEN

    assert configuration.readiness_cache_ttl_seconds == 3.0

    assert configuration.readiness_concurrent_wait_seconds == 0.5

    assert configuration.readiness_evaluation_budget_seconds == 5.0


@pytest.mark.parametrize(
    "value",
    [
        "true",
        "TRUE",
        "1",
        "yes",
        "on",
        "enabled",
    ],
)
def test_accepts_enabled_values(
    value,
):
    configuration = load_telegram_operational_configuration(
        {
            INTERNAL_ROUTE_ENABLED_ENV: value,
            INTERNAL_OPERATIONS_TOKEN_ENV: (STRONG_TOKEN),
        }
    )

    assert configuration.internal_route_enabled is True


@pytest.mark.parametrize(
    "value",
    [
        "false",
        "FALSE",
        "0",
        "no",
        "off",
        "disabled",
    ],
)
def test_accepts_disabled_values(
    value,
):
    configuration = load_telegram_operational_configuration(
        {
            INTERNAL_ROUTE_ENABLED_ENV: value,
        }
    )

    assert configuration.internal_route_enabled is False


def test_enabled_route_requires_token():
    with pytest.raises(TelegramOperationalConfigurationError):
        TelegramOperationalConfiguration(
            internal_route_enabled=True,
            internal_operations_token=None,
        )


@pytest.mark.parametrize(
    "token",
    [
        "short",
        "password",
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "11111111111111111111111111111111",
    ],
)
def test_rejects_weak_token(
    token,
):
    with pytest.raises(TelegramOperationalConfigurationError):
        TelegramOperationalConfiguration(
            internal_route_enabled=True,
            internal_operations_token=token,
        )


@pytest.mark.parametrize(
    (
        "field",
        "value",
    ),
    [
        (
            "readiness_cache_ttl_seconds",
            -1,
        ),
        (
            "readiness_cache_ttl_seconds",
            61,
        ),
        (
            ("readiness_concurrent_wait_seconds"),
            -0.1,
        ),
        (
            ("readiness_concurrent_wait_seconds"),
            11,
        ),
        (
            ("readiness_evaluation_budget_seconds"),
            0,
        ),
        (
            ("readiness_evaluation_budget_seconds"),
            31,
        ),
    ],
)
def test_rejects_out_of_bounds_values(
    field,
    value,
):
    values = {
        "readiness_cache_ttl_seconds": 1,
        ("readiness_concurrent_wait_seconds"): 0.25,
        ("readiness_evaluation_budget_seconds"): 2,
    }

    values[field] = value

    with pytest.raises(TelegramOperationalConfigurationError):
        TelegramOperationalConfiguration(**values)


@pytest.mark.parametrize(
    "value",
    [
        "nan",
        "inf",
        "-inf",
        "invalid",
    ],
)
def test_rejects_invalid_numbers(
    value,
):
    with pytest.raises(TelegramOperationalConfigurationError):
        TelegramOperationalConfiguration(
            readiness_cache_ttl_seconds=(value),
        )


def test_safe_dict_does_not_expose_token():
    configuration = TelegramOperationalConfiguration(
        internal_route_enabled=True,
        internal_operations_token=(STRONG_TOKEN),
    )

    payload = configuration.to_safe_dict()

    rendered = repr(payload)

    assert isinstance(
        payload,
        MappingProxyType,
    )

    assert STRONG_TOKEN not in rendered

    assert payload["internal_token_configured"] is True

    assert payload["internal_token_length"] == len(STRONG_TOKEN)


def test_disabled_route_may_have_no_token():
    configuration = TelegramOperationalConfiguration(
        internal_route_enabled=False,
        internal_operations_token=None,
    )

    assert configuration.internal_route_enabled is False
