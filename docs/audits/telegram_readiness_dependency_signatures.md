# F2H5-H2B — Assinaturas das dependências de readiness

## Objetos resolvidos

### `src.channels.telegram_update_worker._observable_bridge_factory_kwargs`

- Arquivo: `src/channels/telegram_update_worker.py:247`
- Assinatura: `(bridge_factory: 'Callable[..., Any]', *, metrics: 'TelegramConversationMetrics', event_sink: 'TelegramOperationalEventSink', clock: 'Callable[[], float]') -> 'dict[str, object]'`

### `src.channels.telegram_update_worker.load_telegram_processor`

- Arquivo: `src/channels/telegram_update_worker.py:508`
- Assinatura: `(*, metrics_factory: 'Callable[[], TelegramConversationMetrics]' = <class 'src.services.telegram_observability.metrics.NoOpTelegramConversationMetrics'>, event_sink_factory: 'Callable[[], TelegramOperationalEventSink]' = <class 'src.services.telegram_observability.events.NoOpTelegramOperationalEventSink'>, clock: 'Callable[[], float]' = <built-in function perf_counter>)`

### `src.channels.telegram_update_worker._productive_receipt_for_runner_result`

- Arquivo: `src/channels/telegram_update_worker.py:858`
- Assinatura: `(result: 'TelegramUpdateRunnerResult') -> 'tuple[str, str, str | None] | None'`

### `src.channels.telegram_update_worker._productive_queue_for_runner_result`

- Arquivo: `src/channels/telegram_update_worker.py:966`
- Assinatura: `(result: 'TelegramUpdateRunnerResult') -> 'tuple[str, str, str | None] | None'`

### `src.channels.telegram_update_worker.record_productive_receipt_and_queue_result`

- Arquivo: `src/channels/telegram_update_worker.py:1115`
- Assinatura: `(result: 'TelegramUpdateRunnerResult', *, operations) -> 'None'`

### `src.channels.telegram_update_worker._load_productive_telegram_processor`

- Arquivo: `src/channels/telegram_update_worker.py:1417`
- Assinatura: `(*, stderr: 'TextIO', metrics_runtime: 'TelegramProductiveMetricsRuntime | None' = None)`

### `src.services.telegram_observability.health_readiness.create_process_health_service`

- Arquivo: `src/services/telegram_observability/health_readiness.py:627`
- Assinatura: `(*, clock_check: 'Callable[[], bool]' = <function <lambda> at 0x0000020F11B04720>) -> 'TelegramOperationalStatusService'`

### `src.services.telegram_update_jobs.execution.TelegramUpdateExecutionDecryptionError`

- Arquivo: `src/services/telegram_update_jobs/execution.py:56`
- Assinatura: `None`

### `src.services.telegram_update_jobs.execution.decrypt_authenticated_telegram_worker_lease`

- Arquivo: `src/services/telegram_update_jobs/execution.py:486`
- Assinatura: `(lease: 'worker_module.TelegramUpdateWorkerLease', *, keyring: 'crypto_service.TelegramUpdateEncryptionKeyring | None' = None) -> 'TelegramUpdateWorkerPayload'`

### `src.services.telegram_update_jobs.ingress._ReceiptSnapshot`

- Arquivo: `src/services/telegram_update_jobs/ingress.py:167`
- Assinatura: `(update_id: 'int', status: 'str', attempt_count: 'int', update_fingerprint: 'str | None' = None, lease_active: 'bool' = False) -> None`

### `src.services.telegram_update_jobs.ingress._JobSnapshot`

- Arquivo: `src/services/telegram_update_jobs/ingress.py:180`
- Assinatura: `(update_id: 'int', status: 'JobState', attempt_count: 'int', max_attempts: 'int', payload_version: 'int') -> None`

### `src.services.telegram_update_jobs.ingress._set_transaction_timeouts`

- Arquivo: `src/services/telegram_update_jobs/ingress.py:244`
- Assinatura: `(cursor: 'Any') -> 'None'`

### `src.services.telegram_update_jobs.ingress._receipt_snapshot_from_row`

- Arquivo: `src/services/telegram_update_jobs/ingress.py:256`
- Assinatura: `(row: 'Any') -> '_ReceiptSnapshot'`

