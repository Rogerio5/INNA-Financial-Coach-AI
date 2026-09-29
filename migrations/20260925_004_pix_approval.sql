BEGIN;
ALTER TABLE inna_manual_pix_orders ADD COLUMN IF NOT EXISTS fulfillment JSONB;
CREATE TABLE IF NOT EXISTS inna_manual_pix_reviews (
 order_id TEXT PRIMARY KEY REFERENCES inna_manual_pix_orders(order_id),
 reviewer_id TEXT NOT NULL,
 bank_reference TEXT NOT NULL UNIQUE,
 received_cents BIGINT NOT NULL CHECK(received_cents > 0),
 reason TEXT NOT NULL,
 reviewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS inna_pix_reviewers (
 user_id TEXT PRIMARY KEY REFERENCES inna_auth_users(user_id),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMIT;
