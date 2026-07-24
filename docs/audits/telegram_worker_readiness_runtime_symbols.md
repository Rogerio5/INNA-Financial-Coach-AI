# F2H5-H2E — Símbolos produtivos para wiring

## `src.channels.telegram_update_worker`

- `CompositeTelegramConversationMetrics(recorders: 'Iterable[TelegramConversationMetricsRecorder]') -> 'None'` — type; definido em `src.services.telegram_observability.productive_adapter`
- `EXIT_RUNTIME_ERROR` — int; definido em `None`
- `InMemoryTelegramProductiveMetrics(*, histogram_buckets: 'tuple[float, ...]' = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)) -> 'None'` — type; definido em `src.services.telegram_observability.productive_metrics`
- `NoOpTelegramConversationMetrics()` — type; definido em `src.services.telegram_observability.metrics`
- `ProductiveTelegramConversationMetricsAdapter(productive_metrics: 'TelegramProductiveMetricsSink') -> 'None'` — type; definido em `src.services.telegram_observability.productive_adapter`
- `SafeTelegramProductiveMetrics(delegate: 'TelegramProductiveMetricsSink') -> 'None'` — type; definido em `src.services.telegram_observability.productive_metrics`
- `TelegramConversationMetrics(*args, **kwargs)` — _ProtocolMeta; definido em `src.services.telegram_observability.contracts`
- `TelegramProductiveMetricsRuntime() -> 'None'` — type; definido em `src.channels.telegram_update_worker`
- `TelegramUpdateJobConfigurationError` — type; definido em `src.services.telegram_update_jobs.service`
- `_load_productive_telegram_processor(*, stderr: 'TextIO', metrics_runtime: 'TelegramProductiveMetricsRuntime | None' = None)` — function; definido em `src.channels.telegram_update_worker`
- `_productive_receipt_for_runner_result(result: 'TelegramUpdateRunnerResult') -> 'tuple[str, str, str | None] | None'` — function; definido em `src.channels.telegram_update_worker`
- `create_production_telegram_metrics_runtime() -> 'TelegramProductiveMetricsRuntime'` — function; definido em `src.channels.telegram_update_worker`
- `load_telegram_processor(*, metrics_factory: 'Callable[[], TelegramConversationMetrics]' = <class 'src.services.telegram_observability.metrics.NoOpTelegramConversationMetrics'>, event_sink_factory: 'Callable[[], TelegramOperationalEventSink]' = <class 'src.services.telegram_observability.events.NoOpTelegramOperationalEventSink'>, clock: 'Callable[[], float]' = <built-in function perf_counter>)` — function; definido em `src.channels.telegram_update_worker`
- `load_telegram_update_keyring_from_env() -> 'TelegramUpdateEncryptionKeyring'` — function; definido em `src.services.telegram_update_jobs.service`
- `load_worker_config_from_env(environment: 'Mapping[str, str] | None' = None) -> 'TelegramUpdateWorkerConfig'` — function; definido em `src.channels.telegram_update_worker`
- `record_productive_receipt_and_queue_result(result: 'TelegramUpdateRunnerResult', *, operations) -> 'None'` — function; definido em `src.channels.telegram_update_worker`

## `src.services.telegram_update_jobs.repository`

- `SQL_CLAIM_NEXT_JOB` — str; definido em `None`
- `SQL_COMPLETE_JOB` — str; definido em `None`
- `SQL_INSERT_JOB` — str; definido em `None`
- `SQL_RECOVER_EXPIRED_JOBS` — str; definido em `None`
- `SQL_RENEW_JOB_LEASE` — str; definido em `None`
- `SQL_RETRY_OR_DEAD_LETTER_JOB` — str; definido em `None`
- `SQL_SELECT_JOB` — str; definido em `None`
- `TelegramUpdateJobLease(update_id: 'int', attempt_count: 'int', max_attempts: 'int', payload_version: 'int', payload_ciphertext: 'bytes', payload_nonce: 'bytes', payload_key_id: 'str', lock_token: 'str') -> None` — type; definido em `src.services.telegram_update_jobs.repository`
- `TelegramUpdateJobOwnershipError` — type; definido em `src.services.telegram_update_jobs.repository`
- `TelegramUpdateJobRecord(update_id: 'int', status: 'str', attempt_count: 'int', max_attempts: 'int', payload_version: 'int') -> None` — type; definido em `src.services.telegram_update_jobs.repository`
- `TelegramUpdateJobRepositoryError` — type; definido em `src.services.telegram_update_jobs.repository`
- `TelegramUpdateJobValidationError` — type; definido em `src.services.telegram_update_jobs.repository`
- `claim_next_telegram_update_job(*, lock_token: 'str', lease_seconds: 'int' = 120) -> 'TelegramUpdateJobLease | None'` — function; definido em `src.services.telegram_update_jobs.repository`
- `complete_telegram_update_job(*, update_id: 'int', lock_token: 'str') -> 'TelegramUpdateJobRecord'` — function; definido em `src.services.telegram_update_jobs.repository`
- `cursor_postgres(*, dict_cursor: 'bool' = False, commit_automatico: 'bool' = True)` — function; definido em `src.database.connection`
- `enqueue_telegram_update_job(*, update_id: 'int', payload_ciphertext: 'bytes', payload_nonce: 'bytes', payload_key_id: 'str', payload_version: 'int' = 1, max_attempts: 'int' = 5) -> 'TelegramUpdateJobRecord'` — function; definido em `src.services.telegram_update_jobs.repository`
- `recover_expired_telegram_update_jobs(*, limit: 'int' = 100) -> 'tuple[TelegramUpdateJobRecord, ...]'` — function; definido em `src.services.telegram_update_jobs.repository`
- `renew_telegram_update_job_lease(*, update_id: 'int', lock_token: 'str', lease_seconds: 'int' = 120) -> 'TelegramUpdateJobRecord'` — function; definido em `src.services.telegram_update_jobs.repository`
- `retry_or_dead_letter_telegram_update_job(*, update_id: 'int', lock_token: 'str', error_code: 'str', retry_delay_seconds: 'int') -> 'TelegramUpdateJobRecord'` — function; definido em `src.services.telegram_update_jobs.repository`

