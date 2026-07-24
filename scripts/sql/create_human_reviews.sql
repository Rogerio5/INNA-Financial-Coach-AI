BEGIN;

CREATE TABLE IF NOT EXISTS public.human_reviews (
    id BIGSERIAL PRIMARY KEY,

    review_id VARCHAR(255) NOT NULL,
    thread_id VARCHAR(255) NOT NULL,

    status VARCHAR(40) NOT NULL DEFAULT 'pending',

    requested_by VARCHAR(160) NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    trigger VARCHAR(160) NOT NULL DEFAULT '',
    risk_level VARCHAR(40) NOT NULL DEFAULT '',

    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    allowed_actions JSONB NOT NULL DEFAULT '[]'::jsonb,

    decision_action VARCHAR(40) NOT NULL DEFAULT '',
    reviewer_id VARCHAR(160) NOT NULL DEFAULT '',
    reviewer_comment TEXT NOT NULL DEFAULT '',
    rejection_reason TEXT NOT NULL DEFAULT '',
    corrections JSONB NOT NULL DEFAULT '{}'::jsonb,

    resume_route VARCHAR(160) NOT NULL DEFAULT '',

    processing_request_id VARCHAR(200) NOT NULL DEFAULT '',
    processing_started_at TIMESTAMPTZ,

    failure_reason TEXT NOT NULL DEFAULT '',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,

    CONSTRAINT uq_human_reviews_review_id
        UNIQUE (review_id),

    CONSTRAINT ck_human_reviews_status
        CHECK (
            status IN (
                'pending',
                'processing',
                'approved',
                'corrected',
                'rejected',
                'cancelled',
                'resume_failed'
            )
        ),

    CONSTRAINT ck_human_reviews_payload_object
        CHECK (
            jsonb_typeof(payload) = 'object'
        ),

    CONSTRAINT ck_human_reviews_allowed_actions_array
        CHECK (
            jsonb_typeof(allowed_actions) = 'array'
        ),

    CONSTRAINT ck_human_reviews_corrections_object
        CHECK (
            jsonb_typeof(corrections) = 'object'
        )
);

CREATE INDEX IF NOT EXISTS
    idx_human_reviews_status_created_at
ON public.human_reviews (
    status,
    created_at
);

CREATE INDEX IF NOT EXISTS
    idx_human_reviews_thread_id
ON public.human_reviews (
    thread_id
);

CREATE INDEX IF NOT EXISTS
    idx_human_reviews_reviewer_id
ON public.human_reviews (
    reviewer_id
)
WHERE reviewer_id <> '';

CREATE INDEX IF NOT EXISTS
    idx_human_reviews_processing
ON public.human_reviews (
    processing_started_at
)
WHERE status = 'processing';

COMMIT;
