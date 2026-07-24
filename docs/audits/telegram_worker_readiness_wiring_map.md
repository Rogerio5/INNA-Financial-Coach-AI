# F2H5-H2E — Wiring produtivo do readiness Telegram

## Resumo

- Imports relevantes: 5
- Definições relevantes: 12
- Atribuições relevantes: 32
- Leituras de ambiente: 0
- Candidatos seguros: 19
- Operações mutantes identificadas: 112

## Imports relevantes

- `src/channels/telegram_update_worker.py:21` — `src.services.telegram_observability: JsonTelegramOperationalEventSink, NoOpTelegramConversationMetrics, NoOpTelegramOperationalEventSink, TelegramConversationMetrics, TelegramOperationalEventSink, CompositeTelegramConversationMetrics, InMemoryTelegramProductiveMetrics, ProductiveTelegramConversationMetricsAdapter, SafeTelegramProductiveMetrics, SafeTelegramProductiveOperations, TelegramProductiveOperationsRecorder`
- `src/channels/telegram_update_worker.py:35` — `src.services.telegram_update_jobs: TelegramUpdateJobConfigurationError, TelegramUpdateRunnerConfigurationError, TelegramUpdateRunnerResult, TelegramUpdateRunnerSummary, TelegramUpdateWorkerConfig, load_telegram_update_keyring_from_env, run_telegram_update_worker`
- `src/channels/telegram_update_worker.py:535` — `src.services.telegram_conversation_state: create_postgres_telegram_webhook_conversation_bridge`
- `src/services/telegram_update_jobs/repository.py:7` — `src.database.connection: cursor_postgres`
- `src/services/telegram_update_receipts/repository.py:8` — `src.database.connection: cursor_postgres`

## Leituras de ambiente

- Nenhuma leitura direta encontrada.

## Candidatos seguros para wiring

- `src/channels/telegram_update_worker.py:569` — `load_telegram_processor` chama `metrics_factory`
- `src/channels/telegram_update_worker.py:570` — `load_telegram_processor` chama `event_sink_factory`
- `src/channels/telegram_update_worker.py:589` — `load_telegram_processor` chama `_observable_bridge_factory_kwargs`
- `src/channels/telegram_update_worker.py:1434` — `_load_productive_telegram_processor` chama `create_production_telegram_metrics_runtime`
- `src/channels/telegram_update_worker.py:1486` — `_load_productive_telegram_processor` chama `load_telegram_processor`
- `src/channels/telegram_update_worker.py:1536` — `main` chama `load_worker_config_from_env`
- `src/channels/telegram_update_worker.py:1544` — `main` chama `create_production_telegram_metrics_runtime`
- `src/channels/telegram_update_worker.py:1548` — `main` chama `_load_productive_telegram_processor`
- `src/services/telegram_update_jobs/repository.py:670` — `enqueue_telegram_update_job` chama `cursor_postgres`
- `src/services/telegram_update_jobs/repository.py:757` — `claim_next_telegram_update_job` chama `cursor_postgres`
- `src/services/telegram_update_jobs/repository.py:822` — `renew_telegram_update_job_lease` chama `cursor_postgres`
- `src/services/telegram_update_jobs/repository.py:886` — `complete_telegram_update_job` chama `cursor_postgres`
- `src/services/telegram_update_jobs/repository.py:960` — `retry_or_dead_letter_telegram_update_job` chama `cursor_postgres`
- `src/services/telegram_update_jobs/repository.py:1027` — `recover_expired_telegram_update_jobs` chama `cursor_postgres`
- `src/services/telegram_update_jobs/service.py:547` — `encrypt_authenticated_telegram_update` chama `resolved_keyring.get_key`
- `src/services/telegram_update_jobs/service.py:644` — `decrypt_authenticated_telegram_update` chama `resolved_keyring.get_key`
- `src/services/telegram_update_receipts/repository.py:510` — `claim_telegram_update` chama `cursor_postgres`
- `src/services/telegram_update_receipts/repository.py:691` — `complete_telegram_update` chama `cursor_postgres`
- `src/services/telegram_update_receipts/repository.py:770` — `fail_telegram_update` chama `cursor_postgres`

