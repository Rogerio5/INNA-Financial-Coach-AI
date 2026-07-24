# F2H5-G2 — Contrato das métricas produtivas

## Resumo

- Versão: `1.0.0`
- Famílias de métricas: 8
- Labels permitidas: 7
- Labels proibidas: 30
- Erros de validação: 0

## Famílias

- `inna_telegram_operations_total` — counter
- `inna_telegram_operation_duration_seconds` — histogram
- `inna_telegram_conflicts_total` — counter
- `inna_telegram_receipts_total` — counter
- `inna_telegram_worker_cycles_total` — counter
- `inna_telegram_worker_updates_total` — counter
- `inna_telegram_queue_operations_total` — counter
- `inna_telegram_failures_total` — counter

## Controles

- ✅ Namespace estável
- ✅ Labels de vocabulário fechado
- ✅ Limite de cardinalidade
- ✅ Identificadores proibidos
- ✅ Texto livre proibido
- ✅ Dados financeiros proibidos
- ✅ Exceções classificadas
- ✅ Exporter fail-safe

