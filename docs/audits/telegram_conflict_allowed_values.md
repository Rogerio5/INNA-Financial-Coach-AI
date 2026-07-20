# F2H5-E3 — Valores permitidos de observabilidade

## Resumo

- Constantes esperadas: 5
- Constantes encontradas: 5
- Constantes ausentes: 0
- Exports necessários: 5
- Exports ausentes: 0

## Valores permitidos

### `ALLOWED_ERROR_CATEGORIES`

- Linha: 44

- `frozenset({'configuration', 'validation', 'security', 'identity', 'persistence', 'external_service', 'optimistic_conflict', 'timeout', 'unavailable', 'unknown'})`

### `ALLOWED_EVENT_LEVELS`

- Linha: 59

- `frozenset({'debug', 'info', 'warning', 'error', 'critical'})`

### `ALLOWED_METRIC_COMPONENTS`

- Linha: 23

- `frozenset({'bridge', 'worker', 'webhook', 'receipt', 'repository'})`

### `ALLOWED_METRIC_OPERATIONS`

- Linha: 8

- `frozenset({'load_or_open_session', 'save_session', 'reload_session', 'delete_session', 'resolve_language', 'claim_update', 'process_update', 'complete_receipt', 'fail_receipt', 'rollback'})`

### `ALLOWED_OUTCOMES`

- Linha: 33

- `frozenset({'success', 'error', 'conflict', 'recovered', 'discarded', 'skipped'})`

## Exports necessários

- ✅ `TelegramConversationMetricRecord`
- ✅ `TelegramConversationMetrics`
- ✅ `TelegramOperationalEvent`
- ✅ `TelegramOperationalEventSink`
- ✅ `sanitize_event_fields`
