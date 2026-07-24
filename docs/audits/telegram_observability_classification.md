# F2H5-A — Classificação da observabilidade atual

Este documento classifica os logs, prints, exceções, operações duráveis e riscos de telemetria do fluxo Telegram.

## Resumo

- Prints produtivos: 10
- Logging estruturado atual: 0
- Handlers de exceção: 64
- Possíveis supressões silenciosas: 2
- Possíveis logs sensíveis: 1
- Operações da bridge identificadas: 9
- Operações de receipts identificadas: 2

## Classificação dos prints

| Arquivo | Linha | Owner | Categoria | Nível | Evento sugerido | Ação |
|---|---:|---|---|---|---|---|
| api/telegram_webhook.py | 754 | send_telegram_message | configuration | warning | telegram_configuration_send_telegram_message | Migrar para evento estruturado de configuração. |
| api/telegram_webhook.py | 746 | safe_record_telegram_event | operation_failure | error | telegram_operation_failure_safe_record_telegram_event | Migrar para evento estruturado com categoria de erro. |
| api/telegram_webhook.py | 1455 | _process_telegram_update_core | security | warning | telegram_security_process_telegram_update_core | Registrar evento sanitizado sem payload ou segredo. |
| api/telegram_webhook.py | 1792 | _process_telegram_update_core | operation_failure | error | telegram_operation_failure_process_telegram_update_core | Migrar para evento estruturado com categoria de erro. |
| api/telegram_webhook.py | 1821 | _fail_claimed_telegram_update_safely | operation_failure | error | telegram_operation_failure_fail_claimed_telegram_update_safely | Migrar para evento estruturado com categoria de erro. |
| api/telegram_webhook.py | 1827 | _fail_claimed_telegram_update_safely | operation_failure | error | telegram_operation_failure_fail_claimed_telegram_update_safely | Migrar para evento estruturado com categoria de erro. |
| api/telegram_webhook.py | 1853 | process_claimed_telegram_update | operation_failure | error | telegram_operation_failure_process_claimed_telegram_update | Migrar para evento estruturado com categoria de erro. |
| api/telegram_webhook.py | 1875 | process_claimed_telegram_update | operation_failure | error | telegram_operation_failure_process_claimed_telegram_update | Migrar para evento estruturado com categoria de erro. |
| api/telegram_webhook.py | 1885 | process_claimed_telegram_update | operation_failure | error | telegram_operation_failure_process_claimed_telegram_update | Migrar para evento estruturado com categoria de erro. |
| src/channels/telegram_update_worker.py | 311 | _emit_event | operational | info | telegram_operational_emit_event | Revisar e substituir por evento estruturado. |

### Expressões atuais dos prints

1. `print("TELEGRAM_BOT_TOKEN não configurado.")`
2. `print( "[telegram-event-log] " "Falha segura ao registrar evento." )`
3. `print( "[telegram-webhook] " "Update inválido descartado." )`
4. `print( "[telegram-webhook] " "Falha segura ao processar atualização." )`
5. `print( "[telegram-webhook] " "Falha segura ao atualizar receipt." )`
6. `print( "[telegram-webhook] " "Falha segura ao atualizar receipt." )`
7. `print( "[telegram-webhook] " "Falha segura no worker Telegram." )`
8. `print( "[telegram-webhook] " "Falha segura ao concluir receipt." )`
9. `print( "[telegram-webhook] " "Falha segura ao concluir receipt." )`
10. `print( serialized, file=stream, flush=True, )`

## Classificação dos handlers de exceção

