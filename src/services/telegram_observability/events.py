from __future__ import annotations

from threading import RLock

from .contracts import (
    TelegramOperationalEvent,
)


class NoOpTelegramOperationalEventSink:
    """
    Sink padrão sem saída.
    """

    __slots__ = ()

    def emit(
        self,
        event: TelegramOperationalEvent,
    ) -> None:
        del event


class InMemoryTelegramOperationalEventSink:
    """
    Armazena eventos sanitizados para testes.
    """

    def __init__(self) -> None:
        self._events: list[
            TelegramOperationalEvent
        ] = []

        self._lock = RLock()

    def emit(
        self,
        event: TelegramOperationalEvent,
    ) -> None:
        if not isinstance(
            event,
            TelegramOperationalEvent,
        ):
            raise TypeError(
                "event deve ser TelegramOperationalEvent."
            )

        with self._lock:
            self._events.append(event)

    def snapshot(
        self,
    ) -> tuple[
        TelegramOperationalEvent,
        ...,
    ]:
        with self._lock:
            return tuple(
                self._events
            )

    def clear(self) -> None:
        with self._lock:
            self._events.clear()

    def count(
        self,
        *,
        name: str | None = None,
        component: str | None = None,
        outcome: str | None = None,
        level: str | None = None,
    ) -> int:
        return sum(
            1
            for event in self.snapshot()
            if (
                name is None
                or event.name == name
            )
            and (
                component is None
                or event.component == component
            )
            and (
                outcome is None
                or event.outcome == outcome
            )
            and (
                level is None
                or event.level == level
            )
        )
