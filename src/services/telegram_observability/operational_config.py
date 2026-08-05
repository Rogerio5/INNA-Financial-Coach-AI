from __future__ import annotations

import math
import os
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


INTERNAL_ROUTE_ENABLED_ENV = "INNA_INTERNAL_READY_ENABLED"

INTERNAL_OPERATIONS_TOKEN_ENV = "INNA_INTERNAL_OPERATIONS_TOKEN"

READINESS_CACHE_TTL_ENV = "INNA_READINESS_CACHE_TTL_SECONDS"

READINESS_CONCURRENT_WAIT_ENV = "INNA_READINESS_CONCURRENT_WAIT_SECONDS"

READINESS_EVALUATION_BUDGET_ENV = "INNA_READINESS_EVALUATION_BUDGET_SECONDS"


DEFAULT_READINESS_CACHE_TTL_SECONDS = 1.0

DEFAULT_READINESS_CONCURRENT_WAIT_SECONDS = 0.25

DEFAULT_READINESS_EVALUATION_BUDGET_SECONDS = 2.0

MINIMUM_INTERNAL_TOKEN_LENGTH = 32

MAXIMUM_READINESS_CACHE_TTL_SECONDS = 60.0

MAXIMUM_READINESS_CONCURRENT_WAIT_SECONDS = 10.0

MAXIMUM_READINESS_EVALUATION_BUDGET_SECONDS = 30.0


class TelegramOperationalConfigurationError(ValueError):
    pass


def _parse_boolean(
    *,
    name: str,
    value: object,
    default: bool,
) -> bool:
    if value is None:
        return default

    if isinstance(
        value,
        bool,
    ):
        return value

    normalized = str(value).strip().lower()

    truthy = {
        "1",
        "true",
        "yes",
        "on",
        "enabled",
    }

    falsy = {
        "0",
        "false",
        "no",
        "off",
        "disabled",
    }

    if normalized in truthy:
        return True

    if normalized in falsy:
        return False

    raise TelegramOperationalConfigurationError(
        f"{name} possui valor booleano inválido."
    )


