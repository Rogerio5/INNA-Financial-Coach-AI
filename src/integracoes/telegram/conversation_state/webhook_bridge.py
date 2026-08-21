from __future__ import annotations

import threading
import time
from functools import wraps

from collections.abc import (
    Callable,
    Mapping,
)
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Any,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from src.services.telegram_observability import (
    NoOpTelegramConversationMetrics,
    NoOpTelegramOperationalEventSink,
    TelegramConversationMetricRecord,
    TelegramConversationMetrics,
    TelegramOperationalEvent,
    TelegramOperationalEventSink,
    sanitize_event_fields,
)

from .contracts import (
    DEFAULT_STATE_TTL_SECONDS,
    TelegramConversationStateConsistencyError,
    TelegramConversationStateError,
    TelegramConversationStateUnavailableError,
    TelegramConversationStateValidationError,
    normalize_telegram_language,
    normalize_telegram_state,
    validate_cleanup_limit,
    validate_state_ttl_seconds,
    validate_telegram_identity,
)

from .runtime import (
    TelegramConversationSession,
    create_postgres_telegram_conversation_state_runtime,
)


_T = TypeVar(
    "_T"
)


@runtime_checkable
class TelegramConversationStateRuntimePort(
    Protocol
):
    def load_session(
        self,
        telegram_user_id: int,
        chat_id: int,
    ) -> TelegramConversationSession | None:
        ...

    def open_session(
        self,
        telegram_user_id: int,
        chat_id: int,
        initial_state: Mapping[str, Any],
        language: str | None = None,
        ttl_seconds: int | None = None,
    ) -> TelegramConversationSession:
        ...

    def save_session(
        self,
        session: TelegramConversationSession,
        *,
        ttl_seconds: int | None = None,
        only_if_changed: bool = True,
    ) -> TelegramConversationSession:
        ...

    def reload_session(
        self,
        session: TelegramConversationSession,
    ) -> TelegramConversationSession | None:
        ...

    def delete_session(
        self,
        session: TelegramConversationSession,
    ) -> bool:
        ...

    def delete_identity(
        self,
        telegram_user_id: int,
        chat_id: int,
    ) -> bool:
        ...

    def cleanup_expired(
        self,
        limit: int = 100,
    ) -> int:
        ...


def _validate_session(
    value: Any,
    *,
    telegram_user_id: int | None = None,
    chat_id: int | None = None,
) -> TelegramConversationSession:
    if not isinstance(
        value,
        TelegramConversationSession,
    ):
        raise TelegramConversationStateConsistencyError(
            "Sessão retornada pelo runtime inválida."
        )

    if value.deleted:
        raise TelegramConversationStateConsistencyError(
            "Runtime retornou uma sessão removida."
        )

    if (
        telegram_user_id is not None
        and value.telegram_user_id
        != telegram_user_id
    ):
        raise TelegramConversationStateConsistencyError(
            "Runtime alterou o telegram_user_id."
        )

    if (
        chat_id is not None
        and value.chat_id
        != chat_id
    ):
        raise TelegramConversationStateConsistencyError(
            "Runtime alterou o chat_id."
        )

    return value



_BRIDGE_EVENT_NAMES = {
    "load_or_open_session": (
        "telegram_session_load_completed"
    ),
    "save_session": (
        "telegram_session_save_completed"
    ),
    "reload_session": (
        "telegram_session_reload_completed"
    ),
    "delete_session": (
        "telegram_session_delete_completed"
    ),
    "resolve_language": (
        "telegram_language_resolution_completed"
    ),
}


def _classify_observability_error(
    error: BaseException,
) -> str:
    error_name = type(
        error
    ).__name__.lower()

    if "conflict" in error_name:
        return "optimistic_conflict"

    if "timeout" in error_name:
        return "timeout"

    if "unavailable" in error_name:
        return "unavailable"

    if "validation" in error_name:
        return "validation"

    if "identity" in error_name:
        return "identity"

    if "security" in error_name:
        return "security"

    if (
        "repository" in error_name
        or "persistence" in error_name
        or "conversationstate" in error_name
    ):
        return "persistence"

    return "unknown"


