BEGIN;
CREATE TABLE IF NOT EXISTS inna_credit_wallets (
 user_id TEXT PRIMARY KEY,
 balance BIGINT NOT NULL DEFAULT 0 CHECK (balance >= 0),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS inna_credit_operations (
 user_id TEXT NOT NULL REFERENCES inna_credit_wallets(user_id),
 operation_id TEXT NOT NULL,
 amount BIGINT NOT NULL CHECK (amount > 0),
 kind TEXT NOT NULL CHECK (kind IN ('grant','usage')),
 source TEXT NOT NULL,
 state TEXT NOT NULL CHECK (state IN ('reserved','completed','refunded')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY(user_id,operation_id)
);
CREATE TABLE IF NOT EXISTS inna_credit_ledger (
 entry_id BIGSERIAL PRIMARY KEY,
 user_id TEXT NOT NULL,
 operation_id TEXT NOT NULL,
 event TEXT NOT NULL CHECK (event IN ('grant','reserve','complete','refund')),
 delta BIGINT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 FOREIGN KEY(user_id,operation_id) REFERENCES inna_credit_operations(user_id,operation_id),
 UNIQUE(user_id,operation_id,event)
);
CREATE INDEX IF NOT EXISTS inna_credit_ledger_user_history ON inna_credit_ledger(user_id,entry_id DESC);
COMMIT;
