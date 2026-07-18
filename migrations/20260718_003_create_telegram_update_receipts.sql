/*
Migração: cria uma inbox durável para updates Telegram.

Objetivos:
- impedir replay após reinício da API;
- coordenar múltiplas instâncias;
- permitir recuperação de processamento interrompido;
- não armazenar o conteúdo sensível do update.
*/

BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';

SELECT pg_advisory_xact_lock(
    hashtext(
        'inna:20260718:create_telegram_update_receipts'
    )
);

CREATE TABLE IF NOT EXISTS
    public.telegram_update_receipts (
        update_id BIGINT PRIMARY KEY,

        update_fingerprint VARCHAR(64)
            NOT NULL,

        claim_token VARCHAR(64)
            NOT NULL,

        status VARCHAR(20)
            NOT NULL
            DEFAULT 'processing',

        attempt_count INTEGER
            NOT NULL
            DEFAULT 1,

        first_received_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        last_received_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        claimed_at TIMESTAMPTZ
            NOT NULL
            DEFAULT NOW(),

        lease_expires_at TIMESTAMPTZ
            NOT NULL,

        completed_at TIMESTAMPTZ,

        failed_at TIMESTAMPTZ,

        last_error_code VARCHAR(64),

        CONSTRAINT
            ck_telegram_update_id_nonnegative
        CHECK (
            update_id >= 0
        ),

        CONSTRAINT
            ck_telegram_update_fingerprint_sha256
        CHECK (
            char_length(
                update_fingerprint
            ) = 64

            AND update_fingerprint
                ~ '^[0-9a-f]{64}$'
        ),

        CONSTRAINT
            ck_telegram_update_claim_token_sha256
        CHECK (
            char_length(
                claim_token
            ) = 64

            AND claim_token
                ~ '^[0-9a-f]{64}$'
        ),

        CONSTRAINT
            ck_telegram_update_status
        CHECK (
            status IN (
                'processing',
                'completed',
                'failed'
            )
        ),

        CONSTRAINT
            ck_telegram_update_attempt_count
        CHECK (
            attempt_count
                BETWEEN 1 AND 1000000
        ),

        CONSTRAINT
            ck_telegram_update_error_code_format
        CHECK (
            last_error_code IS NULL

            OR (
                char_length(
                    last_error_code
                ) BETWEEN 1 AND 64

                AND btrim(
                    last_error_code
                ) = last_error_code

                AND last_error_code
                    ~ '^[a-z0-9][a-z0-9._:-]{0,63}$'
            )
        ),

        CONSTRAINT
            ck_telegram_update_lifecycle
        CHECK (
            (
                status = 'processing'

                AND completed_at IS NULL
                AND failed_at IS NULL
                AND last_error_code IS NULL
            )

            OR (
                status = 'completed'

                AND completed_at IS NOT NULL
                AND failed_at IS NULL
                AND last_error_code IS NULL
            )

            OR (
                status = 'failed'

                AND completed_at IS NULL
                AND failed_at IS NOT NULL
                AND last_error_code IS NOT NULL
            )
        ),

        CONSTRAINT
            ck_telegram_update_received_order
        CHECK (
            first_received_at
                <= last_received_at
        )
    );

CREATE INDEX IF NOT EXISTS
    ix_telegram_update_receipts_status_lease
ON public.telegram_update_receipts (
    status,
    lease_expires_at,
    update_id
)
WHERE status IN (
    'processing',
    'failed'
);

CREATE INDEX IF NOT EXISTS
    ix_telegram_update_receipts_last_received
ON public.telegram_update_receipts (
    last_received_at DESC,
    update_id DESC
);

COMMENT ON TABLE
    public.telegram_update_receipts
IS
    'Inbox durável e sem payload para controle '
    'de replay e processamento de updates Telegram.';

COMMENT ON COLUMN
    public.telegram_update_receipts.update_fingerprint
IS
    'SHA-256 hexadecimal do JSON canônico autenticado.';

COMMENT ON COLUMN
    public.telegram_update_receipts.claim_token
IS
    'Token SHA-256 aleatório que identifica o '
    'proprietário atual do lease.';

COMMENT ON COLUMN
    public.telegram_update_receipts.lease_expires_at
IS
    'Prazo do claim atual para recuperação após falha.';

COMMENT ON COLUMN
    public.telegram_update_receipts.last_error_code
IS
    'Código operacional sanitizado; nunca contém '
    'mensagens de exceção, tokens ou dados financeiros.';

COMMIT;