### `src.services.telegram_update_jobs.ingress._job_snapshot_from_row`

- Arquivo: `src/services/telegram_update_jobs/ingress.py:340`
- Assinatura: `(row: 'Any') -> '_JobSnapshot'`

### `src.services.telegram_update_jobs.ingress._select_existing_job`

- Arquivo: `src/services/telegram_update_jobs/ingress.py:405`
- Assinatura: `(cursor: 'Any', *, update_id: 'int') -> '_JobSnapshot | None'`

### `src.services.telegram_update_jobs.ingress._ensure_encrypted_job`

- Arquivo: `src/services/telegram_update_jobs/ingress.py:470`
- Assinatura: `(cursor: 'Any', *, update: 'dict[str, Any]', update_id: 'int', receipt_state: 'ReceiptState', receipt_attempt_count: 'int', max_attempts: 'int', keyring: 'crypto_service.TelegramUpdateEncryptionKeyring | None') -> 'TelegramUpdateIngressOutcome'`

### `src.services.telegram_update_jobs.ingress.enqueue_authenticated_telegram_update_atomic`

- Arquivo: `src/services/telegram_update_jobs/ingress.py:581`
- Assinatura: `(update: 'Mapping[str, Any]', *, receipt_lease_seconds: 'int' = 120, max_attempts: 'int' = 5, keyring: 'crypto_service.TelegramUpdateEncryptionKeyring | None' = None) -> 'TelegramUpdateIngressOutcome'`

### `src.services.telegram_update_jobs.repository.TelegramUpdateJobRepositoryError`

- Arquivo: `src/services/telegram_update_jobs/repository.py:280`
- Assinatura: `None`

### `src.services.telegram_update_jobs.repository.TelegramUpdateJobOwnershipError`

- Arquivo: `src/services/telegram_update_jobs/repository.py:288`
- Assinatura: `None`

### `src.services.telegram_update_jobs.repository.TelegramUpdateJobValidationError`

- Arquivo: `src/services/telegram_update_jobs/repository.py:296`
- Assinatura: `None`

### `src.services.telegram_update_jobs.repository.TelegramUpdateJobRecord`

- Arquivo: `src/services/telegram_update_jobs/repository.py:308`
- Assinatura: `(update_id: 'int', status: 'str', attempt_count: 'int', max_attempts: 'int', payload_version: 'int') -> None`

Métodos públicos:

- `to_safe_dict(self) -> 'dict[str, int | str]'`

### `src.services.telegram_update_jobs.repository.TelegramUpdateJobLease`

- Arquivo: `src/services/telegram_update_jobs/repository.py:331`
- Assinatura: `(update_id: 'int', attempt_count: 'int', max_attempts: 'int', payload_version: 'int', payload_ciphertext: 'bytes', payload_nonce: 'bytes', payload_key_id: 'str', lock_token: 'str') -> None`

Métodos públicos:

- `to_safe_dict(self) -> 'dict[str, int | str]'`

### `src.services.telegram_update_jobs.repository.enqueue_telegram_update_job`

- Arquivo: `src/services/telegram_update_jobs/repository.py:622`
- Assinatura: `(*, update_id: 'int', payload_ciphertext: 'bytes', payload_nonce: 'bytes', payload_key_id: 'str', payload_version: 'int' = 1, max_attempts: 'int' = 5) -> 'TelegramUpdateJobRecord'`

### `src.services.telegram_update_jobs.repository.claim_next_telegram_update_job`

- Arquivo: `src/services/telegram_update_jobs/repository.py:739`
- Assinatura: `(*, lock_token: 'str', lease_seconds: 'int' = 120) -> 'TelegramUpdateJobLease | None'`

### `src.services.telegram_update_jobs.repository.renew_telegram_update_job_lease`

- Arquivo: `src/services/telegram_update_jobs/repository.py:799`
- Assinatura: `(*, update_id: 'int', lock_token: 'str', lease_seconds: 'int' = 120) -> 'TelegramUpdateJobRecord'`

### `src.services.telegram_update_jobs.repository.complete_telegram_update_job`

- Arquivo: `src/services/telegram_update_jobs/repository.py:871`
- Assinatura: `(*, update_id: 'int', lock_token: 'str') -> 'TelegramUpdateJobRecord'`

