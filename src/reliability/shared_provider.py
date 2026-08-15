"""Provider compartilhado de Reliability da INNA."""

from __future__ import annotations

import math
import os
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from .production_tracker import (
    PRODUCTION_RELIABILITY_POLICIES,
    ProductionReliabilitySnapshot,
    ProductionReliabilityTracker,
    get_production_reliability_tracker,
)
from .repository import (
    ProductionReliabilityWindow,
    load_production_reliability_window,
)


class ReliabilityDataSource(StrEnum):
    SHARED_CACHE = "shared_cache"
    LOCAL_FALLBACK = "local_fallback"


@dataclass(
    frozen=True,
    slots=True,
)
class SharedReliabilitySnapshot:
    operation: str

    source: ReliabilityDataSource
    provider_enabled: bool

    local_snapshot: ProductionReliabilitySnapshot

    shared_window: (
        ProductionReliabilityWindow
        | None
    )

    cache_age_seconds: float | None
    cache_stale: bool

    database_unavailable: bool
    refresh_in_flight: bool

    def to_safe_dict(
        self,
    ) -> Mapping[str, object]:
        shared = self.shared_window

        return MappingProxyType(
            {
                "operation": self.operation,
                "source": self.source.value,
                "provider_enabled": (
                    self.provider_enabled
                ),
                "cache_age_seconds": (
                    self.cache_age_seconds
                ),
                "cache_stale": (
                    self.cache_stale
                ),
                "database_unavailable": (
                    self.database_unavailable
                ),
                "refresh_in_flight": (
                    self.refresh_in_flight
                ),
                "local_total_operations": (
                    self.local_snapshot
                    .total_operations
                ),
                "shared_total_operations": (
                    None
                    if shared is None
                    else shared.total_operations
                ),
                "shared_failed_operations": (
                    None
                    if shared is None
                    else shared.failed_operations
                ),
                "shared_circuit_rejections": (
                    None
                    if shared is None
                    else shared.circuit_rejections
                ),
            }
        )


@dataclass(
    frozen=True,
    slots=True,
)
class _CacheEntry:
    window: ProductionReliabilityWindow
    refreshed_at: float


ThreadStarter = Callable[
    [
        str,
        Callable[[], None],
    ],
    None,
]


def _default_thread_starter(
    name: str,
    target: Callable[[], None],
) -> None:
    thread = threading.Thread(
        target=target,
        name=name,
        daemon=True,
    )

    thread.start()


def _env_bool(
    name: str,
    *,
    default: bool,
) -> bool:
    raw = os.getenv(name)

    if raw is None:
        return default

    normalized = raw.strip().lower()

    if normalized in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return True

    if normalized in {
        "0",
        "false",
        "no",
        "off",
    }:
        return False

    return default


def _env_positive_float(
    name: str,
    *,
    default: float,
) -> float:
    raw = os.getenv(name)

    if raw is None:
        return default

    try:
        parsed = float(raw)
    except ValueError:
        return default

    if (
        not math.isfinite(parsed)
        or parsed <= 0
    ):
        return default

    return parsed


