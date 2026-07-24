# Alertas Prometheus do Telegram

## Objetivo

Documentar os alertas operacionais do worker, fila, receipts e operações conversacionais do Telegram.

## Métricas utilizadas

- `inna_telegram_worker_updates_total`
- `inna_telegram_worker_cycles_total`
- `inna_telegram_failures_total`
- `inna_telegram_operation_duration_seconds_bucket`
- `inna_telegram_operations_total`
- `inna_telegram_queue_operations_total`
- `inna_telegram_receipts_total`

## Taxa de falhas do worker

O denominador é o total de atualizações processadas pelo worker.

O numerador é o contador de falhas com `component="worker"` e `operation="process_update"`.

## Burn rate

O SLO inicial de sucesso é 99%.

O error budget correspondente é 1%.

- warning sustentado: burn rate igual ou superior a 2x;
- critical rápido: burn rate igual ou superior a 6x.

## Latência

- warning quando p95 ultrapassar 2 segundos;
- critical quando p99 ultrapassar 5 segundos.

## Conflitos

Um volume elevado de conflitos pode indicar contenção, concorrência excessiva ou problemas de idempotência.

## Fila e receipts

Falhas persistentes nesses componentes devem ser investigadas junto ao banco, estado dos receipts e comportamento do worker.

## Procedimento de investigação

1. Verificar `/health` e `/ready`.
2. Verificar a taxa de atualizações do worker.
3. Separar falhas por `error_category`.
4. Verificar conflitos e falhas de persistência.
5. Verificar logs estruturados no mesmo intervalo.
6. Confirmar se houve alteração recente de configuração ou deploy.

## Métricas ainda ausentes

Não existem atualmente métricas confirmadas para:

- backlog;
- dead-letter;
- retries;
- freshness.

Alertas para esses sinais somente devem ser adicionados após implementação e validação das métricas correspondentes.
