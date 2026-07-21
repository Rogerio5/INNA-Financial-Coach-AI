# F2H5-I3A.3 — Métodos produtivos de métricas

## Métodos

### `record_worker_cycle`

- Existe: `False`

### `record_worker_update`

- Existe: `False`

### `record_queue_operation`

- Existe: `False`

### `record_conversation_operation`

- Existe: `True`
- Assinatura: `(self, metric: 'TelegramConversationMetricRecord') -> 'None'`

Código-fonte:

```python
    def record_conversation_operation(
        self,
        metric: TelegramConversationMetricRecord,
    ) -> None:
        error_category = (
            metric.error_category
            or "none"
        )

        self.increment(
            "inna_telegram_operations_total",
            labels={
                "component": metric.component,
                "operation": metric.operation,
                "outcome": metric.outcome,
                "error_category": error_category,
            },
        )

        duration_seconds = max(
            0.0,
            float(
                metric.duration_ms
            )
            / 1000.0,
        )

        self.observe(
            (
                "inna_telegram_"
                "operation_duration_seconds"
            ),
            duration_seconds,
            labels={
                "component": metric.component,
                "operation": metric.operation,
                "outcome": metric.outcome,
            },
        )

        if metric.outcome in {
            "error",
            "conflict",
        }:
            self.increment(
                "inna_telegram_failures_total",
                labels={
                    "component": metric.component,
                    "operation": metric.operation,
                    "error_category": (
                        error_category
                    ),
                },
            )

        if (
            metric.outcome
            in {
                "conflict",
                "recovered",
            }
            or metric.conflict_recovered
            is True
        ):
            conflict_outcome = (
                "recovered"
                if metric.conflict_recovered
                is True
                else metric.outcome
            )

            self.increment(
                "inna_telegram_conflicts_total",
                labels={
                    "operation": metric.operation,
                    "outcome": conflict_outcome,
                },
            )

```

## Pontos de chamada

### `src/channels/telegram_update_worker.py:1154`

- Método: `record_queue_operation`
- Posicionais: `[]`
- Keywords: `{'operation': 'operation', 'outcome': 'outcome', 'error_category': 'error_category'}`

### `src/channels/telegram_update_worker.py:1176`

- Método: `record_worker_cycle`
- Posicionais: `[]`
- Keywords: `{'result': 'cycle_result'}`

### `src/channels/telegram_update_worker.py:1193`

- Método: `record_worker_update`
- Posicionais: `[]`
- Keywords: `{'outcome': 'outcome', 'error_category': 'error_category'}`

### `src/services/telegram_observability/productive_operations.py:267`

- Método: `record_worker_cycle`
- Posicionais: `[]`
- Keywords: `{'result': 'result'}`

### `src/services/telegram_observability/productive_operations.py:280`

- Método: `record_worker_update`
- Posicionais: `[]`
- Keywords: `{'outcome': 'outcome', 'error_category': 'error_category'}`

### `src/services/telegram_observability/productive_operations.py:311`

- Método: `record_queue_operation`
- Posicionais: `[]`
- Keywords: `{'operation': 'operation', 'outcome': 'outcome', 'error_category': 'error_category'}`