### `src.services.telegram_update_jobs.repository.retry_or_dead_letter_telegram_update_job`

- Arquivo: `src/services/telegram_update_jobs/repository.py:932`
- Assinatura: `(*, update_id: 'int', lock_token: 'str', error_code: 'str', retry_delay_seconds: 'int') -> 'TelegramUpdateJobRecord'`

### `src.services.telegram_update_jobs.repository.recover_expired_telegram_update_jobs`

- Arquivo: `src/services/telegram_update_jobs/repository.py:1012`
- Assinatura: `(*, limit: 'int' = 100) -> 'tuple[TelegramUpdateJobRecord, ...]'`

### `src.services.telegram_update_jobs.runner.TelegramUpdateProcessorError`

- Arquivo: `src/services/telegram_update_jobs/runner.py:59`
- Assinatura: `(error_code: 'str') -> 'None'`

### `src.services.telegram_update_jobs.runner.run_one_telegram_update_job`

- Arquivo: `src/services/telegram_update_jobs/runner.py:640`
- Assinatura: `(processor: 'Callable[[dict[str, Any]], Any]', *, config: 'TelegramUpdateWorkerConfig | None' = None, dependencies: 'TelegramUpdateWorkerDependencies | None' = None, keyring: 'Any' = None) -> 'TelegramUpdateRunnerResult'`

### `src.services.telegram_update_jobs.service.TelegramUpdateJobServiceError`

- Arquivo: `src/services/telegram_update_jobs/service.py:56`
- Assinatura: `None`

### `src.services.telegram_update_jobs.service.TelegramUpdateJobValidationError`

- Arquivo: `src/services/telegram_update_jobs/service.py:64`
- Assinatura: `None`

### `src.services.telegram_update_jobs.service.TelegramUpdateJobConfigurationError`

- Arquivo: `src/services/telegram_update_jobs/service.py:72`
- Assinatura: `None`

### `src.services.telegram_update_jobs.service.TelegramUpdateJobEncryptionError`

- Arquivo: `src/services/telegram_update_jobs/service.py:80`
- Assinatura: `None`

### `src.services.telegram_update_jobs.service.TelegramUpdateJobDecryptionError`

- Arquivo: `src/services/telegram_update_jobs/service.py:88`
- Assinatura: `None`

### `src.services.telegram_update_jobs.service.TelegramUpdateEncryptionKeyring`

- Arquivo: `src/services/telegram_update_jobs/service.py:239`
- Assinatura: `(active_key_id: 'str', keys: 'Mapping[str, bytes]') -> None`

Métodos públicos:

- `get_key(self, key_id: 'str') -> 'bytes'`

### `src.services.telegram_update_jobs.service.EncryptedTelegramUpdatePayload`

- Arquivo: `src/services/telegram_update_jobs/service.py:337`
- Assinatura: `(update_id: 'int', payload_key_id: 'str', payload_version: 'int', payload_ciphertext: 'bytes', payload_nonce: 'bytes') -> None`

Métodos públicos:

- `to_safe_dict(self) -> 'dict[str, int | str]'`

### `src.services.telegram_update_jobs.service.load_telegram_update_keyring_from_env`

- Arquivo: `src/services/telegram_update_jobs/service.py:365`
- Assinatura: `() -> 'TelegramUpdateEncryptionKeyring'`

### `src.services.telegram_update_jobs.service.encrypt_authenticated_telegram_update`

- Arquivo: `src/services/telegram_update_jobs/service.py:525`
- Assinatura: `(update: 'Any', *, keyring: 'TelegramUpdateEncryptionKeyring | None' = None) -> 'EncryptedTelegramUpdatePayload'`

### `src.services.telegram_update_jobs.service.decrypt_authenticated_telegram_update`

- Arquivo: `src/services/telegram_update_jobs/service.py:593`
- Assinatura: `(*, update_id: 'int', payload_ciphertext: 'bytes', payload_nonce: 'bytes', payload_key_id: 'str', payload_version: 'int', keyring: 'TelegramUpdateEncryptionKeyring | None' = None) -> 'dict[str, Any]'`

