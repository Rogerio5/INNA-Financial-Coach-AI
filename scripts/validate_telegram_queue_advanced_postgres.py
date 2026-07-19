from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

project_root_text = str(
    PROJECT_ROOT
)

if (
    project_root_text
    not in sys.path
):
    sys.path.insert(
        0,
        project_root_text,
    )


from concurrent.futures import (
    ThreadPoolExecutor,
)
from dataclasses import replace
import secrets
from threading import Barrier
import time
from typing import Any

from src.database.connection import (
    cursor_postgres,
)

from src.services.telegram_update_jobs import (
    TelegramUpdateExecutionDecryptionError,
    TelegramUpdateWorkerOwnershipError,
    claim_next_authenticated_telegram_update_job_atomic,
    complete_authenticated_telegram_update_job_atomic,
    decrypt_authenticated_telegram_worker_lease,
    enqueue_authenticated_telegram_update_atomic,
    recover_expired_authenticated_telegram_update_jobs_atomic,
    retry_or_dead_letter_authenticated_telegram_update_job_atomic,
)

from src.services.telegram_update_jobs import (
    service as crypto_service,
)


ADVISORY_LOCK_KEY = (
    "inna:test:telegram-update-jobs:"
    "advanced-postgres"
)

KEY_ID = "inna.integration.advanced.v1"

BASE_UPDATE_ID = (
    8_200_000_000_000_000_000
    + secrets.randbelow(
        10_000_000
    )
)


UPDATE_IDS = {
    "retry": BASE_UPDATE_ID + 1,
    "dead_letter": BASE_UPDATE_ID + 2,
    "completion_replay": BASE_UPDATE_ID + 3,
    "ownership": BASE_UPDATE_ID + 4,
    "recovery_retry": BASE_UPDATE_ID + 5,
    "recovery_dead": BASE_UPDATE_ID + 6,
    "concurrency_a": BASE_UPDATE_ID + 7,
    "concurrency_b": BASE_UPDATE_ID + 8,
}


keyring = (
    crypto_service
    .TelegramUpdateEncryptionKeyring(
        active_key_id=KEY_ID,
        keys={
            KEY_ID: secrets.token_bytes(32),
        },
    )
)


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise RuntimeError(
            "STOP: " + message
        )


def synthetic_update(
    update_id: int,
    *,
    label: str,
) -> dict[str, Any]:
    return {
        "update_id": update_id,
        "message": {
            "message_id": (
                update_id % 1_000_000
            ),
            "date": 1_700_000_000,
            "chat": {
                "id": -9_200_001,
                "type": "private",
            },
            "from": {
                "id": 9_200_001,
                "is_bot": False,
                "first_name": "Integration",
            },
            "text": (
                "Teste sintético INNA: "
                + label
            ),
        },
    }


def enqueue_case(
    update_id: int,
    *,
    label: str,
    max_attempts: int,
) -> None:
    enqueue_authenticated_telegram_update_atomic(
        synthetic_update(
            update_id,
            label=label,
        ),
        receipt_lease_seconds=120,
        max_attempts=max_attempts,
        keyring=keyring,
    )

    state = fetch_state(
        update_id
    )

    require(
        state is not None,
        "o ingresso não criou o estado esperado.",
    )

    require(
        state["job_status"] == "queued",
        "o job não iniciou em queued.",
    )

    require(
        state["receipt_status"]
        == "processing",
        "o receipt não iniciou em processing.",
    )


