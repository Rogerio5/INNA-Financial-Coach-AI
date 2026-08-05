from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from src.services.telegram_update_jobs import (
    execution,
    runner,
    worker,
)


LOCK_TOKEN = "a" * 64


def make_lease(
    *,
    attempt_count=1,
    max_attempts=5,
):
    return worker.TelegramUpdateWorkerLease(
        update_id=95001,
        job_status="processing",
        receipt_status="processing",
        job_attempt_count=attempt_count,
        job_max_attempts=max_attempts,
        receipt_attempt_count=attempt_count,
        payload_version=1,
        payload_key_id="inna.telegram.v1",
        payload_ciphertext=b"c" * 32,
        payload_nonce=b"n" * 12,
        lock_token=LOCK_TOKEN,
    )


class FakePayload:
    def __init__(
        self,
        update=None,
    ):
        self.update = update or {
            "update_id": 95001,
            "message": {
                "text": "Olá",
            },
        }

    def to_processing_dict(self):
        return {
            "update_id": (self.update["update_id"]),
            "message": dict(self.update["message"]),
        }


@dataclass
class FakeRecovery:
    retried: int = 0
    dead_lettered: int = 0


class FakeStopEvent:
    def __init__(self):
        self.wait_calls = []
        self.stopped = False

    def is_set(self):
        return self.stopped

    def wait(self, timeout):
        self.wait_calls.append(timeout)
        return self.stopped


def dependencies(
    *,
    claim=None,
    decrypt=None,
    complete=None,
    fail=None,
    recover=None,
    times=None,
):
    clock_values = iter(
        times
        or [
            0.0,
            0.0,
            1.0,
            1.0,
            2.0,
            2.0,
        ]
    )

    return runner.TelegramUpdateWorkerDependencies(
        claim=(claim or (lambda **_kwargs: make_lease())),
        decrypt=(decrypt or (lambda *_args, **_kwargs: FakePayload())),
        complete=(
            complete
            or (
                lambda _lease: SimpleNamespace(
                    job_status="completed",
                    idempotent_replay=False,
                )
            )
        ),
        fail=(
            fail
            or (
                lambda *_args, **_kwargs: SimpleNamespace(
                    job_status="queued",
                    idempotent_replay=False,
                )
            )
        ),
        recover=(recover or (lambda **_kwargs: FakeRecovery())),
        monotonic=(lambda: next(clock_values)),
    )


def test_run_one_completes_successfully():
    received = []

    result = runner.run_one_telegram_update_job(
        lambda update: received.append(update),
        dependencies=dependencies(),
    )

    assert result.decision == "completed"
    assert result.job_status == "completed"
    assert received[0]["update_id"] == 95001


def test_none_processor_result_is_success():
    result = runner.run_one_telegram_update_job(
        lambda _update: None,
        dependencies=dependencies(),
    )

    assert result.decision == "completed"


def test_false_processor_result_schedules_retry():
    result = runner.run_one_telegram_update_job(
        lambda _update: False,
        dependencies=dependencies(),
    )

    assert result.decision == "retry_scheduled"

    assert result.error_code == "telegram.processing_failed"


def test_transient_exception_schedules_retry():
    def processor(_update):
        raise (
            runner.TelegramUpdateTransientProcessingError("telegram.provider_timeout")
        )

    result = runner.run_one_telegram_update_job(
        processor,
        dependencies=dependencies(),
    )

    assert result.decision == "retry_scheduled"

    assert result.error_code == "telegram.provider_timeout"


def test_permanent_exception_dead_letters():
    def processor(_update):
        raise (
            runner.TelegramUpdatePermanentProcessingError("telegram.update_rejected")
        )

    result = runner.run_one_telegram_update_job(
        processor,
        dependencies=dependencies(
            fail=(
                lambda *_args, **_kwargs: SimpleNamespace(
                    job_status="dead_letter",
                    idempotent_replay=False,
                )
            )
        ),
    )

    assert result.decision == "dead_lettered"


