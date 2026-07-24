# Contrato de exportação Prometheus das métricas Telegram

## Status

F2H5-J1 — Exportador Prometheus/OpenMetrics.

## Objetivo

Converter snapshots imutáveis das métricas produtivas do Telegram em formatos textuais compatíveis com Prometheus e OpenMetrics.

## Snapshot de origem

O exportador recebe um `TelegramProductiveMetricsSnapshot` com:

- `counters`;
- `histograms`.

As estruturas são imutáveis e expostas como `mappingproxy`.

Cada histograma utiliza `TelegramHistogramSnapshot` com:

- `count`;
- `sum`;
- `buckets`.

## Prometheus Text Exposition

Content-Type:

text/plain; version=0.0.4; charset=utf-8

## OpenMetrics

Content-Type:

application/openmetrics-text; version=1.0.0; charset=utf-8

Uma resposta OpenMetrics deve terminar com:

# EOF

## Contadores

Cada contador deve possuir uma declaração TYPE:

# TYPE inna_telegram_worker_cycles_total counter

## Histogramas

Cada histograma deve exportar:

- `_bucket`;
- `_sum`;
- `_count`;
- bucket final `+Inf`.

## Regras

- validar nomes de métricas;
- validar nomes de labels;
- ordenar métricas e labels;
- escapar aspas, barras e quebras de linha;
- preservar determinismo;
- não modificar o snapshot;
- rejeitar estruturas inválidas.

## Privacidade

Não podem ser exportados:

- `update_id`;
- `chat_id`;
- `user_id`;
- `claim_token`;
- payloads;
- mensagens;
- dados financeiros;
- textos de exceção;
- stack traces.

Valores não reconhecidos devem permanecer normalizados como `unknown`.

## Próximas integrações

1. exportador Prometheus/OpenMetrics;
2. health e readiness;
3. autenticação interna;
4. endpoint interno de métricas;
5. coleta pelo Prometheus;
6. dashboards Grafana;
7. alertas operacionais.

