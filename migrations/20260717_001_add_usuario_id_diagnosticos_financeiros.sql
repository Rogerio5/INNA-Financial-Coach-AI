/*
Migração: adiciona identidade de usuário aos diagnósticos.

Características:
- compatível com os registros antigos;
- idempotente;
- sem backfill por nome;
- sem NOT NULL nesta primeira fase;
- índice parcial para consultas por usuário.
*/

BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';

SELECT pg_advisory_xact_lock(
    hashtext(
        'inna:20260717:add_usuario_id_diagnosticos'
    )
);

ALTER TABLE public.diagnosticos_financeiros
ADD COLUMN IF NOT EXISTS usuario_id VARCHAR(160);

DO $migration$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE
            conname =
                'ck_diagnosticos_usuario_id_formato'
            AND conrelid =
                'public.diagnosticos_financeiros'
                ::regclass
    ) THEN
        ALTER TABLE
            public.diagnosticos_financeiros
        ADD CONSTRAINT
            ck_diagnosticos_usuario_id_formato
        CHECK (
            usuario_id IS NULL
            OR char_length(
                btrim(usuario_id)
            ) BETWEEN 1 AND 160
        )
        NOT VALID;
    END IF;
END
$migration$;

ALTER TABLE public.diagnosticos_financeiros
VALIDATE CONSTRAINT
    ck_diagnosticos_usuario_id_formato;

CREATE INDEX IF NOT EXISTS
    ix_diagnosticos_usuario_data
ON public.diagnosticos_financeiros (
    usuario_id,
    data_hora DESC,
    id DESC
)
WHERE usuario_id IS NOT NULL;

COMMENT ON COLUMN
    public.diagnosticos_financeiros.usuario_id
IS
    'Identidade confiável do usuário. '
    'Registros legados permanecem NULL.';

COMMIT;
