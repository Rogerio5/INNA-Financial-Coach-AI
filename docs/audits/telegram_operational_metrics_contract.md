# F2H5-I1 — Contrato real de métricas Telegram

## Resumo

- Arquivos analisados: 4
- Constantes relevantes: 45
- Strings candidatas a métricas: 27
- Contratos de labels: 11
- Buckets de histogramas: 9
- Chamadas de registro: 13

## Strings candidatas a métricas

- `telegram_worker_result` — `src/channels/telegram_update_worker.py:672`
- `error_code` — `src/channels/telegram_update_worker.py:685`
- `consistency_error` — `src/channels/telegram_update_worker.py:783`
- `telegram_worker_summary` — `src/channels/telegram_update_worker.py:1242`
- `telegram_worker_error` — `src/channels/telegram_update_worker.py:1559`
- `telegram_worker_started` — `src/channels/telegram_update_worker.py:1599`
- `telegram_worker_stopped` — `src/channels/telegram_update_worker.py:1631`
- `EXIT_CONFIGURATION_ERROR` — `src/channels/telegram_update_worker.py:1693`
- `EXIT_RUNTIME_ERROR` — `src/channels/telegram_update_worker.py:1696`
- `duration_ms não pode ser negativa.` — `src/services/telegram_observability/contracts.py:93`
- `duration_ms não pode ser NaN.` — `src/services/telegram_observability/contracts.py:98`
- `duration_ms deve ser finita.` — `src/services/telegram_observability/contracts.py:106`
- `duration_ms` — `src/services/telegram_observability/contracts.py:157`
- `error_category` — `src/services/telegram_observability/contracts.py:166`
- `error_category é obrigatória para outcomes error ou conflict.` — `src/services/telegram_observability/contracts.py:183`
- `telegram_` — `src/services/telegram_observability/contracts.py:225`
- `telegram_user_id` — `src/services/telegram_observability/productive_metrics.py:127`
- `inna_telegram_operations_total` — `src/services/telegram_observability/productive_metrics.py:162`
- `inna_telegram_operation_duration_seconds` — `src/services/telegram_observability/productive_metrics.py:168`
- `inna_telegram_conflicts_total` — `src/services/telegram_observability/productive_metrics.py:173`
- `inna_telegram_receipts_total` — `src/services/telegram_observability/productive_metrics.py:177`
- `inna_telegram_worker_cycles_total` — `src/services/telegram_observability/productive_metrics.py:182`
- `inna_telegram_worker_updates_total` — `src/services/telegram_observability/productive_metrics.py:185`
- `inna_telegram_queue_operations_total` — `src/services/telegram_observability/productive_metrics.py:189`
- `inna_telegram_failures_total` — `src/services/telegram_observability/productive_metrics.py:194`
- `TELEGRAM_OPERATION_DURATION_BUCKETS_SECONDS` — `src/services/telegram_observability/productive_metrics.py:777`
- `_count` — `src/services/telegram_observability/prometheus_exporter.py:570`

## Contratos de labels

- `_ALLOWED_LABEL_VALUES` — `src/services/telegram_observability/productive_metrics.py:31` — `None`
- `_FORBIDDEN_LABEL_NAMES` — `src/services/telegram_observability/productive_metrics.py:124` — `None`
- `_METRIC_LABELS` — `src/services/telegram_observability/productive_metrics.py:160` — `None`
- `normalized_labels` — `src/services/telegram_observability/productive_metrics.py:475` — `None`
- `normalized_labels` — `src/services/telegram_observability/productive_metrics.py:518` — `None`
- `_LABEL_NAME_PATTERN` — `src/services/telegram_observability/prometheus_exporter.py:24` — `None`
- `label_name` — `src/services/telegram_observability/prometheus_exporter.py:200` — `None`
- `normalized_labels` — `src/services/telegram_observability/prometheus_exporter.py:268` — `None`
- `normalized_labels` — `src/services/telegram_observability/prometheus_exporter.py:475` — `None`
- `bucket_labels` — `src/services/telegram_observability/prometheus_exporter.py:517` — `None`
- `bucket_labels` — `src/services/telegram_observability/prometheus_exporter.py:539` — `None`

## Buckets de histogramas

- `TELEGRAM_OPERATION_DURATION_BUCKETS_SECONDS` — `src/services/telegram_observability/productive_metrics.py:15` — `(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)`
- `normalized_buckets` — `src/services/telegram_observability/productive_metrics.py:397` — `None`
- `self._histogram_buckets` — `src/services/telegram_observability/productive_metrics.py:427` — `None`
- `self._histogram_bucket_counts` — `src/services/telegram_observability/productive_metrics.py:443` — `None`
- `buckets` — `src/services/telegram_observability/productive_metrics.py:655` — `None`
- `raw_buckets` — `src/services/telegram_observability/prometheus_exporter.py:325` — `None`
- `buckets` — `src/services/telegram_observability/prometheus_exporter.py:500` — `None`
- `bucket_labels` — `src/services/telegram_observability/prometheus_exporter.py:517` — `None`
- `bucket_labels` — `src/services/telegram_observability/prometheus_exporter.py:539` — `None`

## Chamadas de registro

- `src/channels/telegram_update_worker.py:384` — `TelegramProductiveOperationsRecorder`
- `src/channels/telegram_update_worker.py:1133` — `operations.record_receipt`
- `src/channels/telegram_update_worker.py:1154` — `operations.record_queue_operation`
- `src/channels/telegram_update_worker.py:1176` — `operations.record_worker_cycle`
- `src/channels/telegram_update_worker.py:1193` — `operations.record_worker_update`
- `src/channels/telegram_update_worker.py:1220` — `record_productive_runner_result`
- `src/channels/telegram_update_worker.py:1228` — `record_productive_receipt_and_queue_result`
- `src/services/telegram_observability/productive_metrics.py:560` — `self.increment`
- `src/services/telegram_observability/productive_metrics.py:578` — `self.observe`
- `src/services/telegram_observability/productive_metrics.py:595` — `self.increment`
- `src/services/telegram_observability/productive_metrics.py:622` — `self.increment`
- `src/services/telegram_observability/productive_metrics.py:748` — `self._delegate.increment`
- `src/services/telegram_observability/productive_metrics.py:764` — `self._delegate.observe`