def _safe_duration_ms(
    *,
    clock: Callable[[], float],
    started_at: float,
) -> float:
    try:
        finished_at = float(
            clock()
        )

        duration_ms = (
            finished_at
            - float(started_at)
        ) * 1000.0

    except Exception:
        return 0.0

    return max(
        0.0,
        duration_ms,
    )


def _safe_record_bridge_metric(
    bridge: Any,
    record: TelegramConversationMetricRecord,
) -> None:
    try:
        bridge.metrics.record_operation(
            record
        )

    except Exception:
        # Telemetria nunca interrompe
        # a operação principal.
        return


def _safe_emit_bridge_event(
    bridge: Any,
    event: TelegramOperationalEvent,
) -> None:
    try:
        bridge.event_sink.emit(
            event
        )

    except Exception:
        # Telemetria nunca interrompe
        # a operação principal.
        return


def _observe_bridge_operation(
    operation_name: str,
):
    if operation_name not in _BRIDGE_EVENT_NAMES:
        raise ValueError(
            "Operação observável inválida: "
            f"{operation_name!r}."
        )

    event_name = _BRIDGE_EVENT_NAMES[
        operation_name
    ]

    def decorator(
        method: Callable[..., _T],
    ) -> Callable[..., _T]:
        @wraps(method)
        def wrapped(
            self: Any,
            *args: Any,
            **kwargs: Any,
        ) -> _T:
            try:
                started_at = float(
                    self.clock()
                )

            except Exception:
                started_at = 0.0

            try:
                result = method(
                    self,
                    *args,
                    **kwargs,
                )

            except Exception as error:
                duration_ms = (
                    _safe_duration_ms(
                        clock=self.clock,
                        started_at=started_at,
                    )
                )

                error_category = (
                    _classify_observability_error(
                        error
                    )
                )

                is_conflict = (
                    error_category
                    == "optimistic_conflict"
                )

                outcome = (
                    "conflict"
                    if is_conflict
                    else "error"
                )

                record = (
                    TelegramConversationMetricRecord(
                        operation=operation_name,
                        component="bridge",
                        outcome=outcome,
                        duration_ms=duration_ms,
                        error_category=(
                            error_category
                        ),
                        conflict_recovered=(
                            False
                            if is_conflict
                            else None
                        ),
                    )
                )

                _safe_record_bridge_metric(
                    self,
                    record,
                )

                failure_event_name = (
                    "telegram_session_save_conflict"
                    if (
                        operation_name
                        == "save_session"
                        and is_conflict
                    )
                    else event_name
                )

                _safe_emit_bridge_event(
                    self,
                    TelegramOperationalEvent(
                        name=failure_event_name,
                        level=(
                            "warning"
                            if is_conflict
                            else "error"
                        ),
                        component="bridge",
                        outcome=outcome,
                        fields=sanitize_event_fields(
                            {
                                "operation": (
                                    operation_name
                                ),
                                "duration_ms": (
                                    duration_ms
                                ),
                                "error_category": (
                                    error_category
                                ),
                                "conflict_recovered": (
                                    False
                                    if is_conflict
                                    else None
                                ),
                            }
                        ),
                    ),
                )

                raise

            duration_ms = _safe_duration_ms(
                clock=self.clock,
                started_at=started_at,
            )

            _safe_record_bridge_metric(
                self,
                TelegramConversationMetricRecord(
                    operation=operation_name,
                    component="bridge",
                    outcome="success",
                    duration_ms=duration_ms,
                ),
            )

            _safe_emit_bridge_event(
                self,
                TelegramOperationalEvent(
                    name=event_name,
                    level="info",
                    component="bridge",
                    outcome="success",
                    fields=sanitize_event_fields(
                        {
                            "operation": (
                                operation_name
                            ),
                            "duration_ms": (
                                duration_ms
                            ),
                        }
                    ),
                ),
            )

            return result

        return wrapped

    return decorator


