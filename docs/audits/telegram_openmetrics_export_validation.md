# F2H5-J1 — Validação do exportador Prometheus/OpenMetrics

## Resultado

- `prometheus_content_type`: **APROVADO**
- `openmetrics_content_type`: **APROVADO**
- `prometheus_without_eof`: **APROVADO**
- `openmetrics_with_eof`: **APROVADO**
- `all_required_metrics_present`: **APROVADO**
- `deterministic_export`: **APROVADO**
- `no_update_id`: **APROVADO**
- `no_chat_id`: **APROVADO**
- `no_user_id`: **APROVADO**
- `no_claim_token`: **APROVADO**
- `no_payload`: **APROVADO**

## Formatos

- Prometheus: `text/plain; version=0.0.4; charset=utf-8`
- OpenMetrics: `application/openmetrics-text; version=1.0.0; charset=utf-8`

## Métricas verificadas

- `inna_telegram_queue_operations_total`
- `inna_telegram_receipts_total`
- `inna_telegram_worker_cycles_total`
- `inna_telegram_worker_updates_total`

## Privacidade

O relatório valida que identificadores, tokens e payloads não aparecem na saída.
