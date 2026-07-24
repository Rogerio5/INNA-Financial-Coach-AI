BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';

CREATE TABLE IF NOT EXISTS
    public.telegram_conversation_states
(
    telegram_user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,

    state JSONB NOT NULL
        DEFAULT '{}'::jsonb,

    language VARCHAR(16),

    state_version BIGINT NOT NULL
        DEFAULT 1,

    expires_at TIMESTAMPTZ NOT NULL,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT
        pk_telegram_conversation_states
        PRIMARY KEY
        (
            telegram_user_id,
            chat_id
        ),

    CONSTRAINT
        ck_telegram_conversation_states_user_id
        CHECK
        (
            telegram_user_id > 0
        ),

    CONSTRAINT
        ck_telegram_conversation_states_chat_id
        CHECK
        (
            chat_id <> 0
        ),

    CONSTRAINT
        ck_telegram_conversation_states_state
        CHECK
        (
            jsonb_typeof(state) = 'object'
        ),

    CONSTRAINT
        ck_telegram_conversation_states_language
        CHECK
        (
            language IS NULL
            OR
            (
                language = BTRIM(language)
                AND CHAR_LENGTH(language)
                    BETWEEN 2 AND 16
            )
        ),

    CONSTRAINT
        ck_telegram_conversation_states_version
        CHECK
        (
            state_version >= 1
        ),

    CONSTRAINT
        ck_telegram_conversation_states_timestamps
        CHECK
        (
            updated_at >= created_at
        ),

    CONSTRAINT
        ck_telegram_conversation_states_expiration
        CHECK
        (
            expires_at > updated_at
        )
);

CREATE INDEX IF NOT EXISTS
    idx_telegram_conversation_states_expires_at
ON
    public.telegram_conversation_states
    (
        expires_at
    );

CREATE INDEX IF NOT EXISTS
    idx_telegram_conversation_states_updated_at
ON
    public.telegram_conversation_states
    (
        updated_at DESC
    );

COMMENT ON TABLE
    public.telegram_conversation_states
IS
    'Estado conversacional mínimo e temporário do canal Telegram.';

COMMENT ON COLUMN
    public.telegram_conversation_states.telegram_user_id
IS
    'Identidade técnica confiável do usuário Telegram.';

COMMENT ON COLUMN
    public.telegram_conversation_states.chat_id
IS
    'Escopo da conversa no Telegram, incluindo chats privados e grupos.';

COMMENT ON COLUMN
    public.telegram_conversation_states.state
IS
    'Estado mínimo da conversa como objeto JSONB; não armazena update bruto.';

COMMENT ON COLUMN
    public.telegram_conversation_states.language
IS
    'Idioma selecionado ou inferido para o escopo da conversa.';

COMMENT ON COLUMN
    public.telegram_conversation_states.state_version
IS
    'Versão monotônica usada para controle otimista de concorrência.';

COMMENT ON COLUMN
    public.telegram_conversation_states.expires_at
IS
    'Momento a partir do qual o estado poderá ser removido com segurança.';

COMMIT;
