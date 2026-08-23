from __future__ import annotations

import io
import json

from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.channels import (
    telegram_update_worker
    as entrypoint,
)

from src.services.telegram_update_jobs import (
    TelegramUpdateRunnerConfigurationError,
    TelegramUpdateWorkerConfig,
)


class SafeResult:
    def __init__(
        self,
        *,
        decision="completed",
        payload=None,
    ):
        self.decision = decision
        self._payload = (
            payload
            or {
                "decision": decision,
                "stage": "complete",
                "update_id": 1001,
            }
        )

    def to_safe_dict(self):
        return dict(
            self._payload
        )


class SafeSummary:
    def to_safe_dict(self):
        return {
            "cycles": 1,
            "completed": 1,
            "retry_scheduled": 0,
            "dead_lettered": 0,
            "idle": 0,
            "ownership_lost": 0,
            "unavailable": 0,
            "consistency_errors": 0,
            "recovered_retry": 0,
            "recovered_dead_letter": 0,
            "duration_seconds": 0.1,
        }


class FakeSignalModule:
    SIGINT = 2
    SIGTERM = 15

    def __init__(self):
        self.handlers = {}
        self.restored = {}

    def signal(
        self,
        signal_number,
        handler,
    ):
        previous = (
            f"previous-{signal_number}"
        )

        if signal_number in self.handlers:
            self.restored[
                signal_number
            ] = handler

        self.handlers[
            signal_number
        ] = handler

        return previous


def _records(
    stream: io.StringIO,
):
    return [
        json.loads(line)
        for line in stream
        .getvalue()
        .splitlines()
        if line.strip()
    ]


def test_worker_config_uses_defaults():
    config = (
        entrypoint
        .load_worker_config_from_env(
            {}
        )
    )

    assert config == (
        TelegramUpdateWorkerConfig()
    )


def test_worker_config_accepts_environment():
    config = (
        entrypoint
        .load_worker_config_from_env(
            {
                entrypoint
                .ENV_LEASE_SECONDS:
                    "180",

                entrypoint
                .ENV_IDLE_SLEEP_SECONDS:
                    "0.5",

                entrypoint
                .ENV_UNAVAILABLE_SLEEP_SECONDS:
                    "7.5",

                entrypoint
                .ENV_RECOVERY_INTERVAL_SECONDS:
                    "45",

                entrypoint
                .ENV_RECOVERY_BATCH_SIZE:
                    "50",

                entrypoint
                .ENV_RETRY_BASE_DELAY_SECONDS:
                    "10",

                entrypoint
                .ENV_RETRY_MAX_DELAY_SECONDS:
                    "1200",
            }
        )
    )

    assert config.lease_seconds == 180

    assert (
        config.idle_sleep_seconds
        == 0.5
    )

    assert (
        config.unavailable_sleep_seconds
        == 7.5
    )

    assert (
        config.recovery_interval_seconds
        == 45.0
    )

    assert (
        config.recovery_batch_size
        == 50
    )

    assert (
        config.retry_base_delay_seconds
        == 10
    )

    assert (
        config.retry_max_delay_seconds
        == 1200
    )


@pytest.mark.parametrize(
    (
        "environment_name",
        "invalid_value",
    ),
    [
        (
            entrypoint
            .ENV_LEASE_SECONDS,
            "invalid",
        ),
        (
            entrypoint
            .ENV_IDLE_SLEEP_SECONDS,
            "nan",
        ),
        (
            entrypoint
            .ENV_RECOVERY_BATCH_SIZE,
            "",
        ),
    ],
)
def test_invalid_environment_is_rejected(
    environment_name,
    invalid_value,
):
    with pytest.raises(
        TelegramUpdateRunnerConfigurationError
    ):
        (
            entrypoint
            .load_worker_config_from_env(
                {
                    environment_name:
                        invalid_value,
                }
            )
        )


def test_idle_result_is_not_logged():
    stream = io.StringIO()

    entrypoint.emit_runner_result(
        SafeResult(
            decision="idle",
        ),
        stream=stream,
    )

    assert stream.getvalue() == ""


def test_result_log_uses_safe_contract():
    stream = io.StringIO()

    entrypoint.emit_runner_result(
        SafeResult(
            payload={
                "decision": "completed",
                "stage": "complete",
                "update_id": 1001,
                "job_status": "completed",
            }
        ),
        stream=stream,
    )

    records = _records(
        stream
    )

    assert records == [
        {
            "event":
                "telegram_worker_result",
            "data": {
                "decision": "completed",
                "stage": "complete",
                "update_id": 1001,
                "job_status": "completed",
            },
        },
    ]

    assert "payload" not in (
        stream.getvalue()
    )

    assert "ciphertext" not in (
        stream.getvalue()
    )