| Arquivo | Linha | Owner | Exceção | Categoria |
|---|---:|---|---|---|
| api/telegram_webhook.py | 8 | <module> | ImportError | optimistic_concurrency |
| api/telegram_webhook.py | 745 | safe_record_telegram_event | Exception | external_service |
| api/telegram_webhook.py | 858 | format_money | Exception | application_or_unknown |
| api/telegram_webhook.py | 1285 | _sync_and_save_durable_telegram_session | Exception | optimistic_concurrency |
| api/telegram_webhook.py | 1454 | _process_telegram_update_core | TelegramUpdateContextError | security_or_identity |
| api/telegram_webhook.py | 1788 | _process_telegram_update_core | ValueError | configuration_or_validation |
| api/telegram_webhook.py | 1791 | _process_telegram_update_core | Exception | external_service |
| api/telegram_webhook.py | 1820 | _fail_claimed_telegram_update_safely | TelegramUpdateReceiptServiceError | persistence_or_infrastructure |
| api/telegram_webhook.py | 1826 | _fail_claimed_telegram_update_safely | Exception | persistence_or_infrastructure |
| api/telegram_webhook.py | 1852 | process_claimed_telegram_update | Exception | external_service |
| api/telegram_webhook.py | 1874 | process_claimed_telegram_update | TelegramUpdateReceiptServiceError | persistence_or_infrastructure |
| api/telegram_webhook.py | 1884 | process_claimed_telegram_update | Exception | persistence_or_infrastructure |
| api/telegram_webhook.py | 1918 | telegram_webhook | Exception | external_service |
| api/telegram_webhook.py | 1944 | telegram_webhook | TelegramUpdateIngressValidationError | external_service |
| api/telegram_webhook.py | 1952 | telegram_webhook | TelegramUpdateIngressConflictError | optimistic_concurrency |
| api/telegram_webhook.py | 1960 | telegram_webhook | (TelegramUpdateIngressConfigurationError, TelegramUpdateIngressConsistencyError, TelegramUpdateIngressUnavailableError) | configuration_or_validation |
| api/telegram_webhook.py | 1973 | telegram_webhook | Exception | external_service |
| src/channels/telegram_update_worker.py | 100 | _read_integer | (TypeError, ValueError, OverflowError) | configuration_or_validation |
| src/channels/telegram_update_worker.py | 132 | _read_float | (TypeError, ValueError, OverflowError) | configuration_or_validation |
| src/channels/telegram_update_worker.py | 221 | load_worker_config_from_env | TelegramUpdateRunnerConfigurationError | configuration_or_validation |
| src/channels/telegram_update_worker.py | 224 | load_worker_config_from_env | Exception | configuration_or_validation |
| src/channels/telegram_update_worker.py | 265 | load_telegram_processor | Exception | configuration_or_validation |
| src/channels/telegram_update_worker.py | 476 | _positive_integer_argument | (TypeError, ValueError, OverflowError) | configuration_or_validation |
| src/channels/telegram_update_worker.py | 546 | main | SystemExit | application_or_unknown |
| src/channels/telegram_update_worker.py | 564 | main | (TelegramUpdateJobConfigurationError, TelegramUpdateRunnerConfigurationError) | configuration_or_validation |
| src/channels/telegram_update_worker.py | 581 | main | Exception | external_service |
| src/channels/telegram_update_worker.py | 636 | main | KeyboardInterrupt | external_service |
| src/channels/telegram_update_worker.py | 649 | main | (TelegramUpdateJobConfigurationError, TelegramUpdateRunnerConfigurationError) | configuration_or_validation |
| src/channels/telegram_update_worker.py | 666 | main | Exception | external_service |
| src/channels/telegram_update_worker.py | 463 | _restore_signal_handlers | Exception | persistence_or_infrastructure |
| src/services/telegram_conversation_state/contracts.py | 329 | normalize_telegram_state | (TypeError, ValueError, OverflowError, RecursionError) | configuration_or_validation |
| src/services/telegram_conversation_state/contracts.py | 358 | normalize_telegram_state | (TypeError, ValueError) | configuration_or_validation |
| src/services/telegram_conversation_state/repository.py | 213 | _serialize_state | (TypeError, ValueError, OverflowError, RecursionError) | configuration_or_validation |
| src/services/telegram_conversation_state/repository.py | 277 | _deserialize_state | TelegramConversationStateValidationError | external_service |
| src/services/telegram_conversation_state/repository.py | 330 | _record_from_row | (KeyError, TypeError) | external_service |
| src/services/telegram_conversation_state/repository.py | 352 | _record_from_row | TelegramConversationStateValidationError | external_service |
| src/services/telegram_conversation_state/repository.py | 402 | _safe_rollback | Exception | application_or_unknown |
| src/services/telegram_conversation_state/repository.py | 458 | load_telegram_conversation_state | TelegramConversationStateError | external_service |
| src/services/telegram_conversation_state/repository.py | 461 | load_telegram_conversation_state | Exception | external_service |
| src/services/telegram_conversation_state/repository.py | 567 | create_telegram_conversation_state | TelegramConversationStateError | external_service |
| src/services/telegram_conversation_state/repository.py | 570 | create_telegram_conversation_state | Exception | external_service |
| src/services/telegram_conversation_state/repository.py | 672 | save_telegram_conversation_state | TelegramConversationStateError | external_service |
| src/services/telegram_conversation_state/repository.py | 675 | save_telegram_conversation_state | Exception | external_service |
| src/services/telegram_conversation_state/repository.py | 732 | delete_telegram_conversation_state | TelegramConversationStateError | external_service |
| src/services/telegram_conversation_state/repository.py | 735 | delete_telegram_conversation_state | Exception | external_service |
| src/services/telegram_conversation_state/repository.py | 787 | delete_expired_telegram_conversation_states | TelegramConversationStateError | external_service |
| src/services/telegram_conversation_state/repository.py | 790 | delete_expired_telegram_conversation_states | Exception | external_service |
| src/services/telegram_conversation_state/repository.py | 249 | _deserialize_state | UnicodeDecodeError | external_service |
| src/services/telegram_conversation_state/repository.py | 263 | _deserialize_state | (TypeError, ValueError, json.JSONDecodeError) | configuration_or_validation |
| src/services/telegram_conversation_state/repository.py | 446 | load_telegram_conversation_state | TelegramConversationStateError | persistence_or_infrastructure |
| src/services/telegram_conversation_state/repository.py | 452 | load_telegram_conversation_state | Exception | persistence_or_infrastructure |
| src/services/telegram_conversation_state/repository.py | 555 | create_telegram_conversation_state | TelegramConversationStateError | persistence_or_infrastructure |
| src/services/telegram_conversation_state/repository.py | 561 | create_telegram_conversation_state | Exception | persistence_or_infrastructure |
| src/services/telegram_conversation_state/repository.py | 660 | save_telegram_conversation_state | TelegramConversationStateError | persistence_or_infrastructure |
| src/services/telegram_conversation_state/repository.py | 666 | save_telegram_conversation_state | Exception | persistence_or_infrastructure |
| src/services/telegram_conversation_state/repository.py | 720 | delete_telegram_conversation_state | TelegramConversationStateError | persistence_or_infrastructure |
| src/services/telegram_conversation_state/repository.py | 726 | delete_telegram_conversation_state | Exception | persistence_or_infrastructure |
| src/services/telegram_conversation_state/repository.py | 775 | delete_expired_telegram_conversation_states | TelegramConversationStateError | persistence_or_infrastructure |
| src/services/telegram_conversation_state/repository.py | 781 | delete_expired_telegram_conversation_states | Exception | persistence_or_infrastructure |
| src/services/telegram_conversation_state/store.py | 280 | open | TelegramConversationStateConflictError | optimistic_concurrency |
| src/services/telegram_conversation_state/webhook_bridge.py | 640 | _invoke | TelegramConversationStateError | external_service |
| src/services/telegram_conversation_state/webhook_bridge.py | 643 | _invoke | Exception | external_service |
| src/services/telegram_conversation_state/webhook_bridge.py | 609 | _get_runtime | TelegramConversationStateError | external_service |
| src/services/telegram_conversation_state/webhook_bridge.py | 612 | _get_runtime | Exception | external_service |

