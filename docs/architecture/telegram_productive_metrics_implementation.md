# Métricas produtivas do Telegram

## Status

Implementação concluída na fase F2H5-G.

## Objetivo

Fornecer métricas operacionais agregadas e de baixa cardinalidade para o fluxo durável do Telegram, sem exportar identificadores, payloads, mensagens, tokens, dados financeiros ou textos de exceção.

## Famílias

- `inna_telegram_operations_total`
- `inna_telegram_operation_duration_seconds`
- `inna_telegram_conflicts_total`
- `inna_telegram_receipts_total`
- `inna_telegram_worker_cycles_total`
- `inna_telegram_worker_updates_total`
- `inna_telegram_queue_operations_total`
- `inna_telegram_failures_total`

## Componentes

### Registry

`InMemoryTelegramProductiveMetrics`

Responsável por:

- contadores;
- histogramas;
- normalização de labels;
- snapshots imutáveis;
- segurança concorrente;
- cardinalidade controlada.

### Proteção de falhas

`SafeTelegramProductiveMetrics`

Falhas da camada de observabilidade não interrompem o processamento do Telegram.

### Adapter da bridge

`ProductiveTelegramConversationMetricsAdapter`

Converte métricas da bridge de conversação em famílias produtivas agregadas.

### API operacional

`TelegramProductiveOperationsRecorder`

Expõe métodos seguros:

- `record_worker_cycle`;
- `record_worker_update`;
- `record_receipt`;
- `record_queue_operation`.

### Composição do worker

`TelegramProductiveMetricsRuntime`

Mantém uma única instância do registry durante a vida do processo do worker.

## Semântica do runner

### Ciclos

- `idle` → `empty`
- processamento concluído ou finalizado → `processed`
- falha operacional → `failed`
- valor desconhecido → `unknown`

### Updates

- execução concluída → `success`
- replay idempotente → `duplicate`
- falha → `error`
- recovery → não contabiliza update

### Receipts

- conclusão → `completed`
- retry/dead letter → `failed`
- perda de ownership → `released`
- replay idempotente → `duplicate`
- recovery → não contabiliza receipt

### Fila

- claim → `claim`
- conclusão → `acknowledge`
- retry → `release`
- dead letter → `fail`
- recovery → `recover`

## Replay idempotente

Replay é registrado como `duplicate`.

Isso diferencia uma execução original de uma confirmação idempotente sem criar labels dinâmicas.

## Recovery

Recovery gera:

- um ciclo do worker;
- uma operação `recover` da fila.

Recovery não gera:

- update processado;
- receipt artificial.

## Cardinalidade

Valores não reconhecidos são normalizados para `unknown`.

Nenhum dos seguintes dados pode ser usado como label:

- `update_id`;
- `chat_id`;
- `user_id`;
- tokens;
- payloads;
- mensagens;
- dados financeiros;
- textos de exceção;
- stack traces.

## Contagem

Cada resultado entregue ao callback produtivo registra no máximo:

- um ciclo;
- um update;
- um receipt;
- uma operação da fila.

A quantidade exata depende da semântica do resultado.

## Exportação

O registry está preparado para a próxima etapa de exportação:

- endpoint Prometheus;
- health/readiness;
- dashboards Grafana;
- alertas operacionais.