def test_unexpected_exception_schedules_retry():
    def processor(_update):
        raise RuntimeError("sensitive error")

    result = runner.run_one_telegram_update_job(
        processor,
        dependencies=dependencies(),
    )

    assert result.decision == "retry_scheduled"

    assert "sensitive" not in str(result.to_safe_dict())


def test_idle_when_no_job():
    result = runner.run_one_telegram_update_job(
        lambda _update: None,
        dependencies=dependencies(claim=(lambda **_kwargs: None)),
    )

    assert result.decision == "idle"
    assert result.update_id is None


def test_claim_unavailable_is_safe():
    def claim(**_kwargs):
        raise (worker.TelegramUpdateWorkerUnavailableError("database secret"))

    result = runner.run_one_telegram_update_job(
        lambda _update: None,
        dependencies=dependencies(claim=claim),
    )

    assert result.decision == "unavailable"
    assert "secret" not in str(result.to_safe_dict())


def test_keyring_error_schedules_retry():
    def decrypt(*_args, **_kwargs):
        raise (execution.TelegramUpdateExecutionConfigurationError("secret key"))

    result = runner.run_one_telegram_update_job(
        lambda _update: None,
        dependencies=dependencies(decrypt=decrypt),
    )

    assert result.decision == "retry_scheduled"

    assert result.error_code == "telegram.keyring_unavailable"


def test_invalid_payload_is_dead_lettered():
    def decrypt(*_args, **_kwargs):
        raise (execution.TelegramUpdateExecutionPayloadError("payload detail"))

    result = runner.run_one_telegram_update_job(
        lambda _update: None,
        dependencies=dependencies(
            decrypt=decrypt,
            fail=(
                lambda *_args, **_kwargs: SimpleNamespace(
                    job_status="dead_letter",
                    idempotent_replay=False,
                )
            ),
        ),
    )

    assert result.decision == "dead_lettered"

    assert result.error_code == "telegram.payload_invalid"


def test_completion_ownership_loss():
    def complete(_lease):
        raise (worker.TelegramUpdateWorkerOwnershipError("token detail"))

    result = runner.run_one_telegram_update_job(
        lambda _update: None,
        dependencies=dependencies(complete=complete),
    )

    assert result.decision == "ownership_lost"


def test_failure_unavailable_is_safe():
    def fail(*_args, **_kwargs):
        raise (worker.TelegramUpdateWorkerUnavailableError("db password"))

    result = runner.run_one_telegram_update_job(
        lambda _update: False,
        dependencies=dependencies(fail=fail),
    )

    assert result.decision == "unavailable"

    assert "password" not in str(result.to_safe_dict())


@pytest.mark.parametrize(
    (
        "attempt",
        "expected",
    ),
    [
        (1, 5),
        (2, 10),
        (3, 20),
        (10, 2560),
        (20, 3600),
    ],
)
def test_retry_backoff(
    attempt,
    expected,
):
    config = runner.TelegramUpdateWorkerConfig()

    assert (
        runner.calculate_worker_retry_delay_seconds(
            attempt_count=attempt,
            config=config,
        )
        == expected
    )


def test_runner_recovers_then_processes():
    received_limits = []

    deps = dependencies(
        recover=(
            lambda **kwargs: (
                received_limits.append(kwargs["limit"])
                or FakeRecovery(
                    retried=2,
                    dead_lettered=1,
                )
            )
        ),
        claim=lambda **_kwargs: None,
        times=[
            0.0,
            0.0,
            1.0,
        ],
    )

    stop = FakeStopEvent()

    summary = runner.run_telegram_update_worker(
        lambda _update: None,
        stop_event=stop,
        dependencies=deps,
        max_cycles=1,
    )

    assert received_limits == [100]
    assert summary.recovered_retry == 2

    assert summary.recovered_dead_letter == 1

    assert summary.idle == 1


