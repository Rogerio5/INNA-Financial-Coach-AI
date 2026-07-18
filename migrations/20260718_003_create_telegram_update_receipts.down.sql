/*
Rollback da inbox durável de updates Telegram.

Atenção:
a remoção da tabela elimina o histórico operacional
usado para impedir replay após reinícios.
*/

BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';

SELECT pg_advisory_xact_lock(
    hashtext(
        'inna:20260718:create_telegram_update_receipts'
    )
);

DROP TABLE IF EXISTS
    public.telegram_update_receipts;

COMMIT;
