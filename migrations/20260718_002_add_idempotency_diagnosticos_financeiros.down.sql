BEGIN;

SELECT pg_advisory_xact_lock(
    hashtext(
        'inna:20260718:add_diagnostico_idempotency'
    )
);

DROP INDEX IF EXISTS
    public.ux_diagnosticos_usuario_idempotency;

ALTER TABLE
    public.diagnosticos_financeiros
DROP CONSTRAINT IF EXISTS
    ck_diagnosticos_idempotency_consistencia;

ALTER TABLE
    public.diagnosticos_financeiros
DROP COLUMN IF EXISTS
    request_fingerprint;

ALTER TABLE
    public.diagnosticos_financeiros
DROP COLUMN IF EXISTS
    idempotency_key;

COMMIT;
