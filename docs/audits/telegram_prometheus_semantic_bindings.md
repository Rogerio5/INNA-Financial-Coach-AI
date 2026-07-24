# F2H5-I3A — Vinculação semântica das métricas

## Resumo

- Métricas válidas encontradas: 16

## `operation_total`

- Obrigatória: `True`
- Estado: `resolved`
- Selecionada: `inna_telegram_operations_total`

### Candidatas

- `inna_telegram_operations_total` — score `205`

## `duration_histogram`

- Obrigatória: `True`
- Estado: `resolved`
- Selecionada: `inna_telegram_operation_duration_seconds`

### Candidatas

- `inna_telegram_operation_duration_seconds` — score `305`

## `error_total`

- Obrigatória: `False`
- Estado: `resolved`
- Selecionada: `inna_telegram_failures_total`

### Candidatas

- `inna_telegram_failures_total` — score `205`

## `retry_total`

- Obrigatória: `False`
- Estado: `missing`
- Selecionada: `None`

### Candidatas

- Nenhuma métrica real encontrada.

## `dead_letter_total`

- Obrigatória: `False`
- Estado: `missing`
- Selecionada: `None`

### Candidatas

- Nenhuma métrica real encontrada.

## `backlog`

- Obrigatória: `False`
- Estado: `missing`
- Selecionada: `None`

### Candidatas

- Nenhuma métrica real encontrada.

## `freshness_timestamp`

- Obrigatória: `False`
- Estado: `missing`
- Selecionada: `None`

### Candidatas

- Nenhuma métrica real encontrada.
