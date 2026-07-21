# Contrato de SLOs operacionais do Telegram

## Status

F2H5-I2.

## Objetivo

Definir objetivos de nível de serviço para o worker Telegram com limites validados, error budget e severidades operacionais.

## Escopo

A política cobre:

- disponibilidade;
- taxa de sucesso;
- latência;
- backlog;
- dead-letter;
- freshness das métricas;
- burn rate;
- janelas de avaliação;
- severidades warning e critical.

## Princípios

- a política não depende de Prometheus;
- a política não executa queries;
- a política não consome jobs;
- a política não acessa PostgreSQL;
- a política não contém identificadores privados;
- a política deve ser imutável;
- todos os limites devem ser validados.

## Disponibilidade

Objetivo inicial recomendado:

99.5 por cento em janela de 30 dias.

Esse objetivo permite aproximadamente 3 horas e 36 minutos de indisponibilidade em 30 dias.

## Taxa de sucesso

Objetivo inicial recomendado:

99 por cento dos processamentos devem terminar com sucesso.

Falhas transitórias recuperadas podem ser contabilizadas separadamente de falhas finais.

## Latência

Objetivos iniciais recomendados:

- p95 menor ou igual a 2 segundos;
- p99 menor ou igual a 5 segundos.

## Backlog

Limites iniciais:

- warning a partir de 25 jobs pendentes;
- critical a partir de 100 jobs pendentes.

## Dead-letter

Limites iniciais:

- warning quando houver 1 ou mais ocorrências na janela;
- critical quando houver 5 ou mais ocorrências na janela.

## Freshness

As métricas devem ser consideradas desatualizadas quando não houver atualização dentro do limite configurado.

Limites iniciais:

- warning após 120 segundos;
- critical após 300 segundos.

## Burn rate

Burn rate representa a velocidade de consumo do error budget.

Valores iniciais:

- warning: 2 vezes o orçamento esperado;
- critical: 6 vezes o orçamento esperado.

## Severidades

### Warning

Indica deterioração que ainda permite investigação antes de impacto amplo.

### Critical

Indica indisponibilidade, consumo acelerado do error budget ou risco operacional imediato.

## Janelas

Política inicial:

- janela curta: 5 minutos;
- janela média: 1 hora;
- janela longa: 30 dias.

## Error budget

Para um objetivo de disponibilidade S:

error_budget = 1 - S

Exemplo:

SLO de 99.5 por cento gera error budget de 0.5 por cento.

## Operações proibidas

A camada de SLO não pode:

- executar PromQL;
- importar cliente Prometheus;
- consultar banco;
- consumir jobs;
- alterar métricas;
- registrar payloads;
- armazenar tokens;
- expor exceções brutas.

## Evolução futura

Os valores iniciais devem ser recalibrados com dados reais de produção após uma janela de observação.
