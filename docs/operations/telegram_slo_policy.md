# Política de SLOs do worker Telegram

## Disponibilidade

- Objetivo: 99.500%
- Janela: 30 dias
- Error budget: 0.500%
- Indisponibilidade permitida: 3.60 horas

## Taxa de sucesso

- Objetivo: 99.00%
- Budget de falhas: 1.00%

## Latência

- p95: 2.000 segundos
- p99: 5.000 segundos

## Backlog

- Warning: 25 jobs
- Critical: 100 jobs

## Dead-letter

- Warning: 1
- Critical: 5

## Freshness

- Warning: 120 segundos
- Critical: 300 segundos

## Burn rate

- Warning: 2.0x
- Critical: 6.0x

## Janelas

- Curta: 300 segundos
- Média: 3600 segundos
- Longa: 2592000 segundos

## Observação

Os valores iniciais devem ser recalibrados após coleta de dados reais em produção.