## `src.services.telegram_update_jobs.service`

- `EncryptedTelegramUpdatePayload(update_id: 'int', payload_key_id: 'str', payload_version: 'int', payload_ciphertext: 'bytes', payload_nonce: 'bytes') -> None` — type; definido em `src.services.telegram_update_jobs.service`
- `PAYLOAD_VERSION` — int; definido em `None`
- `TelegramUpdateEncryptionKeyring(active_key_id: 'str', keys: 'Mapping[str, bytes]') -> None` — type; definido em `src.services.telegram_update_jobs.service`
- `TelegramUpdateJobConfigurationError` — type; definido em `src.services.telegram_update_jobs.service`
- `TelegramUpdateJobDecryptionError` — type; definido em `src.services.telegram_update_jobs.service`
- `TelegramUpdateJobEncryptionError` — type; definido em `src.services.telegram_update_jobs.service`
- `TelegramUpdateJobServiceError` — type; definido em `src.services.telegram_update_jobs.service`
- `TelegramUpdateJobValidationError` — type; definido em `src.services.telegram_update_jobs.service`
- `generate_telegram_update_job_lock_token() -> 'str'` — function; definido em `src.services.telegram_update_jobs.service`
- `load_telegram_update_keyring_from_env() -> 'TelegramUpdateEncryptionKeyring'` — function; definido em `src.services.telegram_update_jobs.service`

## `src.services.telegram_update_receipts.repository`

- `SQL_COMPLETE_RECEIPT` — str; definido em `None`
- `SQL_FAIL_RECEIPT` — str; definido em `None`
- `SQL_INSERT_RECEIPT` — str; definido em `None`
- `SQL_LOCK_EXISTING_RECEIPT` — str; definido em `None`
- `SQL_RECLAIM_RECEIPT` — str; definido em `None`
- `SQL_TOUCH_RECEIPT` — str; definido em `None`
- `TelegramUpdateReceiptRepositoryError` — type; definido em `src.services.telegram_update_receipts.repository`
- `cursor_postgres(*, dict_cursor: 'bool' = False, commit_automatico: 'bool' = True)` — function; definido em `src.database.connection`

## `src.services.telegram_observability.productive_metrics`

- `InMemoryTelegramProductiveMetrics(*, histogram_buckets: 'tuple[float, ...]' = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)) -> 'None'` — type; definido em `src.services.telegram_observability.productive_metrics`
- `NoOpTelegramProductiveMetrics()` — type; definido em `src.services.telegram_observability.productive_metrics`
- `SafeTelegramProductiveMetrics(delegate: 'TelegramProductiveMetricsSink') -> 'None'` — type; definido em `src.services.telegram_observability.productive_metrics`
- `TelegramConversationMetricRecord(operation: 'str', component: 'str', outcome: 'str', duration_ms: 'float', error_category: 'str | None' = None, conflict_recovered: 'bool | None' = None) -> None` — type; definido em `src.services.telegram_observability.contracts`
- `TelegramProductiveMetricsSink(*args, **kwargs)` — _ProtocolMeta; definido em `src.services.telegram_observability.productive_metrics`
- `TelegramProductiveMetricsSnapshot(counters: 'Mapping[str, Mapping[tuple[tuple[str, str], ...], float]]', histograms: 'Mapping[str, Mapping[tuple[tuple[str, str], ...], TelegramHistogramSnapshot]]') -> None` — type; definido em `src.services.telegram_observability.productive_metrics`
- `_METRIC_LABELS` — mappingproxy; definido em `None`
- `normalize_metric_labels(*, metric_name: 'str', labels: 'Mapping[str, object]') -> 'tuple[tuple[str, str], ...]'` — function; definido em `src.services.telegram_observability.productive_metrics`

## Falhas de importação

- Nenhuma.
