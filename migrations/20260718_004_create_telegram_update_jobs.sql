BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '15s';

CREATE TABLE public.telegram_update_jobs (
    update_id BIGINT PRIMARY KEY,

    status VARCHAR(20)
        NOT NULL
        DEFAULT 'queued',

    payload_ciphertext BYTEA,
    payload_nonce BYTEA,
    payload_key_id VARCHAR(64),

    payload_version SMALLINT
        NOT NULL
        DEFAULT 1,

    attempt_count INTEGER
        NOT NULL
        DEFAULT 0,

    max_attempts INTEGER
        NOT NULL
        DEFAULT 5,

    available_at TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    locked_at TIMESTAMPTZ,
    lock_expires_at TIMESTAMPTZ,
    lock_token VARCHAR(64),

    completed_at TIMESTAMPTZ,
    dead_lettered_at TIMESTAMPTZ,

    last_error_code VARCHAR(64),

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    CONSTRAINT fk_telegram_update_jobs_receipt
        FOREIGN KEY (update_id)
        REFERENCES public.telegram_update_receipts (
            update_id
        )
        ON DELETE CASCADE,

    CONSTRAINT ck_telegram_update_jobs_status
        CHECK (
            status IN (
                'queued',
                'processing',
                'completed',
                'dead_letter'
            )
        ),

    CONSTRAINT ck_telegram_update_jobs_payload_version
        CHECK (
            payload_version BETWEEN 1 AND 32767
        ),

    CONSTRAINT ck_telegram_update_jobs_attempts
        CHECK (
            attempt_count >= 0
            AND max_attempts BETWEEN 1 AND 20
            AND attempt_count <= max_attempts
        ),

    CONSTRAINT ck_telegram_update_jobs_ciphertext_size
        CHECK (
            payload_ciphertext IS NULL
            OR (
                OCTET_LENGTH(payload_ciphertext) >= 16
                AND OCTET_LENGTH(payload_ciphertext)
                    <= 1048576
            )
        ),

    CONSTRAINT ck_telegram_update_jobs_nonce_size
        CHECK (
            payload_nonce IS NULL
            OR OCTET_LENGTH(payload_nonce) = 12
        ),

    CONSTRAINT ck_telegram_update_jobs_key_id
        CHECK (
            payload_key_id IS NULL
            OR payload_key_id ~
                '^[A-Za-z0-9._:-]{1,64}$'
        ),

    CONSTRAINT ck_telegram_update_jobs_lock_token
        CHECK (
            lock_token IS NULL
            OR lock_token ~ '^[0-9a-f]{64}$'
        ),

    CONSTRAINT ck_telegram_update_jobs_error_code
        CHECK (
            last_error_code IS NULL
            OR last_error_code ~
                '^[a-z0-9._:-]{1,64}$'
        ),

    CONSTRAINT ck_telegram_update_jobs_payload_lifecycle
        CHECK (
            (
                status IN (
                    'queued',
                    'processing',
                    'dead_letter'
                )
                AND payload_ciphertext IS NOT NULL
                AND payload_nonce IS NOT NULL
                AND payload_key_id IS NOT NULL
            )
            OR
            (
                status = 'completed'
                AND payload_ciphertext IS NULL
                AND payload_nonce IS NULL
                AND payload_key_id IS NULL
            )
        ),

    CONSTRAINT ck_telegram_update_jobs_lock_lifecycle
        CHECK (
            (
                status = 'processing'
                AND locked_at IS NOT NULL
                AND lock_expires_at IS NOT NULL
                AND lock_token IS NOT NULL
            )
            OR
            (
                status <> 'processing'
                AND locked_at IS NULL
                AND lock_expires_at IS NULL
                AND lock_token IS NULL
            )
        ),

    CONSTRAINT ck_telegram_update_jobs_terminal_lifecycle
        CHECK (
            (
                status = 'completed'
                AND completed_at IS NOT NULL
                AND dead_lettered_at IS NULL
            )
            OR
            (
                status = 'dead_letter'
                AND completed_at IS NULL
                AND dead_lettered_at IS NOT NULL
            )
            OR
            (
                status IN (
                    'queued',
                    'processing'
                )
                AND completed_at IS NULL
                AND dead_lettered_at IS NULL
            )
        ),

    CONSTRAINT ck_telegram_update_jobs_attempt_lifecycle
        CHECK (
            status = 'queued'
            OR attempt_count >= 1
        ),

    CONSTRAINT ck_telegram_update_jobs_timestamp_order
        CHECK (
            updated_at >= created_at
            AND available_at >= created_at
            AND (
                locked_at IS NULL
                OR locked_at >= created_at
            )
            AND (
                lock_expires_at IS NULL
                OR (
                    locked_at IS NOT NULL
                    AND lock_expires_at > locked_at
                )
            )
            AND (
                completed_at IS NULL
                OR completed_at >= created_at
            )
            AND (
                dead_lettered_at IS NULL
                OR dead_lettered_at >= created_at
            )
        )
);

CREATE INDEX ix_telegram_update_jobs_dequeue
    ON public.telegram_update_jobs (
        available_at,
        created_at,
        update_id
    )
    WHERE status = 'queued';

CREATE INDEX ix_telegram_update_jobs_processing_lease
    ON public.telegram_update_jobs (
        lock_expires_at,
        update_id
    )
    WHERE status = 'processing';

CREATE INDEX ix_telegram_update_jobs_completed_retention
    ON public.telegram_update_jobs (
        completed_at,
        update_id
    )
    WHERE status = 'completed';

CREATE INDEX ix_telegram_update_jobs_dead_letter
    ON public.telegram_update_jobs (
        dead_lettered_at,
        update_id
    )
    WHERE status = 'dead_letter';

COMMIT;