### `src.services.telegram_update_jobs.service.generate_telegram_update_job_lock_token`

- Arquivo: `src/services/telegram_update_jobs/service.py:717`
- Assinatura: `() -> 'str'`

### `src.services.telegram_update_jobs.worker._ReceiptCandidate`

- Arquivo: `src/services/telegram_update_jobs/worker.py:174`
- Assinatura: `(update_id: 'int', receipt_status: 'str', receipt_attempt_count: 'int') -> None`

### `src.services.telegram_update_jobs.worker._set_transaction_timeouts`

- Arquivo: `src/services/telegram_update_jobs/worker.py:325`
- Assinatura: `(cursor: 'Any') -> 'None'`

### `src.services.telegram_update_jobs.worker.claim_next_authenticated_telegram_update_job_atomic`

- Arquivo: `src/services/telegram_update_jobs/worker.py:538`
- Assinatura: `(*, lease_seconds: 'int' = 120) -> 'TelegramUpdateWorkerLease | None'`

### `src.services.telegram_update_jobs.worker._OwnedReceiptCompletionSnapshot`

- Arquivo: `src/services/telegram_update_jobs/worker.py:919`
- Assinatura: `(update_id: 'int', status: 'str', attempt_count: 'int', claim_token: 'str', lease_active: 'bool' = False) -> None`

### `src.services.telegram_update_jobs.worker._CompletedJobSnapshot`

- Arquivo: `src/services/telegram_update_jobs/worker.py:935`
- Assinatura: `(update_id: 'int', status: 'str', attempt_count: 'int', max_attempts: 'int', payload_version: 'int', payload_cleared: 'bool', ownership_cleared: 'bool', completed_at_set: 'bool') -> None`

### `src.services.telegram_update_jobs.worker._CompletedReceiptSnapshot`

- Arquivo: `src/services/telegram_update_jobs/worker.py:952`
- Assinatura: `(update_id: 'int', status: 'str', attempt_count: 'int', completed_at_set: 'bool', lease_closed: 'bool') -> None`

### `src.services.telegram_update_jobs.worker._owned_receipt_completion_from_row`

- Arquivo: `src/services/telegram_update_jobs/worker.py:1067`
- Assinatura: `(row: 'Any') -> '_OwnedReceiptCompletionSnapshot'`

### `src.services.telegram_update_jobs.worker._completed_job_from_row`

- Arquivo: `src/services/telegram_update_jobs/worker.py:1126`
- Assinatura: `(row: 'Any') -> '_CompletedJobSnapshot'`

### `src.services.telegram_update_jobs.worker._completed_receipt_from_row`

- Arquivo: `src/services/telegram_update_jobs/worker.py:1187`
- Assinatura: `(row: 'Any') -> '_CompletedReceiptSnapshot'`

### `src.services.telegram_update_jobs.worker._validate_completed_job_matches_lease`

- Arquivo: `src/services/telegram_update_jobs/worker.py:1237`
- Assinatura: `(*, lease: 'TelegramUpdateWorkerLease', job: '_CompletedJobSnapshot') -> 'None'`

### `src.services.telegram_update_jobs.worker.complete_authenticated_telegram_update_job_atomic`

- Arquivo: `src/services/telegram_update_jobs/worker.py:1336`
- Assinatura: `(lease: 'TelegramUpdateWorkerLease') -> 'TelegramUpdateWorkerCompletionOutcome'`

### `src.services.telegram_update_jobs.worker._FailureReceiptSnapshot`

- Arquivo: `src/services/telegram_update_jobs/worker.py:1764`
- Assinatura: `(update_id: 'int', status: 'str', attempt_count: 'int', last_error_code: 'str | None', claim_token: 'str', lease_active: 'bool' = False) -> None`

### `src.services.telegram_update_jobs.worker._FailedJobSnapshot`

- Arquivo: `src/services/telegram_update_jobs/worker.py:1782`
- Assinatura: `(update_id: 'int', status: "Literal['queued', 'dead_letter']", attempt_count: 'int', max_attempts: 'int', payload_version: 'int', last_error_code: 'str', payload_retained: 'bool', ownership_cleared: 'bool', completed_at_cleared: 'bool', retry_state_valid: 'bool', dead_letter_state_valid: 'bool') -> None`