## Operações que não podem ser chamadas pelo readiness

- `src/channels/telegram_update_worker.py:89` — `_configuration_error` chama `TelegramUpdateRunnerConfigurationError`
- `src/channels/telegram_update_worker.py:182` — `load_worker_config_from_env` chama `TelegramUpdateWorkerConfig`
- `src/channels/telegram_update_worker.py:186` — `load_worker_config_from_env` chama `TelegramUpdateWorkerConfig`
- `src/channels/telegram_update_worker.py:348` — `_resolve_telegram_operational_log_level` chama `TelegramUpdateRunnerConfigurationError`
- `src/channels/telegram_update_worker.py:420` — `create_production_telegram_event_sink` chama `TelegramUpdateRunnerConfigurationError`
- `src/channels/telegram_update_worker.py:542` — `load_telegram_processor` chama `TelegramUpdateRunnerConfigurationError`
- `src/channels/telegram_update_worker.py:549` — `load_telegram_processor` chama `TelegramUpdateRunnerConfigurationError`
- `src/channels/telegram_update_worker.py:554` — `load_telegram_processor` chama `TelegramUpdateRunnerConfigurationError`
- `src/channels/telegram_update_worker.py:559` — `load_telegram_processor` chama `TelegramUpdateRunnerConfigurationError`
- `src/channels/telegram_update_worker.py:564` — `load_telegram_processor` chama `TelegramUpdateRunnerConfigurationError`
- `src/channels/telegram_update_worker.py:604` — `load_telegram_processor` chama `TelegramUpdateRunnerConfigurationError`
- `src/channels/telegram_update_worker.py:610` — `load_telegram_processor` chama `TelegramUpdateRunnerConfigurationError`
- `src/channels/telegram_update_worker.py:617` — `process_with_durable_conversation_state` chama `process_telegram_update`
- `src/channels/telegram_update_worker.py:1181` — `record_productive_runner_result` chama `_productive_update_outcome_for_runner_result`
- `src/channels/telegram_update_worker.py:1193` — `record_productive_runner_result` chama `operations.record_worker_update`
- `src/channels/telegram_update_worker.py:1292` — `_install_signal_handlers` chama `TelegramUpdateRunnerConfigurationError`
- `src/channels/telegram_update_worker.py:1540` — `main` chama `load_telegram_update_keyring_from_env`
- `src/channels/telegram_update_worker.py:1607` — `main` chama `run_telegram_update_worker`
- `src/services/telegram_update_jobs/repository.py:378` — `_validate_integer` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/repository.py:406` — `_validate_sha256` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/repository.py:421` — `_validate_key_id` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/repository.py:436` — `_validate_error_code` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/repository.py:458` — `_validate_bytes` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/repository.py:469` — `_validate_bytes` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/repository.py:512` — `_record_from_row` chama `TelegramUpdateJobRecord`
- `src/services/telegram_update_jobs/repository.py:527` — `_record_from_row` chama `TelegramUpdateJobRepositoryError`
- `src/services/telegram_update_jobs/repository.py:537` — `_lease_from_row` chama `TelegramUpdateJobLease`
- `src/services/telegram_update_jobs/repository.py:604` — `_lease_from_row` chama `TelegramUpdateJobRepositoryError`
- `src/services/telegram_update_jobs/repository.py:631` — `enqueue_telegram_update_job` chama `_validate_update_id`
- `src/services/telegram_update_jobs/repository.py:717` — `enqueue_telegram_update_job` chama `TelegramUpdateJobRepositoryError`
- `src/services/telegram_update_jobs/repository.py:733` — `enqueue_telegram_update_job` chama `TelegramUpdateJobRepositoryError`
- `src/services/telegram_update_jobs/repository.py:793` — `claim_next_telegram_update_job` chama `TelegramUpdateJobRepositoryError`
- `src/services/telegram_update_jobs/repository.py:805` — `renew_telegram_update_job_lease` chama `_validate_update_id`
- `src/services/telegram_update_jobs/repository.py:848` — `renew_telegram_update_job_lease` chama `TelegramUpdateJobOwnershipError`
- `src/services/telegram_update_jobs/repository.py:865` — `renew_telegram_update_job_lease` chama `TelegramUpdateJobRepositoryError`
- `src/services/telegram_update_jobs/repository.py:876` — `complete_telegram_update_job` chama `_validate_update_id`
- `src/services/telegram_update_jobs/repository.py:909` — `complete_telegram_update_job` chama `TelegramUpdateJobOwnershipError`
- `src/services/telegram_update_jobs/repository.py:926` — `complete_telegram_update_job` chama `TelegramUpdateJobRepositoryError`
- `src/services/telegram_update_jobs/repository.py:939` — `retry_or_dead_letter_telegram_update_job` chama `_validate_update_id`
- `src/services/telegram_update_jobs/repository.py:989` — `retry_or_dead_letter_telegram_update_job` chama `TelegramUpdateJobOwnershipError`
- `src/services/telegram_update_jobs/repository.py:1006` — `retry_or_dead_letter_telegram_update_job` chama `TelegramUpdateJobRepositoryError`
- `src/services/telegram_update_jobs/repository.py:1058` — `recover_expired_telegram_update_jobs` chama `TelegramUpdateJobRepositoryError`
- `src/services/telegram_update_jobs/service.py:104` — `_validate_key_id` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/service.py:120` — `_validate_update_id` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/service.py:140` — `_validate_integer` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/service.py:162` — `_validate_bytes` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/service.py:173` — `_validate_bytes` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/service.py:198` — `_decode_base64url_key` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:220` — `_decode_base64url_key` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:230` — `_decode_base64url_key` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:258` — `__post_init__` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:266` — `__post_init__` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:286` — `__post_init__` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:295` — `__post_init__` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:326` — `get_key` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:378` — `load_telegram_update_keyring_from_env` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:383` — `load_telegram_update_keyring_from_env` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:396` — `load_telegram_update_keyring_from_env` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:404` — `load_telegram_update_keyring_from_env` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:420` — `load_telegram_update_keyring_from_env` chama `TelegramUpdateJobConfigurationError`
- `src/services/telegram_update_jobs/service.py:430` — `load_telegram_update_keyring_from_env` chama `TelegramUpdateEncryptionKeyring`
- `src/services/telegram_update_jobs/service.py:446` — `canonicalize_telegram_update` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/service.py:450` — `canonicalize_telegram_update` chama `_validate_update_id`
- `src/services/telegram_update_jobs/service.py:451` — `canonicalize_telegram_update` chama `update.get`
- `src/services/telegram_update_jobs/service.py:475` — `canonicalize_telegram_update` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/service.py:484` — `canonicalize_telegram_update` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_jobs/service.py:500` — `_build_authenticated_data` chama `_validate_update_id`
- `src/services/telegram_update_jobs/service.py:534` — `encrypt_authenticated_telegram_update` chama `load_telegram_update_keyring_from_env`
- `src/services/telegram_update_jobs/service.py:538` — `encrypt_authenticated_telegram_update` chama `canonicalize_telegram_update`
- `src/services/telegram_update_jobs/service.py:573` — `encrypt_authenticated_telegram_update` chama `TelegramUpdateJobEncryptionError`
- `src/services/telegram_update_jobs/service.py:579` — `encrypt_authenticated_telegram_update` chama `TelegramUpdateJobEncryptionError`
- `src/services/telegram_update_jobs/service.py:584` — `encrypt_authenticated_telegram_update` chama `EncryptedTelegramUpdatePayload`
- `src/services/telegram_update_jobs/service.py:603` — `decrypt_authenticated_telegram_update` chama `_validate_update_id`
- `src/services/telegram_update_jobs/service.py:633` — `decrypt_authenticated_telegram_update` chama `TelegramUpdateJobDecryptionError`
- `src/services/telegram_update_jobs/service.py:640` — `decrypt_authenticated_telegram_update` chama `load_telegram_update_keyring_from_env`
- `src/services/telegram_update_jobs/service.py:649` — `decrypt_authenticated_telegram_update` chama `TelegramUpdateJobDecryptionError`
- `src/services/telegram_update_jobs/service.py:671` — `decrypt_authenticated_telegram_update` chama `TelegramUpdateJobDecryptionError`
- `src/services/telegram_update_jobs/service.py:676` — `decrypt_authenticated_telegram_update` chama `TelegramUpdateJobDecryptionError`
- `src/services/telegram_update_jobs/service.py:693` — `decrypt_authenticated_telegram_update` chama `TelegramUpdateJobDecryptionError`
- `src/services/telegram_update_jobs/service.py:701` — `decrypt_authenticated_telegram_update` chama `TelegramUpdateJobDecryptionError`
- `src/services/telegram_update_jobs/service.py:705` — `decrypt_authenticated_telegram_update` chama `update.get`
- `src/services/telegram_update_jobs/service.py:710` — `decrypt_authenticated_telegram_update` chama `TelegramUpdateJobDecryptionError`
- `src/services/telegram_update_jobs/service.py:726` — `generate_telegram_update_job_lock_token` chama `TelegramUpdateJobServiceError`
- `src/services/telegram_update_jobs/service.py:765` — `calculate_telegram_update_retry_delay` chama `TelegramUpdateJobValidationError`
- `src/services/telegram_update_receipts/repository.py:323` — `_validar_attempt_count` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:334` — `_extrair_update_id` chama `_validar_update_id`
- `src/services/telegram_update_receipts/repository.py:343` — `_extrair_update_id` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:358` — `_extrair_status_banco` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:367` — `_extrair_status_banco` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:396` — `_resultado_claim` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:400` — `_resultado_claim` chama `TelegramUpdateClaimResult`
- `src/services/telegram_update_receipts/repository.py:401` — `_resultado_claim` chama `_extrair_update_id`
- `src/services/telegram_update_receipts/repository.py:425` — `_resultado_lifecycle` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:440` — `_resultado_lifecycle` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:444` — `_resultado_lifecycle` chama `TelegramUpdateLifecycleResult`
- `src/services/telegram_update_receipts/repository.py:445` — `_resultado_lifecycle` chama `_extrair_update_id`
- `src/services/telegram_update_receipts/repository.py:467` — `claim_telegram_update` chama `_validar_update_id`
- `src/services/telegram_update_receipts/repository.py:532` — `claim_telegram_update` chama `_resultado_claim`
- `src/services/telegram_update_receipts/repository.py:553` — `claim_telegram_update` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:571` — `claim_telegram_update` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:582` — `claim_telegram_update` chama `TelegramUpdateFingerprintConflictError`
- `src/services/telegram_update_receipts/repository.py:604` — `claim_telegram_update` chama `_resultado_claim`
- `src/services/telegram_update_receipts/repository.py:630` — `claim_telegram_update` chama `_resultado_claim`
- `src/services/telegram_update_receipts/repository.py:645` — `claim_telegram_update` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:651` — `claim_telegram_update` chama `_resultado_claim`
- `src/services/telegram_update_receipts/repository.py:666` — `claim_telegram_update` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:678` — `complete_telegram_update` chama `_validar_update_id`
- `src/services/telegram_update_receipts/repository.py:721` — `complete_telegram_update` chama `TelegramUpdateClaimOwnershipError`
- `src/services/telegram_update_receipts/repository.py:738` — `complete_telegram_update` chama `TelegramUpdateReceiptRepositoryError`
- `src/services/telegram_update_receipts/repository.py:751` — `fail_telegram_update` chama `_validar_update_id`
- `src/services/telegram_update_receipts/repository.py:803` — `fail_telegram_update` chama `TelegramUpdateClaimOwnershipError`
- `src/services/telegram_update_receipts/repository.py:820` — `fail_telegram_update` chama `TelegramUpdateReceiptRepositoryError`
