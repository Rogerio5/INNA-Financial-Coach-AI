from __future__ import annotations

import ast
from pathlib import Path

import pytest

from api import (
    telegram_webhook,
)
from src.services.telegram_observability import (
    TelegramOperationalEvent,
)


ROOT = Path(__file__).resolve().parents[3]

WEBHOOK_FILE = (
    ROOT
    / "api"
    / "telegram_webhook.py"
)

WORKER_FILE = (
    ROOT
    / "src"
    / "channels"
    / "telegram_update_worker.py"
)


class CapturingEventSink:
    def __init__(self) -> None:
        self.events = []

    def emit(
        self,
        event,
    ) -> None:
        self.events.append(
            event
        )


class BrokenEventSink:
    def emit(
        self,
        event,
    ) -> None:
        del event

        raise RuntimeError(
            "logging unavailable"
        )


def parse_file(
    path: Path,
) -> ast.Module:
    return ast.parse(
        path.read_text(
            encoding="utf-8",
        ),
        filename=str(path),
    )


def print_calls(
    tree: ast.Module,
):
    return [
        node
        for node in ast.walk(tree)
        if isinstance(
            node,
            ast.Call,
        )
        and isinstance(
            node.func,
            ast.Name,
        )
        and node.func.id == "print"
    ]


def enclosing_function_name(
    tree: ast.Module,
    target: ast.AST,
) -> str | None:
    parents = {}

    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(
            parent
        ):
            parents[child] = parent

    current = parents.get(
        target
    )

    while current is not None:
        if isinstance(
            current,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            return current.name

        current = parents.get(
            current
        )

    return None


def test_webhook_has_no_print_calls():
    tree = parse_file(
        WEBHOOK_FILE
    )

    assert print_calls(
        tree
    ) == []


def test_worker_preserves_only_cli_print():
    tree = parse_file(
        WORKER_FILE
    )

    calls = print_calls(
        tree
    )

    assert len(calls) == 1

    assert (
        enclosing_function_name(
            tree,
            calls[0],
        )
        == "_emit_event"
    )


def test_safe_helper_emits_structured_event(
    monkeypatch,
):
    sink = CapturingEventSink()

    monkeypatch.setattr(
        telegram_webhook,
        "_telegram_operational_event_sink",
        sink,
    )

    telegram_webhook\
        ._emit_telegram_operational_event_safely(
            name=(
                "telegram_update_processing_failed"
            ),
            level="error",
            component="webhook",
            outcome="error",
            operation="process_update",
            error_category="unknown",
            stage="process_update",
        )

    assert len(
        sink.events
    ) == 1

    event = sink.events[0]

    assert isinstance(
        event,
        TelegramOperationalEvent,
    )

    assert event.name == (
        "telegram_update_processing_failed"
    )

    assert event.level == "error"
    assert event.component == "webhook"
    assert event.outcome == "error"

    assert dict(
        event.fields
    ) == {
        "operation": "process_update",
        "error_category": "unknown",
        "stage": "process_update",
    }


def test_safe_helper_swallows_sink_failure(
    monkeypatch,
):
    monkeypatch.setattr(
        telegram_webhook,
        "_telegram_operational_event_sink",
        BrokenEventSink(),
    )

    result = (
        telegram_webhook
        ._emit_telegram_operational_event_safely(
            name=(
                "telegram_update_processing_failed"
            ),
            level="error",
            component="webhook",
            outcome="error",
            operation="process_update",
            error_category="unknown",
        )
    )

    assert result is None


@pytest.mark.parametrize(
    "forbidden",
    [
        "telegram_user_id",
        "chat_id",
        "message_text",
        "processing_state",
        "payload",
        "financial_data",
        "database_url",
        "authorization",
        "token=",
        "secret=",
        "password=",
        "traceback",
    ],
)
def test_helper_call_sites_do_not_include_sensitive_fields(
    forbidden,
):
    source = WEBHOOK_FILE.read_text(
        encoding="utf-8",
    )

    tree = ast.parse(
        source,
        filename=str(WEBHOOK_FILE),
    )

    rendered_calls = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        if not (
            isinstance(
                node.func,
                ast.Name,
            )
            and node.func.id
            == "_emit_telegram_operational_event_safely"
        ):
            continue

        rendered_calls.append(
            ast.unparse(
                node
            ).lower()
        )

    assert rendered_calls

    for rendered in rendered_calls:
        assert forbidden not in rendered
