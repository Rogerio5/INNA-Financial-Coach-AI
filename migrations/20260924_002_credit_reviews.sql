BEGIN;
CREATE TABLE IF NOT EXISTS inna_credit_reviews (
 review_id BIGSERIAL PRIMARY KEY,
 user_id TEXT NOT NULL,
 operation_id TEXT NOT NULL,
 reviewer_id TEXT NOT NULL,
 decision TEXT NOT NULL CHECK (decision IN ('completed','refunded')),
 reason TEXT NOT NULL CHECK (length(reason) >= 10),
 evidence_ref TEXT NOT NULL CHECK (length(evidence_ref) >= 3),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 FOREIGN KEY(user_id,operation_id) REFERENCES inna_credit_operations(user_id,operation_id),
 UNIQUE(user_id,operation_id)
);
COMMIT;