def fetch_state(
    update_id: int,
) -> dict[str, Any] | None:
    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:
        cursor.execute(
            """
            SELECT
                job.update_id,

                job.status AS job_status,
                receipt.status
                    AS receipt_status,

                job.attempt_count,
                job.max_attempts,

                (
                    job.payload_ciphertext
                        IS NOT NULL
                    AND job.payload_nonce
                        IS NOT NULL
                    AND job.payload_key_id
                        IS NOT NULL
                ) AS payload_present,

                (
                    job.payload_ciphertext
                        IS NULL
                    AND job.payload_nonce
                        IS NULL
                    AND job.payload_key_id
                        IS NULL
                ) AS payload_cleared,

                (
                    job.locked_at IS NULL
                    AND job.lock_expires_at
                        IS NULL
                    AND job.lock_token IS NULL
                ) AS ownership_cleared,

                (
                    job.completed_at
                        IS NOT NULL
                ) AS job_completed,

                (
                    job.dead_lettered_at
                        IS NOT NULL
                ) AS job_dead_lettered,

                (
                    receipt.completed_at
                        IS NOT NULL
                ) AS receipt_completed,

                (
                    receipt.failed_at
                        IS NOT NULL
                ) AS receipt_failed,

                job.last_error_code
                    AS job_error_code,

                receipt.last_error_code
                    AS receipt_error_code
            FROM public.telegram_update_jobs
                AS job
            INNER JOIN
                public.telegram_update_receipts
                AS receipt
                ON receipt.update_id =
                    job.update_id
            WHERE
                job.update_id = %(update_id)s;
            """,
            {
                "update_id": update_id,
            },
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return dict(row)


def claim_expected(
    update_id: int,
    *,
    lease_seconds: int = 120,
):
    lease = (
        claim_next_authenticated_telegram_update_job_atomic(
            lease_seconds=lease_seconds,
        )
    )

    require(
        lease is not None,
        "nenhum job estava disponível.",
    )

    require(
        lease.update_id == update_id,
        "o worker obteve um update inesperado.",
    )

    return lease


def decrypt_expected(
    lease,
) -> dict[str, Any]:
    protected = (
        decrypt_authenticated_telegram_worker_lease(
            lease,
            keyring=keyring,
        )
    )

    restored = (
        protected.to_processing_dict()
    )

    require(
        restored.get("update_id")
        == lease.update_id,
        "a identidade descriptografada divergiu.",
    )

    return restored


def cleanup(
    update_ids: list[int],
) -> None:
    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:
        cursor.execute(
            """
            DELETE FROM
                public.telegram_update_receipts
            WHERE
                update_id = ANY(%(update_ids)s);
            """,
            {
                "update_ids": update_ids,
            },
        )


def verify_cleanup(
    update_ids: list[int],
) -> tuple[int, int]:
    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:
        cursor.execute(
            """
            SELECT
                (
                    SELECT COUNT(*)
                    FROM public.telegram_update_receipts
                    WHERE update_id =
                        ANY(%(update_ids)s)
                ) AS receipt_count,

                (
                    SELECT COUNT(*)
                    FROM public.telegram_update_jobs
                    WHERE update_id =
                        ANY(%(update_ids)s)
                ) AS job_count;
            """,
            {
                "update_ids": update_ids,
            },
        )

        row = cursor.fetchone()

    return (
        int(row["receipt_count"]),
        int(row["job_count"]),
    )


def verify_empty_queue() -> None:
    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as cursor:
        cursor.execute(
            """
            SELECT
                (
                    SELECT COUNT(*)
                    FROM public.telegram_update_jobs
                ) AS job_count,

                (
                    SELECT COUNT(*)
                    FROM public.telegram_update_receipts
                ) AS receipt_count;
            """
        )

        row = cursor.fetchone()

    job_count = int(
        row["job_count"]
    )

    receipt_count = int(
        row["receipt_count"]
    )

    print(
        "Jobs antes do teste:",
        job_count,
    )

    print(
        "Receipts antes do teste:",
        receipt_count,
    )

    require(
        job_count == 0,
        "existem jobs fora do teste; "
        "a validação foi cancelada.",
    )

    require(
        receipt_count == 0,
        "existem receipts fora do teste; "
        "a validação foi cancelada.",
    )


def test_retry_and_replay() -> None:
    update_id = UPDATE_IDS["retry"]

    enqueue_case(
        update_id,
        label="retry",
        max_attempts=3,
    )

    first_lease = claim_expected(
        update_id
    )

    decrypt_expected(
        first_lease
    )

    failure = (
        retry_or_dead_letter_authenticated_telegram_update_job_atomic(
            first_lease,
            error_code=(
                "telegram.integration_retry"
            ),
            retry_delay_seconds=0,
            force_dead_letter=False,
        )
    )

    require(
        failure.decision
        == "retry_scheduled",
        "a falha recuperável não agendou retry.",
    )

    state = fetch_state(
        update_id
    )

    require(
        state["job_status"] == "queued",
        "o retry não retornou o job para queued.",
    )

    require(
        state["receipt_status"] == "failed",
        "o receipt do retry não ficou failed.",
    )

    require(
        bool(state["payload_present"]),
        "o retry removeu o payload criptografado.",
    )

    require(
        bool(state["ownership_cleared"]),
        "o retry não liberou o ownership.",
    )

    replay = (
        retry_or_dead_letter_authenticated_telegram_update_job_atomic(
            first_lease,
            error_code=(
                "telegram.integration_retry"
            ),
            retry_delay_seconds=0,
            force_dead_letter=False,
        )
    )

    require(
        replay.decision
        == "already_retry_scheduled",
        "o replay do retry não foi idempotente.",
    )

    second_lease = claim_expected(
        update_id
    )

    require(
        second_lease.job_attempt_count == 2,
        "o segundo claim não incrementou "
        "a tentativa corretamente.",
    )

    decrypt_expected(
        second_lease
    )

    completion = (
        complete_authenticated_telegram_update_job_atomic(
            second_lease
        )
    )

    require(
        completion.decision == "completed",
        "o retry recuperado não foi concluído.",
    )

    print(
        "PASS: retry + replay idempotente"
    )


def test_dead_letter_and_replay() -> None:
    update_id = UPDATE_IDS[
        "dead_letter"
    ]

    enqueue_case(
        update_id,
        label="dead-letter",
        max_attempts=1,
    )

    lease = claim_expected(
        update_id
    )

    decrypt_expected(
        lease
    )

    failure = (
        retry_or_dead_letter_authenticated_telegram_update_job_atomic(
            lease,
            error_code=(
                "telegram.integration_dead_letter"
            ),
            retry_delay_seconds=0,
            force_dead_letter=False,
        )
    )

    require(
        failure.decision
        == "dead_lettered",
        "tentativas esgotadas não geraram "
        "dead-letter.",
    )

    state = fetch_state(
        update_id
    )

    require(
        state["job_status"]
        == "dead_letter",
        "o job não ficou em dead_letter.",
    )

    require(
        state["receipt_status"] == "failed",
        "o receipt dead-letter não ficou failed.",
    )

    require(
        bool(state["payload_present"]),
        "dead-letter removeu o payload criptografado.",
    )

    require(
        bool(state["job_dead_lettered"]),
        "dead_lettered_at não foi preenchido.",
    )

    replay = (
        retry_or_dead_letter_authenticated_telegram_update_job_atomic(
            lease,
            error_code=(
                "telegram.integration_dead_letter"
            ),
            retry_delay_seconds=0,
            force_dead_letter=False,
        )
    )

    require(
        replay.decision
        == "already_dead_lettered",
        "o replay dead-letter não foi idempotente.",
    )

    print(
        "PASS: dead-letter + replay idempotente"
    )


def test_authenticated_decryption_and_completion_replay() -> None:
    update_id = UPDATE_IDS[
        "completion_replay"
    ]

    enqueue_case(
        update_id,
        label="crypto",
        max_attempts=3,
    )

    lease = claim_expected(
        update_id
    )

    tampered = bytearray(
        lease.payload_ciphertext
    )

    tampered[-1] ^= 1

    invalid_lease = replace(
        lease,
        payload_ciphertext=bytes(
            tampered
        ),
    )

    try:
        decrypt_authenticated_telegram_worker_lease(
            invalid_lease,
            keyring=keyring,
        )

    except TelegramUpdateExecutionDecryptionError:
        pass

    else:
        raise RuntimeError(
            "STOP: ciphertext adulterado "
            "foi aceito."
        )

    decrypt_expected(
        lease
    )

    first = (
        complete_authenticated_telegram_update_job_atomic(
            lease
        )
    )

    require(
        first.decision == "completed",
        "a conclusão inicial falhou.",
    )

    replay = (
        complete_authenticated_telegram_update_job_atomic(
            lease
        )
    )

    require(
        replay.decision
        == "already_completed",
        "o replay da conclusão não foi idempotente.",
    )

    state = fetch_state(
        update_id
    )

    require(
        bool(state["payload_cleared"]),
        "a conclusão não apagou o payload.",
    )

    require(
        bool(state["ownership_cleared"]),
        "a conclusão não limpou o ownership.",
    )

    print(
        "PASS: AES-GCM adulterado bloqueado "
        "+ replay de conclusão"
    )


def test_wrong_ownership() -> None:
    update_id = UPDATE_IDS["ownership"]

    enqueue_case(
        update_id,
        label="ownership",
        max_attempts=3,
    )

    lease = claim_expected(
        update_id
    )

    wrong_lease = replace(
        lease,
        lock_token="b" * 64,
    )

    try:
        complete_authenticated_telegram_update_job_atomic(
            wrong_lease
        )

    except TelegramUpdateWorkerOwnershipError:
        pass

    else:
        raise RuntimeError(
            "STOP: ownership incorreto "
            "foi aceito."
        )

    completion = (
        complete_authenticated_telegram_update_job_atomic(
            lease
        )
    )

    require(
        completion.decision == "completed",
        "o proprietário verdadeiro não concluiu "
        "o job.",
    )

    print(
        "PASS: ownership incorreto bloqueado"
    )


def test_real_expired_lease_recovery() -> None:
    retry_id = UPDATE_IDS[
        "recovery_retry"
    ]

    dead_id = UPDATE_IDS[
        "recovery_dead"
    ]

    enqueue_case(
        retry_id,
        label="recovery-retry",
        max_attempts=2,
    )

    enqueue_case(
        dead_id,
        label="recovery-dead",
        max_attempts=1,
    )

    first = (
        claim_next_authenticated_telegram_update_job_atomic(
            lease_seconds=5,
        )
    )

    second = (
        claim_next_authenticated_telegram_update_job_atomic(
            lease_seconds=5,
        )
    )

    require(
        first is not None
        and second is not None,
        "não foi possível obter os dois "
        "leases de recuperação.",
    )

    leases = {
        first.update_id: first,
        second.update_id: second,
    }

    require(
        set(leases)
        == {
            retry_id,
            dead_id,
        },
        "os leases de recuperação não "
        "correspondem aos updates esperados.",
    )

    print(
        "Aguardando expiração real dos leases..."
    )

    time.sleep(
        6.0
    )

    recovery = (
        recover_expired_authenticated_telegram_update_jobs_atomic(
            limit=10
        )
    )

    recovered = {
        record.update_id:
            record.job_status
        for record in recovery.records
    }

    require(
        recovered.get(retry_id)
        == "queued",
        "o lease expirado recuperável "
        "não voltou para queued.",
    )

    require(
        recovered.get(dead_id)
        == "dead_letter",
        "o lease expirado esgotado "
        "não foi para dead-letter.",
    )

    try:
        complete_authenticated_telegram_update_job_atomic(
            leases[retry_id]
        )

    except TelegramUpdateWorkerOwnershipError:
        pass

    else:
        raise RuntimeError(
            "STOP: o lease antigo continuou válido "
            "após a recuperação.",
        )

    new_lease = claim_expected(
        retry_id
    )

    require(
        new_lease.job_attempt_count == 2,
        "o novo claim recuperado não está "
        "na tentativa 2.",
    )

    decrypt_expected(
        new_lease
    )

    completion = (
        complete_authenticated_telegram_update_job_atomic(
            new_lease
        )
    )

    require(
        completion.decision == "completed",
        "o job recuperado não foi concluído.",
    )

    dead_state = fetch_state(
        dead_id
    )

    require(
        dead_state["job_status"]
        == "dead_letter",
        "o estado dead-letter recuperado divergiu.",
    )

    require(
        bool(dead_state["payload_present"]),
        "a recuperação dead-letter removeu "
        "o payload criptografado.",
    )

    print(
        "PASS: recuperação real de lease expirado"
    )


def test_concurrent_workers_skip_locked() -> None:
    update_a = UPDATE_IDS[
        "concurrency_a"
    ]

    update_b = UPDATE_IDS[
        "concurrency_b"
    ]

    enqueue_case(
        update_a,
        label="concurrency-a",
        max_attempts=3,
    )

    enqueue_case(
        update_b,
        label="concurrency-b",
        max_attempts=3,
    )

    barrier = Barrier(2)

    def concurrent_claim():
        barrier.wait(
            timeout=10
        )

        return (
            claim_next_authenticated_telegram_update_job_atomic(
                lease_seconds=120,
            )
        )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        future_a = executor.submit(
            concurrent_claim
        )

        future_b = executor.submit(
            concurrent_claim
        )

        lease_a = future_a.result(
            timeout=30
        )

        lease_b = future_b.result(
            timeout=30
        )

    require(
        lease_a is not None
        and lease_b is not None,
        "um dos workers não recebeu job.",
    )

    require(
        {
            lease_a.update_id,
            lease_b.update_id,
        }
        == {
            update_a,
            update_b,
        },
        "os workers concorrentes receberam "
        "updates inesperados ou duplicados.",
    )

    require(
        lease_a.update_id
        != lease_b.update_id,
        "dois workers receberam o mesmo job.",
    )

    require(
        lease_a.lock_token
        != lease_b.lock_token,
        "os workers receberam o mesmo "
        "token de ownership.",
    )

    decrypt_expected(
        lease_a
    )

    decrypt_expected(
        lease_b
    )

    complete_authenticated_telegram_update_job_atomic(
        lease_a
    )

    complete_authenticated_telegram_update_job_atomic(
        lease_b
    )

    print(
        "PASS: dois workers concorrentes "
        "com SKIP LOCKED"
    )


def run_validation() -> None:
    all_ids = list(
        UPDATE_IDS.values()
    )

    print("=" * 112)
    print(
        "F2H2-F3 — VALIDAÇÃO AVANÇADA REAL "
        "DA FILA TELEGRAM"
    )
    print("=" * 112)

    print(
        "Casos sintéticos:",
        len(all_ids),
    )

    with cursor_postgres(
        dict_cursor=True,
        commit_automatico=True,
    ) as lock_cursor:
        lock_cursor.execute(
            """
            SELECT pg_try_advisory_lock(
                hashtext(%(lock_key)s)
            ) AS acquired;
            """,
            {
                "lock_key":
                    ADVISORY_LOCK_KEY,
            },
        )

        acquired = bool(
            lock_cursor.fetchone()[
                "acquired"
            ]
        )

        require(
            acquired,
            "outra validação avançada "
            "já está em execução.",
        )

        try:
            verify_empty_queue()

            test_retry_and_replay()
            test_dead_letter_and_replay()

            test_authenticated_decryption_and_completion_replay()

            test_wrong_ownership()
            test_real_expired_lease_recovery()

            test_concurrent_workers_skip_locked()

            print()
            print("=" * 112)
            print("RESULTADO")
            print("=" * 112)

            print(
                "STATUS: "
                "ADVANCED_REAL_QUEUE_VALIDATION_APPROVED"
            )

            print(
                "Retry, dead-letter, replay, "
                "segurança, recuperação e "
                "concorrência foram aprovados."
            )

        finally:
            try:
                cleanup(
                    all_ids
                )

                receipt_count, job_count = (
                    verify_cleanup(
                        all_ids
                    )
                )

                print()
                print(
                    "Limpeza receipts:",
                    receipt_count == 0,
                )

                print(
                    "Limpeza jobs:",
                    job_count == 0,
                )

                require(
                    receipt_count == 0,
                    "a limpeza dos receipts falhou.",
                )

                require(
                    job_count == 0,
                    "a limpeza dos jobs falhou.",
                )

            finally:
                lock_cursor.execute(
                    """
                    SELECT pg_advisory_unlock(
                        hashtext(%(lock_key)s)
                    );
                    """,
                    {
                        "lock_key":
                            ADVISORY_LOCK_KEY,
                    },
                )


if __name__ == "__main__":
    run_validation()