### `src.services.telegram_update_jobs.worker._FailedReceiptResult`

- Arquivo: `src/services/telegram_update_jobs/worker.py:1807`
- Assinatura: `(update_id: 'int', status: "Literal['failed',]", attempt_count: 'int', last_error_code: 'str', completed_at_cleared: 'bool', failed_at_set: 'bool', lease_closed: 'bool') -> None`

### `src.services.telegram_update_jobs.worker._failure_receipt_from_row`

- Arquivo: `src/services/telegram_update_jobs/worker.py:1969`
- Assinatura: `(row: 'Any') -> '_FailureReceiptSnapshot'`

### `src.services.telegram_update_jobs.worker._failed_job_from_row`

- Arquivo: `src/services/telegram_update_jobs/worker.py:2053`
- Assinatura: `(row: 'Any') -> '_FailedJobSnapshot'`

### `src.services.telegram_update_jobs.worker._failed_receipt_result_from_row`

- Arquivo: `src/services/telegram_update_jobs/worker.py:2159`
- Assinatura: `(row: 'Any') -> '_FailedReceiptResult'`

### `src.services.telegram_update_jobs.worker._validate_failed_job_matches_lease`

- Arquivo: `src/services/telegram_update_jobs/worker.py:2217`
- Assinatura: `(*, lease: 'TelegramUpdateWorkerLease', job: '_FailedJobSnapshot', error_code: 'str') -> 'None'`

### `src.services.telegram_update_jobs.worker.retry_or_dead_letter_authenticated_telegram_update_job_atomic`

- Arquivo: `src/services/telegram_update_jobs/worker.py:2313`
- Assinatura: `(lease: 'TelegramUpdateWorkerLease', *, error_code: 'str', retry_delay_seconds: 'int', force_dead_letter: 'bool' = False) -> 'TelegramUpdateWorkerFailureOutcome'`

### `src.services.telegram_update_jobs.worker.recover_expired_authenticated_telegram_update_jobs_atomic`

- Arquivo: `src/services/telegram_update_jobs/worker.py:3077`
- Assinatura: `(*, limit: 'int' = 100) -> 'TelegramUpdateWorkerRecoveryBatch'`

### `src.services.telegram_update_receipts.repository.TelegramUpdateReceiptRepositoryError`

- Arquivo: `src/services/telegram_update_receipts/repository.py:156`
- Assinatura: `None`

### `src.services.telegram_update_receipts.service.TelegramUpdateReceiptServiceError`

- Arquivo: `src/services/telegram_update_receipts/service.py:26`
- Assinatura: `None`

### `src.services.telegram_update_receipts.service.TelegramUpdateReceiptValidationError`

- Arquivo: `src/services/telegram_update_receipts/service.py:34`
- Assinatura: `None`

### `src.services.telegram_update_receipts.service.TelegramUpdateReceiptConflictError`

- Arquivo: `src/services/telegram_update_receipts/service.py:42`
- Assinatura: `None`

### `src.services.telegram_update_receipts.service.TelegramUpdateReceiptUnavailableError`

- Arquivo: `src/services/telegram_update_receipts/service.py:51`
- Assinatura: `None`

### `src.services.telegram_update_receipts.service.TelegramUpdateReceiptOwnershipError`

- Arquivo: `src/services/telegram_update_receipts/service.py:59`
- Assinatura: `None`

## Falhas de importação

- `src.services.telegram_observability.health_readiness.ready` — `AttributeError`
- `src.services.telegram_observability.productive_operations.record_receipt` — `AttributeError`
- `src.services.telegram_observability.productive_operations.record_queue_operation` — `AttributeError`
- `src.services.telegram_observability.productive_operations.record_receipt` — `AttributeError`
- `src.services.telegram_observability.productive_operations.record_queue_operation` — `AttributeError`
- `src.services.telegram_observability.productive_operations.record_receipt` — `AttributeError`
- `src.services.telegram_observability.productive_operations.record_queue_operation` — `AttributeError`
- `src.services.telegram_observability.productive_operations.record_receipt` — `AttributeError`
- `src.services.telegram_observability.productive_operations.record_queue_operation` — `AttributeError`
