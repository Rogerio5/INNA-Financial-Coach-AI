BEGIN;

SELECT pg_advisory_xact_lock(
    hashtext(
        'inna:20260718:add_diagnostico_idempotency'
    )
);

ALTER TABLE
    public.diagnosticos_financeiros
ADD COLUMN IF NOT EXISTS
    idempotency_key VARCHAR(160);

ALTER TABLE
    public.diagnosticos_financeiros
ADD COLUMN IF NOT EXISTS
    request_fingerprint VARCHAR(64);

DO $migration$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE
            conname =
                'ck_diagnosticos_idempotency_consistencia'
            AND conrelid =
                'public.diagnosticos_financeiros'
                ::regclass
    ) THEN
        ALTER TABLE
            public.diagnosticos_financeiros
        ADD CONSTRAINT
            ck_diagnosticos_idempotency_consistencia
        CHECK (
            (
                idempotency_key IS NULL
                AND request_fingerprint IS NULL
            )
            OR
            (
                usuario_id IS NOT NULL
                AND idempotency_key IS NOT NULL
                AND request_fingerprint IS NOT NULL

                AND btrim(idempotency_key)
                    = idempotency_key

                AND char_length(idempotency_key)
                    BETWEEN 16 AND 160

                AND idempotency_key
                    ~ '^[A-Za-z0-9._:-]{16,160}$'

                AND char_length(
                    request_fingerprint
                ) = 64

                AND request_fingerprint
                    ~ '^[0-9a-f]{64}$'
            )
        ) NOT VALID;
    END IF;
END
$migration$;

ALTER TABLE
    public.diagnosticos_financeiros
VALIDATE CONSTRAINT
    ck_diagnosticos_idempotency_consistencia;

CREATE UNIQUE INDEX IF NOT EXISTS
    ux_diagnosticos_usuario_idempotency
ON public.diagnosticos_financeiros (
    usuario_id,
    idempotency_key
)
WHERE
    usuario_id IS NOT NULL
    AND idempotency_key IS NOT NULL;

COMMENT ON COLUMN
    public.diagnosticos_financeiros.idempotency_key
IS
    'Chave vinculada ao usuário para impedir '
    'duplicidade de diagnósticos.';

COMMENT ON COLUMN
    public.diagnosticos_financeiros.request_fingerprint
IS
    'SHA-256 hexadecimal do conteúdo financeiro '
    'validado associado à chave de idempotência.';

COMMIT;
