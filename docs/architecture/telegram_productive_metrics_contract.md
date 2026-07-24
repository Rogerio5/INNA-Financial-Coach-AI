# Contrato de métricas produtivas do Telegram

## Objetivo

Definir métricas agregadas, estáveis e seguras para observar o canal Telegram da INNA.

## Princípios

- Métricas não transportam dados pessoais.
- Identificadores nunca são labels.
- Texto livre nunca é label.
- Exceções são classificadas, não copiadas.
- Durações são exportadas em segundos.
- Labels possuem vocabulário fechado.
- Falha do exporter não interrompe o produto.
- O contrato é independente do Prometheus.

## Métricas

### `inna_telegram_operations_total`

- Tipo: `counter`
- Unidade: `operations`
- Labels: `component`, `operation`, `outcome`, `error_category`

Total de operações produtivas do canal Telegram.

### `inna_telegram_operation_duration_seconds`

- Tipo: `histogram`
- Unidade: `seconds`
- Labels: `component`, `operation`, `outcome`

Duração das operações produtivas do Telegram.

### `inna_telegram_conflicts_total`

- Tipo: `counter`
- Unidade: `conflicts`
- Labels: `operation`, `outcome`

Total de conflitos otimistas e seus resultados.

### `inna_telegram_receipts_total`

- Tipo: `counter`
- Unidade: `receipts`
- Labels: `receipt_status`, `outcome`, `error_category`

Total de transições de receipts duráveis.

### `inna_telegram_worker_cycles_total`

- Tipo: `counter`
- Unidade: `cycles`
- Labels: `worker_result`

Total de ciclos executados pelo worker.

### `inna_telegram_worker_updates_total`

- Tipo: `counter`
- Unidade: `updates`
- Labels: `outcome`, `error_category`

Total de updates processados pelo worker.

### `inna_telegram_queue_operations_total`

- Tipo: `counter`
- Unidade: `operations`
- Labels: `queue_operation`, `outcome`, `error_category`

Total de operações da fila criptografada.

### `inna_telegram_failures_total`

- Tipo: `counter`
- Unidade: `failures`
- Labels: `component`, `operation`, `error_category`

Total agregado de falhas operacionais.

## Labels proibidas

- `user_id`
- `telegram_user_id`
- `chat_id`
- `update_id`
- `message_id`
- `receipt_id`
- `claim_token`
- `lease_token`
- `session_id`
- `username`
- `name`
- `email`
- `phone`
- `language_text`
- `message_text`
- `payload`
- `processing_state`
- `financial_data`
- `income`
- `expenses`
- `debt`
- `score`
- `token`
- `secret`
- `password`
- `authorization`
- `database_url`
- `exception`
- `exception_message`
- `traceback`

## Regras de cardinalidade

- Máximo de quatro labels por família de métrica.
- Máximo de vinte valores previstos por label.
- Não utilizar valores gerados pelo usuário.
- Não utilizar IDs, datas ou timestamps.
- Não utilizar mensagens de exceção.