class SharedReliabilityProvider:
    """
    Une o tracker local ao ledger compartilhado.

    O método snapshot() nunca executa SELECT síncrono.

    Em cache miss ou cache vencendo:
    - retorna imediatamente;
    - inicia no máximo um refresh por operação;
    - refresh ocorre em thread daemon curta;
    - falha de banco não propaga ao caller.
    """

    def __init__(
        self,
        *,
        enabled: bool,
        tracker: (
            ProductionReliabilityTracker
            | None
        ) = None,
        window_loader: Callable[
            ...,
            ProductionReliabilityWindow
        ] = (
            load_production_reliability_window
        ),
        cache_ttl_seconds: float = 5.0,
        max_stale_seconds: float = 30.0,
        clock: Callable[
            [],
            float,
        ] = time.monotonic,
        thread_starter: (
            ThreadStarter
            | None
        ) = None,
    ) -> None:
        cache_ttl_seconds = float(
            cache_ttl_seconds
        )

        max_stale_seconds = float(
            max_stale_seconds
        )

        if (
            not math.isfinite(
                cache_ttl_seconds
            )
            or cache_ttl_seconds <= 0
        ):
            raise ValueError(
                "cache_ttl_seconds must be "
                "finite and > 0."
            )

        if (
            not math.isfinite(
                max_stale_seconds
            )
            or max_stale_seconds
            < cache_ttl_seconds
        ):
            raise ValueError(
                "max_stale_seconds must be "
                "finite and >= cache TTL."
            )

        self._enabled = bool(
            enabled
        )

        self._tracker = (
            tracker
            or get_production_reliability_tracker()
        )

        self._window_loader = (
            window_loader
        )

        self._cache_ttl_seconds = (
            cache_ttl_seconds
        )

        self._max_stale_seconds = (
            max_stale_seconds
        )

        self._clock = clock

        self._thread_starter = (
            thread_starter
            or _default_thread_starter
        )

        self._lock = threading.RLock()

        self._cache: dict[
            str,
            _CacheEntry,
        ] = {}

        self._refreshing: set[
            str
        ] = set()

        self._database_unavailable: dict[
            str,
            bool,
        ] = {}

    @property
    def enabled(
        self,
    ) -> bool:
        return self._enabled

    def _validate_operation(
        self,
        operation: str,
    ) -> str:
        normalized = str(
            operation
        ).strip()

        if (
            normalized
            not in PRODUCTION_RELIABILITY_POLICIES
        ):
            raise ValueError(
                "Operation is not a tracked "
                "production reliability boundary."
            )

        return normalized

    def _refresh_once(
        self,
        operation: str,
    ) -> bool:
        local_snapshot = (
            self._tracker.snapshot(
                operation
            )
        )

        try:
            window = (
                self._window_loader(
                    operation=operation,
                    window_seconds=(
                        local_snapshot
                        .window_seconds
                    ),
                )
            )

        except Exception:
            with self._lock:
                self._database_unavailable[
                    operation
                ] = True

            return False

        refreshed_at = self._clock()

        with self._lock:
            self._cache[
                operation
            ] = _CacheEntry(
                window=window,
                refreshed_at=refreshed_at,
            )

            self._database_unavailable[
                operation
            ] = False

        return True

    def _refresh_worker(
        self,
        operation: str,
    ) -> None:
        try:
            self._refresh_once(
                operation
            )

        finally:
            with self._lock:
                self._refreshing.discard(
                    operation
                )

    def _schedule_refresh(
        self,
        operation: str,
    ) -> bool:
        if not self._enabled:
            return False

        with self._lock:
            if (
                operation
                in self._refreshing
            ):
                return False

            self._refreshing.add(
                operation
            )

        try:
            self._thread_starter(
                (
                    "inna-shared-reliability-"
                    f"{operation}"
                ),
                lambda: (
                    self._refresh_worker(
                        operation
                    )
                ),
            )

        except Exception:
            with self._lock:
                self._refreshing.discard(
                    operation
                )

                self._database_unavailable[
                    operation
                ] = True

            return False

        return True

    def refresh_now(
        self,
        operation: str,
    ) -> bool:
        """
        Refresh explícito e síncrono.

        Uso previsto:
        - smoke tests;
        - health diagnostics;
        - ferramentas administrativas.

        Não deve ser chamado pelo caminho crítico.
        """
        operation = (
            self._validate_operation(
                operation
            )
        )

        if not self._enabled:
            return False

        with self._lock:
            if (
                operation
                in self._refreshing
            ):
                return False

            self._refreshing.add(
                operation
            )

        try:
            return self._refresh_once(
                operation
            )

        finally:
            with self._lock:
                self._refreshing.discard(
                    operation
                )

    def snapshot(
        self,
        operation: str,
    ) -> SharedReliabilitySnapshot:
        """
        Retorna imediatamente.

        Nenhuma consulta PostgreSQL é executada
        diretamente neste método.
        """
        operation = (
            self._validate_operation(
                operation
            )
        )

        local_snapshot = (
            self._tracker.snapshot(
                operation
            )
        )

        if not self._enabled:
            return SharedReliabilitySnapshot(
                operation=operation,
                source=(
                    ReliabilityDataSource
                    .LOCAL_FALLBACK
                ),
                provider_enabled=False,
                local_snapshot=(
                    local_snapshot
                ),
                shared_window=None,
                cache_age_seconds=None,
                cache_stale=False,
                database_unavailable=False,
                refresh_in_flight=False,
            )

        now = self._clock()

        with self._lock:
            entry = self._cache.get(
                operation
            )

            refreshing = (
                operation
                in self._refreshing
            )

            database_unavailable = (
                self
                ._database_unavailable
                .get(
                    operation,
                    False,
                )
            )

        age: float | None = None

        if entry is not None:
            age = max(
                0.0,
                now - entry.refreshed_at,
            )

        should_refresh = (
            entry is None
            or (
                age is not None
                and age
                > self._cache_ttl_seconds
            )
        )

        scheduled = False

        if (
            should_refresh
            and not refreshing
        ):
            scheduled = (
                self._schedule_refresh(
                    operation
                )
            )

        refresh_in_flight = (
            refreshing
            or scheduled
        )

        shared_usable = (
            entry is not None
            and age is not None
            and age
            <= self._max_stale_seconds
        )

        if shared_usable:
            return SharedReliabilitySnapshot(
                operation=operation,
                source=(
                    ReliabilityDataSource
                    .SHARED_CACHE
                ),
                provider_enabled=True,
                local_snapshot=(
                    local_snapshot
                ),
                shared_window=(
                    entry.window
                ),
                cache_age_seconds=age,
                cache_stale=(
                    age
                    > self._cache_ttl_seconds
                ),
                database_unavailable=(
                    database_unavailable
                ),
                refresh_in_flight=(
                    refresh_in_flight
                ),
            )

        return SharedReliabilitySnapshot(
            operation=operation,
            source=(
                ReliabilityDataSource
                .LOCAL_FALLBACK
            ),
            provider_enabled=True,
            local_snapshot=(
                local_snapshot
            ),
            shared_window=None,
            cache_age_seconds=age,
            cache_stale=(
                entry is not None
            ),
            database_unavailable=(
                database_unavailable
            ),
            refresh_in_flight=(
                refresh_in_flight
            ),
        )


