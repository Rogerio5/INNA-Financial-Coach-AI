BEGIN;
CREATE TABLE IF NOT EXISTS inna_paid_analyses (
 user_id TEXT NOT NULL,
 request_id UUID NOT NULL,
 quote_id UUID NOT NULL UNIQUE,
 payload_hash TEXT NOT NULL,
 cost INTEGER NOT NULL CHECK (cost > 0),
 state TEXT NOT NULL DEFAULT 'quoted' CHECK (state IN ('quoted','running','completed','refunded','needs_review')),
 result JSONB,
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY(user_id, request_id)
);
CREATE INDEX IF NOT EXISTS inna_paid_analysis_pending ON inna_paid_analyses(state, updated_at);
CREATE TABLE IF NOT EXISTS inna_paid_analysis_reviews (
 quote_id UUID PRIMARY KEY REFERENCES inna_paid_analyses(quote_id),
 reviewer_id TEXT NOT NULL,
 outcome TEXT NOT NULL CHECK(outcome IN ('completed','refunded')),
 reason TEXT NOT NULL,
 evidence_ref TEXT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMIT;
