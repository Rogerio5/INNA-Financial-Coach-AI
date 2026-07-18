BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '15s';

DROP TABLE IF EXISTS public.telegram_update_jobs;

COMMIT;