_SINGLETON_LOCK = threading.Lock()

_SHARED_RELIABILITY_PROVIDER: (
    SharedReliabilityProvider
    | None
) = None


def _build_provider_from_environment(
) -> SharedReliabilityProvider:
    ttl = _env_positive_float(
        (
            "INNA_RELIABILITY_"
            "SHARED_CACHE_TTL_SECONDS"
        ),
        default=5.0,
    )

    max_stale = (
        _env_positive_float(
            (
                "INNA_RELIABILITY_"
                "SHARED_MAX_STALE_SECONDS"
            ),
            default=30.0,
        )
    )

    if max_stale < ttl:
        max_stale = max(
            ttl,
            30.0,
        )

    return SharedReliabilityProvider(
        enabled=_env_bool(
            (
                "INNA_RELIABILITY_"
                "SHARED_PROVIDER_ENABLED"
            ),
            default=False,
        ),
        cache_ttl_seconds=ttl,
        max_stale_seconds=max_stale,
    )


def get_shared_reliability_provider(
) -> SharedReliabilityProvider:
    global _SHARED_RELIABILITY_PROVIDER

    current = (
        _SHARED_RELIABILITY_PROVIDER
    )

    if current is not None:
        return current

    with _SINGLETON_LOCK:
        current = (
            _SHARED_RELIABILITY_PROVIDER
        )

        if current is None:
            current = (
                _build_provider_from_environment()
            )

            _SHARED_RELIABILITY_PROVIDER = (
                current
            )

        return current


__all__ = [
    "ReliabilityDataSource",
    "SharedReliabilityProvider",
    "SharedReliabilitySnapshot",
    "get_shared_reliability_provider",
]