@dataclass(
    slots=True,
)
class TelegramWebhookConversationBridge:
    runtime_factory: Callable[
        [],
        TelegramConversationStateRuntimePort,
    ] = field(
        repr=False
    )

    default_language: str = "pt-BR"

    metrics: TelegramConversationMetrics = field(
        default_factory=(
            NoOpTelegramConversationMetrics
        ),
        repr=False,
    )

    event_sink: TelegramOperationalEventSink = field(
        default_factory=(
            NoOpTelegramOperationalEventSink
        ),
        repr=False,
    )

    clock: Callable[[], float] = field(
        default=time.perf_counter,
        repr=False,
    )

    _runtime: (
        TelegramConversationStateRuntimePort
        | None
    ) = field(
        default=None,
        init=False,
        repr=False,
    )

    _runtime_lock: Any = field(
        default_factory=threading.Lock,
        init=False,
        repr=False,
    )

    def __post_init__(
        self,
    ) -> None:
        if not callable(
            self.runtime_factory
        ):
            raise TelegramConversationStateValidationError(
                "runtime_factory inválido."
            )

        normalized_language = (
            normalize_telegram_language(
                self.default_language
            )
        )

        if normalized_language is None:
            raise TelegramConversationStateValidationError(
                "default_language é obrigatório."
            )

        self.default_language = (
            normalized_language
        )

    @property
    def runtime_initialized(
        self,
    ) -> bool:
        return self._runtime is not None

    def load_session(
        self,
        telegram_user_id: int,
        chat_id: int,
    ) -> TelegramConversationSession | None:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        result = self._invoke(
            lambda: self._get_runtime().load_session(
                normalized_user_id,
                normalized_chat_id,
            )
        )

        if result is None:
            return None

        return _validate_session(
            result,
            telegram_user_id=(
                normalized_user_id
            ),
            chat_id=(
                normalized_chat_id
            ),
        )

    def open_session(
        self,
        telegram_user_id: int,
        chat_id: int,
        initial_state: Mapping[str, Any],
        language: str | None = None,
        ttl_seconds: int | None = None,
    ) -> TelegramConversationSession:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        normalized_state = (
            normalize_telegram_state(
                initial_state
            )
        )

        normalized_language = (
            normalize_telegram_language(
                language
            )
        )

        normalized_ttl = (
            None
            if ttl_seconds is None
            else validate_state_ttl_seconds(
                ttl_seconds
            )
        )

        result = self._invoke(
            lambda: self._get_runtime().open_session(
                telegram_user_id=(
                    normalized_user_id
                ),
                chat_id=(
                    normalized_chat_id
                ),
                initial_state=(
                    normalized_state
                ),
                language=(
                    normalized_language
                ),
                ttl_seconds=(
                    normalized_ttl
                ),
            )
        )

        return _validate_session(
            result,
            telegram_user_id=(
                normalized_user_id
            ),
            chat_id=(
                normalized_chat_id
            ),
        )

    @_observe_bridge_operation('load_or_open_session')
    def load_or_open_session(
        self,
        telegram_user_id: int,
        chat_id: int,
        initial_state: Mapping[str, Any],
        language: str | None = None,
        ttl_seconds: int | None = None,
    ) -> TelegramConversationSession:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        normalized_state = (
            normalize_telegram_state(
                initial_state
            )
        )

        normalized_language = (
            normalize_telegram_language(
                language
            )
        )

        normalized_ttl = (
            None
            if ttl_seconds is None
            else validate_state_ttl_seconds(
                ttl_seconds
            )
        )

        existing = self.load_session(
            normalized_user_id,
            normalized_chat_id,
        )

        if existing is not None:
            return existing

        return self.open_session(
            telegram_user_id=(
                normalized_user_id
            ),
            chat_id=normalized_chat_id,
            initial_state=normalized_state,
            language=normalized_language,
            ttl_seconds=normalized_ttl,
        )

    @_observe_bridge_operation('save_session')
    def save_session(
        self,
        session: TelegramConversationSession,
        *,
        ttl_seconds: int | None = None,
        only_if_changed: bool = True,
    ) -> TelegramConversationSession:
        # Entrada pública inválida é erro de validação.
        # ConsistencyError fica reservado para dados
        # inconsistentes retornados pelo runtime/store.
        if not isinstance(
            session,
            TelegramConversationSession,
        ):
            raise TelegramConversationStateValidationError(
                "Sessão informada para persistência é inválida."
            )

        validated_session = (
            _validate_session(
                session
            )
        )

        if not isinstance(
            only_if_changed,
            bool,
        ):
            raise TelegramConversationStateValidationError(
                "only_if_changed inválido."
            )

        normalized_ttl = (
            None
            if ttl_seconds is None
            else validate_state_ttl_seconds(
                ttl_seconds
            )
        )

        result = self._invoke(
            lambda: self._get_runtime().save_session(
                validated_session,
                ttl_seconds=normalized_ttl,
                only_if_changed=(
                    only_if_changed
                ),
            )
        )

        return _validate_session(
            result,
            telegram_user_id=(
                validated_session
                .telegram_user_id
            ),
            chat_id=(
                validated_session.chat_id
            ),
        )

    @_observe_bridge_operation('reload_session')
    def reload_session(
        self,
        session: TelegramConversationSession,
    ) -> TelegramConversationSession | None:
        validated_session = (
            _validate_session(
                session
            )
        )

        result = self._invoke(
            lambda: self._get_runtime().reload_session(
                validated_session
            )
        )

        if result is None:
            return None

        return _validate_session(
            result,
            telegram_user_id=(
                validated_session
                .telegram_user_id
            ),
            chat_id=(
                validated_session.chat_id
            ),
        )

    @_observe_bridge_operation('delete_session')
    def delete_session(
        self,
        session: TelegramConversationSession,
    ) -> bool:
        validated_session = (
            _validate_session(
                session
            )
        )

        deleted = self._invoke(
            lambda: self._get_runtime().delete_session(
                validated_session
            )
        )

        if not isinstance(
            deleted,
            bool,
        ):
            raise TelegramConversationStateConsistencyError(
                "Resultado de exclusão do runtime inválido."
            )

        if not validated_session.deleted:
            raise TelegramConversationStateConsistencyError(
                "Runtime não invalidou a sessão removida."
            )

        return deleted

    def delete_identity(
        self,
        telegram_user_id: int,
        chat_id: int,
    ) -> bool:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        deleted = self._invoke(
            lambda: self._get_runtime().delete_identity(
                normalized_user_id,
                normalized_chat_id,
            )
        )

        if not isinstance(
            deleted,
            bool,
        ):
            raise TelegramConversationStateConsistencyError(
                "Resultado de exclusão do runtime inválido."
            )

        return deleted

    @_observe_bridge_operation('resolve_language')
    def resolve_language(
        self,
        telegram_user_id: int,
        chat_id: int,
        *,
        fallback_language: str | None = None,
    ) -> str:
        (
            normalized_user_id,
            normalized_chat_id,
        ) = validate_telegram_identity(
            telegram_user_id,
            chat_id,
        )

        resolved_fallback = (
            self.default_language
            if fallback_language is None
            else normalize_telegram_language(
                fallback_language
            )
        )

        if resolved_fallback is None:
            raise TelegramConversationStateValidationError(
                "fallback_language é obrigatório."
            )

        session = self.load_session(
            normalized_user_id,
            normalized_chat_id,
        )

        if (
            session is None
            or session.language is None
        ):
            return resolved_fallback

        return session.language

    def cleanup_expired(
        self,
        limit: int = 100,
    ) -> int:
        normalized_limit = (
            validate_cleanup_limit(
                limit
            )
        )

        deleted_count = self._invoke(
            lambda: self._get_runtime().cleanup_expired(
                normalized_limit
            )
        )

        if (
            isinstance(
                deleted_count,
                bool,
            )
            or not isinstance(
                deleted_count,
                int,
            )
            or deleted_count < 0
            or deleted_count
            > normalized_limit
        ):
            raise TelegramConversationStateConsistencyError(
                "Resultado de cleanup do runtime inválido."
            )

        return deleted_count

    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "default_language": (
                self.default_language
            ),
            "runtime_initialized": (
                self.runtime_initialized
            ),
        }

    def _get_runtime(
        self,
    ) -> TelegramConversationStateRuntimePort:
        existing = self._runtime

        if existing is not None:
            return existing

        with self._runtime_lock:
            existing = self._runtime

            if existing is not None:
                return existing

            try:
                created = self.runtime_factory()

            except TelegramConversationStateError:
                raise

            except Exception:
                raise TelegramConversationStateUnavailableError(
                    "Runtime conversacional "
                    "temporariamente indisponível."
                ) from None

            if not isinstance(
                created,
                TelegramConversationStateRuntimePort,
            ):
                raise TelegramConversationStateConsistencyError(
                    "Factory retornou runtime inválido."
                )

            self._runtime = created

            return created

    @staticmethod
    def _invoke(
        operation: Callable[
            [],
            _T,
        ],
    ) -> _T:
        try:
            return operation()

        except TelegramConversationStateError:
            raise

        except Exception:
            raise TelegramConversationStateUnavailableError(
                "Persistência conversacional "
                "temporariamente indisponível."
            ) from None


