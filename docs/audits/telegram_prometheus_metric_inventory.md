# F2H5-I1 — Inventário Prometheus Telegram

## Métricas encontradas

- `EXIT_CONFIGURATION_ERROR`
- `EXIT_RUNTIME_ERROR`
- `TELEGRAM_OPERATION_DURATION_BUCKETS_SECONDS`
- `_count`
- `consistency_error`
- `duration_ms`
- `duration_ms deve ser finita.`
- `duration_ms não pode ser NaN.`
- `duration_ms não pode ser negativa.`
- `error_category`
- `error_category é obrigatória para outcomes error ou conflict.`
- `error_code`
- `inna_telegram_conflicts_total`
- `inna_telegram_failures_total`
- `inna_telegram_operation_duration_seconds`
- `inna_telegram_operations_total`
- `inna_telegram_operations_total{`
- `inna_telegram_queue_operations_total`
- `inna_telegram_receipts_total`
- `inna_telegram_worker_cycles_total`
- `inna_telegram_worker_updates_total`
- `inna_unknown_metric_total`
- `telegram_`
- `telegram_user_id`
- `telegram_worker_error`
- `telegram_worker_result`
- `telegram_worker_started`
- `telegram_worker_stopped`
- `telegram_worker_summary`

## Restrições para alertas

- Usar somente métricas presentes neste inventário.
- Não criar labels novas nas regras.
- Não utilizar identificadores de usuário.
- Não utilizar update_id, chat_id ou claim_token.
- Não utilizar labels de alta cardinalidade.
- Preservar os nomes e labels do exporter.