def _parse_bounded_float(
    *,
    name: str,
    value: object,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    if value is None:
        normalized = float(default)
    else:
        try:
            normalized = float(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise (
                TelegramOperationalConfigurationError(f"{name} deve ser numérico.")
            ) from exc

    if math.isnan(normalized) or math.isinf(normalized):
        raise TelegramOperationalConfigurationError(f"{name} deve ser finito.")

    if normalized < minimum:
        raise TelegramOperationalConfigurationError(
            f"{name} deve ser maior ou igual a {minimum}."
        )

    if normalized > maximum:
        raise TelegramOperationalConfigurationError(
            f"{name} deve ser menor ou igual a {maximum}."
        )

    return normalized


def _normalize_token(
    value: object,
) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()

    if not normalized:
        return None

    return normalized


def _validate_internal_token(
    *,
    enabled: bool,
    token: str | None,
) -> None:
    if not enabled:
        return

    if token is None:
        raise TelegramOperationalConfigurationError(
            "A rota interna está habilitada, mas "
            "INNA_INTERNAL_OPERATIONS_TOKEN não foi "
            "configurado."
        )

    if len(token) < MINIMUM_INTERNAL_TOKEN_LENGTH:
        raise TelegramOperationalConfigurationError(
            "INNA_INTERNAL_OPERATIONS_TOKEN deve "
            f"possuir ao menos "
            f"{MINIMUM_INTERNAL_TOKEN_LENGTH} "
            "caracteres."
        )

    weak_tokens = {
        "password",
        "changeme",
        "secret",
        "token",
        "admin",
        "development",
        "test",
    }

    lowered = token.lower()

    if lowered in weak_tokens:
        raise TelegramOperationalConfigurationError(
            "INNA_INTERNAL_OPERATIONS_TOKEN é fraco."
        )

    if len(set(token)) < 8:
        raise TelegramOperationalConfigurationError(
            "INNA_INTERNAL_OPERATIONS_TOKEN possui baixa diversidade."
        )


@dataclass(
    frozen=True,
    slots=True,
)
class TelegramOperationalConfiguration:
    internal_route_enabled: bool = False

    internal_operations_token: str | None = None

    readiness_cache_ttl_seconds: float = DEFAULT_READINESS_CACHE_TTL_SECONDS

    readiness_concurrent_wait_seconds: float = DEFAULT_READINESS_CONCURRENT_WAIT_SECONDS

    readiness_evaluation_budget_seconds: float = (
        DEFAULT_READINESS_EVALUATION_BUDGET_SECONDS
    )

    def __post_init__(
        self,
    ) -> None:
        enabled = _parse_boolean(
            name=("internal_route_enabled"),
            value=(self.internal_route_enabled),
            default=False,
        )

        token = _normalize_token(self.internal_operations_token)

        cache_ttl = _parse_bounded_float(
            name=("readiness_cache_ttl_seconds"),
            value=(self.readiness_cache_ttl_seconds),
            default=(DEFAULT_READINESS_CACHE_TTL_SECONDS),
            minimum=0.0,
            maximum=(MAXIMUM_READINESS_CACHE_TTL_SECONDS),
        )

        concurrent_wait = _parse_bounded_float(
            name=("readiness_concurrent_wait_seconds"),
            value=(self.readiness_concurrent_wait_seconds),
            default=(DEFAULT_READINESS_CONCURRENT_WAIT_SECONDS),
            minimum=0.0,
            maximum=(MAXIMUM_READINESS_CONCURRENT_WAIT_SECONDS),
        )

        evaluation_budget = _parse_bounded_float(
            name=("readiness_evaluation_budget_seconds"),
            value=(self.readiness_evaluation_budget_seconds),
            default=(DEFAULT_READINESS_EVALUATION_BUDGET_SECONDS),
            minimum=0.001,
            maximum=(MAXIMUM_READINESS_EVALUATION_BUDGET_SECONDS),
        )

        _validate_internal_token(
            enabled=enabled,
            token=token,
        )

        object.__setattr__(
            self,
            "internal_route_enabled",
            enabled,
        )

        object.__setattr__(
            self,
            "internal_operations_token",
            token,
        )

        object.__setattr__(
            self,
            "readiness_cache_ttl_seconds",
            cache_ttl,
        )

        object.__setattr__(
            self,
            "readiness_concurrent_wait_seconds",
            concurrent_wait,
        )

        object.__setattr__(
            self,
            "readiness_evaluation_budget_seconds",
            evaluation_budget,
        )

    def to_safe_dict(
        self,
    ) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "internal_route_enabled": (self.internal_route_enabled),
                "internal_token_configured": (
                    self.internal_operations_token is not None
                ),
                "internal_token_length": (
                    len(self.internal_operations_token)
                    if (self.internal_operations_token is not None)
                    else 0
                ),
                "readiness_cache_ttl_seconds": (self.readiness_cache_ttl_seconds),
                ("readiness_concurrent_wait_seconds"): (
                    self.readiness_concurrent_wait_seconds
                ),
                ("readiness_evaluation_budget_seconds"): (
                    self.readiness_evaluation_budget_seconds
                ),
            }
        )


def load_telegram_operational_configuration(
    environment: (Mapping[str, str] | None) = None,
) -> TelegramOperationalConfiguration:
    resolved_environment = os.environ if environment is None else environment

    return TelegramOperationalConfiguration(
        internal_route_enabled=(resolved_environment.get(INTERNAL_ROUTE_ENABLED_ENV)),
        internal_operations_token=(
            resolved_environment.get(INTERNAL_OPERATIONS_TOKEN_ENV)
        ),
        readiness_cache_ttl_seconds=(resolved_environment.get(READINESS_CACHE_TTL_ENV)),
        readiness_concurrent_wait_seconds=(
            resolved_environment.get(READINESS_CONCURRENT_WAIT_ENV)
        ),
        readiness_evaluation_budget_seconds=(
            resolved_environment.get(READINESS_EVALUATION_BUDGET_ENV)
        ),
    )


__all__ = [
    "DEFAULT_READINESS_CACHE_TTL_SECONDS",
    "DEFAULT_READINESS_CONCURRENT_WAIT_SECONDS",
    "DEFAULT_READINESS_EVALUATION_BUDGET_SECONDS",
    "INTERNAL_OPERATIONS_TOKEN_ENV",
    "INTERNAL_ROUTE_ENABLED_ENV",
    "MINIMUM_INTERNAL_TOKEN_LENGTH",
    "READINESS_CACHE_TTL_ENV",
    "READINESS_CONCURRENT_WAIT_ENV",
    "READINESS_EVALUATION_BUDGET_ENV",
    "TelegramOperationalConfiguration",
    "TelegramOperationalConfigurationError",
    "load_telegram_operational_configuration",
]
