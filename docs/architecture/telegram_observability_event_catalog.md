# Catálogo de eventos de observabilidade do Telegram

Este catálogo define os eventos operacionais permitidos para o fluxo Telegram durável.

## Regras gerais

- Os nomes dos eventos são estáveis e em `snake_case`.
- O campo `event` deve conter exatamente o nome catalogado.
- Eventos não devem carregar payloads, texto de mensagens ou dados financeiros.
- Exceções devem ser convertidas em categorias sanitizadas.
- IDs de alta cardinalidade podem existir em logs e traces, mas nunca como labels de métricas.

## Catálogo

| Evento | Nível | Categoria | Componente | Campos obrigatórios | Campos proibidos |
|---|---|---|---|---|---|
| `telegram_configuration_missing` | warning | configuration | webhook | `event`, `component`, `configuration_key`, `outcome` | `configuration_value`, `token`, `secret` |
| `telegram_update_invalid_discarded` | warning | security | webhook | `event`, `component`, `outcome`, `error_category` | `payload`, `message_text`, `token` |
| `telegram_update_processing_failed` | error | operation_failure | webhook | `event`, `component`, `outcome`, `error_category` | `payload`, `message_text`, `financial_data` |
| `telegram_session_load_completed` | info | conversation_state | bridge | `event`, `operation`, `outcome`, `duration_ms` | `chat_id`, `telegram_user_id`, `state` |
| `telegram_session_save_completed` | info | conversation_state | bridge | `event`, `operation`, `outcome`, `duration_ms` | `chat_id`, `telegram_user_id`, `state` |
| `telegram_session_save_conflict` | warning | optimistic_concurrency | bridge | `event`, `operation`, `outcome`, `conflict_recovered` | `chat_id`, `telegram_user_id`, `state` |
| `telegram_session_reload_completed` | info | conversation_state | bridge | `event`, `operation`, `outcome`, `duration_ms` | `chat_id`, `telegram_user_id`, `state` |
| `telegram_session_delete_completed` | info | conversation_state | bridge | `event`, `operation`, `outcome`, `duration_ms` | `chat_id`, `telegram_user_id`, `state` |
| `telegram_language_resolution_completed` | info | conversation_state | bridge | `event`, `operation`, `outcome`, `duration_ms` | `chat_id`, `telegram_user_id`, `message_text` |
| `telegram_worker_started` | info | worker_lifecycle | worker | `event`, `component`, `outcome` | `database_url`, `token`, `secret` |
| `telegram_worker_claim_empty` | debug | worker_lifecycle | worker | `event`, `component`, `outcome` | `payload` |
| `telegram_worker_update_claimed` | info | worker_processing | worker | `event`, `component`, `outcome` | `payload`, `message_text` |
| `telegram_worker_update_completed` | info | worker_processing | worker | `event`, `component`, `outcome`, `duration_ms` | `payload`, `message_text` |
| `telegram_worker_update_failed` | error | worker_processing | worker | `event`, `component`, `outcome`, `error_category`, `duration_ms` | `payload`, `message_text`, `exception_message_raw` |
| `telegram_receipt_completed` | info | receipt | webhook | `event`, `operation`, `outcome` | `payload`, `encrypted_payload` |
| `telegram_receipt_failed` | error | receipt | webhook | `event`, `operation`, `outcome`, `error_category` | `payload`, `encrypted_payload`, `exception_message_raw` |
| `telegram_repository_rollback_failed` | warning | persistence | repository | `event`, `operation`, `outcome`, `error_category` | `database_url`, `query`, `parameters`, `exception_message_raw` |

## Categorias de erro permitidas

- `configuration`
- `validation`
- `security`
- `identity`
- `persistence`
- `external_service`
- `optimistic_conflict`
- `timeout`
- `unavailable`
- `unknown`

## Resultados permitidos

- `success`
- `error`
- `conflict`
- `recovered`
- `discarded`
- `skipped`
