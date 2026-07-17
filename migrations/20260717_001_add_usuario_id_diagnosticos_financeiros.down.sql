/*
Rollback da migração de identidade financeira.

Atenção:
remover a coluna também remove as identidades já gravadas.
*/

BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';

SELECT pg_advisory_xact_lock(
    hashtext(
        'inna:20260717:add_usuario_id_diagnosticos'
    )
);

DROP INDEX IF EXISTS
    public.ix_diagnosticos_usuario_data;

ALTER TABLE public.diagnosticos_financeiros
DROP CONSTRAINT IF EXISTS
    ck_diagnosticos_usuario_id_formato;

ALTER TABLE public.diagnosticos_financeiros
DROP COLUMN IF EXISTS usuario_id;

COMMIT;