def test_runner_uses_idle_wait():
    stop = FakeStopEvent()

    summary = runner.run_telegram_update_worker(
        lambda _update: None,
        stop_event=stop,
        dependencies=dependencies(
            claim=(lambda **_kwargs: None),
            times=[
                0.0,
                0.0,
                1.0,
            ],
        ),
        max_cycles=1,
    )

    assert summary.idle == 1
    assert stop.wait_calls == [1.0]


def test_runner_uses_unavailable_wait():
    stop = FakeStopEvent()

    def claim(**_kwargs):
        raise (worker.TelegramUpdateWorkerUnavailableError("unavailable"))

    summary = runner.run_telegram_update_worker(
        lambda _update: None,
        stop_event=stop,
        dependencies=dependencies(
            claim=claim,
            times=[
                0.0,
                0.0,
                1.0,
            ],
        ),
        max_cycles=1,
    )

    assert summary.unavailable == 1
    assert stop.wait_calls == [5.0]


def test_recovery_failure_does_not_claim():
    claimed = []

    def recover(**_kwargs):
        raise RuntimeError("database secret")

    stop = FakeStopEvent()

    summary = runner.run_telegram_update_worker(
        lambda _update: None,
        stop_event=stop,
        dependencies=dependencies(
            recover=recover,
            claim=(lambda **_kwargs: claimed.append(True)),
            times=[
                0.0,
                0.0,
                1.0,
            ],
        ),
        max_cycles=1,
    )

    assert claimed == []
    assert summary.unavailable == 1
    assert stop.wait_calls == [5.0]


def test_callback_receives_safe_result():
    results = []

    (
        runner.run_telegram_update_worker(
            lambda _update: None,
            stop_event=FakeStopEvent(),
            dependencies=dependencies(
                claim=(lambda **_kwargs: None),
                times=[
                    0.0,
                    0.0,
                    1.0,
                ],
            ),
            on_result=results.append,
            max_cycles=1,
        )
    )

    assert len(results) == 1

    assert results[0].to_safe_dict()["decision"] == "idle"


def test_callback_failure_is_ignored():
    def callback(_result):
        raise RuntimeError("callback secret")

    summary = runner.run_telegram_update_worker(
        lambda _update: None,
        stop_event=FakeStopEvent(),
        dependencies=dependencies(
            claim=(lambda **_kwargs: None),
            times=[
                0.0,
                0.0,
                1.0,
            ],
        ),
        on_result=callback,
        max_cycles=1,
    )

    assert summary.cycles == 1


@pytest.mark.parametrize(
    "field_name",
    [
        "idle_sleep_seconds",
        "unavailable_sleep_seconds",
        "recovery_interval_seconds",
    ],
)
def test_invalid_float_config_is_rejected(
    field_name,
):
    values = {
        field_name: 0,
    }

    with pytest.raises(runner.TelegramUpdateRunnerConfigurationError):
        (runner.TelegramUpdateWorkerConfig(**values))


def test_retry_base_cannot_exceed_maximum():
    with pytest.raises(runner.TelegramUpdateRunnerConfigurationError):
        (
            runner.TelegramUpdateWorkerConfig(
                retry_base_delay_seconds=10,
                retry_max_delay_seconds=5,
            )
        )


def test_processor_error_code_is_sanitized():
    with pytest.raises(runner.TelegramUpdateRunnerConfigurationError):
        (runner.TelegramUpdateTransientProcessingError("invalid code"))


def test_runner_result_never_contains_payload():
    result = runner.run_one_telegram_update_job(
        lambda _update: None,
        dependencies=dependencies(),
    )

    safe = result.to_safe_dict()

    assert "payload" not in safe
    assert "lock_token" not in safe
    assert "ciphertext" not in safe

    assert LOCK_TOKEN not in repr(result)
