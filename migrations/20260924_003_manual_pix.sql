BEGIN;
CREATE TABLE IF NOT EXISTS inna_manual_pix_orders (
 order_id TEXT PRIMARY KEY,
 user_id TEXT NOT NULL,
 product_code TEXT NOT NULL,
 amount_cents BIGINT NOT NULL CHECK(amount_cents > 0),
 pix_payload TEXT NOT NULL,
 receiver_name TEXT NOT NULL,
 receiver_city TEXT NOT NULL,
 receiver_key TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'awaiting_manual_verification' CHECK(status IN ('awaiting_manual_verification','verified','cancelled')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS inna_manual_pix_orders_owner ON inna_manual_pix_orders(user_id,created_at DESC);
COMMIT;