def test_signal_handlers_set_stop_event():
    stop_event = Event()

    fake_signal = (
        FakeSignalModule()
    )

    previous = (
        entrypoint
        ._install_signal_handlers(
            stop_event,
            signal_module=fake_signal,
        )
    )

    assert set(previous) == {
        fake_signal.SIGINT,
        fake_signal.SIGTERM,
    }

    fake_signal.handlers[
        fake_signal.SIGTERM
    ](
        fake_signal.SIGTERM,
        None,
    )

    assert stop_event.is_set()


def test_main_runs_worker_and_emits_summary(
    monkeypatch,
):
    stdout = io.StringIO()
    stderr = io.StringIO()

    config = (
        TelegramUpdateWorkerConfig()
    )

    keyring = object()
    processor = MagicMock()
    summary = SafeSummary()

    monkeypatch.setattr(
        entrypoint,
        "load_worker_config_from_env",
        lambda: config,
    )

    monkeypatch.setattr(
        entrypoint,
        (
            "load_telegram_update_"
            "keyring_from_env"
        ),
        lambda: keyring,
    )

    monkeypatch.setattr(
        entrypoint,
        "load_telegram_processor",
        lambda: processor,
    )

    monkeypatch.setattr(
        entrypoint,
        "_install_signal_handlers",
        lambda stop_event: {},
    )

    monkeypatch.setattr(
        entrypoint,
        "_restore_signal_handlers",
        lambda handlers: None,
    )

    runner = MagicMock(
        return_value=summary,
    )

    monkeypatch.setattr(
        entrypoint,
        "run_telegram_update_worker",
        runner,
    )

    exit_code = entrypoint.main(
        [
            "--max-cycles",
            "1",
        ],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == (
        entrypoint.EXIT_OK
    )

    runner.assert_called_once()

    positional, keyword = (
        runner.call_args
    )

    assert positional == (
        processor,
    )

    assert (
        keyword["config"]
        is config
    )

    assert (
        keyword["keyring"]
        is keyring
    )

    assert (
        keyword["max_cycles"]
        == 1
    )

    assert callable(
        keyword["on_result"]
    )

    assert stderr.getvalue() == ""

    events = [
        record["event"]
        for record in _records(
            stdout
        )
    ]

    assert events == [
        "telegram_worker_started",
        "telegram_worker_summary",
    ]


def test_main_sanitizes_configuration_failure(
    monkeypatch,
):
    stdout = io.StringIO()
    stderr = io.StringIO()

    def fail_config():
        raise (
            TelegramUpdateRunnerConfigurationError(
                "postgresql://secret"
            )
        )

    monkeypatch.setattr(
        entrypoint,
        "load_worker_config_from_env",
        fail_config,
    )

    exit_code = entrypoint.main(
        [],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == (
        entrypoint
        .EXIT_CONFIGURATION_ERROR
    )

    assert "postgresql://secret" not in (
        stderr.getvalue()
    )

    assert (
        "configuration_invalid"
        in stderr.getvalue()
    )


def test_main_sanitizes_runtime_failure(
    monkeypatch,
):
    stdout = io.StringIO()
    stderr = io.StringIO()

    monkeypatch.setattr(
        entrypoint,
        "load_worker_config_from_env",
        lambda: (
            TelegramUpdateWorkerConfig()
        ),
    )

    monkeypatch.setattr(
        entrypoint,
        (
            "load_telegram_update_"
            "keyring_from_env"
        ),
        lambda: object(),
    )

    monkeypatch.setattr(
        entrypoint,
        "load_telegram_processor",
        lambda: MagicMock(),
    )

    monkeypatch.setattr(
        entrypoint,
        "_install_signal_handlers",
        lambda stop_event: {},
    )

    monkeypatch.setattr(
        entrypoint,
        "_restore_signal_handlers",
        lambda handlers: None,
    )

    def fail_runner(*args, **kwargs):
        raise RuntimeError(
            "private-financial-message"
        )

    monkeypatch.setattr(
        entrypoint,
        "run_telegram_update_worker",
        fail_runner,
    )

    exit_code = entrypoint.main(
        [],
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == (
        entrypoint.EXIT_RUNTIME_ERROR
    )

    assert (
        "private-financial-message"
        not in stderr.getvalue()
    )

    assert (
        "runtime_failed"
        in stderr.getvalue()
    )


def test_worker_script_exists():
    from pathlib import Path

    path = Path(
        "scripts/"
        "run_telegram_update_worker.py"
    )

    assert path.is_file()

    source = path.read_text(
        encoding="utf-8",
    )

    assert (
        'if __name__ == "__main__":'
        in source
    )

    assert "main()" in source