## Possíveis supressões silenciosas

- `src/channels/telegram_update_worker.py:546` — `main` — exceção `SystemExit` — pass=False — return silencioso=True
- `src/services/telegram_conversation_state/repository.py:402` — `_safe_rollback` — exceção `Exception` — pass=True — return silencioso=False

## Possíveis exposições sensíveis

- `api/telegram_webhook.py:754` — `send_telegram_message` — termos detectados: `telegram_bot_token` — expressão: `print("TELEGRAM_BOT_TOKEN não configurado.")`

## Operações que deverão receber métricas

### Estado conversacional

- `delete_session`
- `load_or_open_session`
- `reload_session`
- `resolve_language`
- `save_session`

### Receipts e fila

- `complete_authenticated_telegram_update`
- `fail_authenticated_telegram_update`

## Dados proibidos na telemetria

- nome do usuário
- texto integral da mensagem
- renda mensal
- gastos fixos ou variáveis
- dívidas
- reserva financeira
- objetivo financeiro
- token do Telegram
- credenciais PostgreSQL
- URL de banco de dados
- payload criptografado ou descriptografado

## Campos operacionais permitidos

- `operation`
- `outcome`
- `error_category`
- `duration_ms`
- `session_version`
- `retry_count`
- `conflict_recovered`
- `worker_status`
- `receipt_status`
- update_id apenas em logs, nunca como label de métrica
- request_id apenas em logs e traces

## Decisões arquiteturais

- Substituir prints produtivos por uma abstração de eventos estruturados.
- Não acoplar o domínio diretamente a Prometheus, Grafana ou OpenTelemetry.
- Métricas devem usar apenas labels de baixa cardinalidade.
- Falhas de telemetria não podem interromper a operação principal.
- Exceções da persistência não devem ser engolidas pela camada de métricas.
- Identificadores de usuário, chat e sessão não devem ser labels de métricas.
- Toda operação durável deve registrar resultado e duração.
- Toda recuperação de conflito deve ser distinguida de um conflito não recuperado.

## Próxima implementação

Criar contratos desacoplados para métricas e eventos:

- `TelegramConversationMetrics`
- `TelegramOperationalEventSink`
- `NoOpTelegramConversationMetrics`
- `InMemoryTelegramConversationMetrics`
- `NoOpTelegramOperationalEventSink`
- `InMemoryTelegramOperationalEventSink`