def create_postgres_telegram_webhook_conversation_bridge(
    *,
    default_ttl_seconds: int = (
        DEFAULT_STATE_TTL_SECONDS
    ),
    default_language: str = "pt-BR",
    metrics: TelegramConversationMetrics
        | None = None,
    event_sink: TelegramOperationalEventSink
        | None = None,
    clock: Callable[[], float] = (
        time.perf_counter
    ),
) -> TelegramWebhookConversationBridge:
    normalized_ttl = (
        validate_state_ttl_seconds(
            default_ttl_seconds
        )
    )

    normalized_language = (
        normalize_telegram_language(
            default_language
        )
    )

    if normalized_language is None:
        raise TelegramConversationStateValidationError(
            "default_language é obrigatório."
        )

    if not callable(clock):
        raise TelegramConversationStateValidationError(
            "clock de observabilidade inválido."
        )

    resolved_metrics = (
        metrics
        if metrics is not None
        else NoOpTelegramConversationMetrics()
    )

    resolved_event_sink = (
        event_sink
        if event_sink is not None
        else NoOpTelegramOperationalEventSink()
    )

    if not isinstance(
        resolved_metrics,
        TelegramConversationMetrics,
    ):
        raise TelegramConversationStateValidationError(
            "Coletor de métricas inválido."
        )

    if not isinstance(
        resolved_event_sink,
        TelegramOperationalEventSink,
    ):
        raise TelegramConversationStateValidationError(
            "Event sink inválido."
        )

    def runtime_factory(
    ) -> TelegramConversationStateRuntimePort:
        return (
            create_postgres_telegram_conversation_state_runtime(
                default_ttl_seconds=(
                    normalized_ttl
                )
            )
        )

    return TelegramWebhookConversationBridge(
        runtime_factory=runtime_factory,
        default_language=(
            normalized_language
        ),
        metrics=resolved_metrics,
        event_sink=resolved_event_sink,
        clock=clock,
    )
