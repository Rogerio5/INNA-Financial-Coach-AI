# Contrato HTTP de health e readiness do Telegram

## Status

F2H5-H4 — Contrato HTTP seguro de health e readiness.

## Objetivo

Adaptar snapshots operacionais do Telegram para respostas HTTP seguras, versionadas, determinísticas e independentes do framework web.

## Endpoints

### /health

Indica se o processo está vivo.

- healthy: HTTP 200;
- degraded: HTTP 200;
- unready: HTTP 503.

O health básico não deve depender obrigatoriamente do PostgreSQL, Telegram API, Gemini API, Gmail ou consumo de jobs.

### /ready

Indica se o worker está apto a receber e processar trabalho.

O readiness pode verificar:

- configuração;
- conexão PostgreSQL;
- repositório de jobs;
- repositório de receipts;
- keyring;
- processor;
- runtime de métricas.

- healthy: HTTP 200;
- degraded: HTTP 200;
- unready: HTTP 503.

## Versão do contrato

schema_version: telegram-operational-status.v1

## Visibilidade pública

A resposta pública pode conter:

- schema_version;
- probe;
- status;
- ready;
- sequence;
- cache_hit;
- reason.

A resposta pública não deve expor os checks internos.

## Visibilidade interna

A resposta interna pode conter checks normalizados, latência, categorias de erro e metadados do runtime.

Nunca devem ser expostos:

- senhas;
- tokens;
- DSNs;
- chaves de criptografia;
- payloads;
- exceções brutas;
- stack traces;
- user IDs;
- chat IDs;
- update IDs;
- claim tokens;
- dados financeiros.

## Headers obrigatórios

- Content-Type: application/json; charset=utf-8
- Cache-Control: no-store
- X-Content-Type-Options: nosniff
- X-INNA-Schema-Version: telegram-operational-status.v1
- X-INNA-Operational-Status: healthy, degraded ou unready

## Serialização JSON

- utilizar UTF-8;
- ordenar as chaves;
- impedir NaN e infinito;
- ser determinística;
- terminar com quebra de linha;
- não depender do repr de objetos internos.

## Fail-safe

Se a adaptação ou serialização falhar:

- retornar HTTP 503;
- utilizar status unready;
- utilizar reason response_serialization_failure;
- não expor a exceção original.

## Independência de framework

O adaptador não pode importar FastAPI, Starlette, Flask, Django, requests ou httpx.

## Operações proibidas

A camada HTTP não pode:

- consumir jobs;
- executar claim;
- renovar leases;
- completar ou falhar jobs;
- recuperar jobs expirados;
- escrever receipts;
- enviar mensagens;
- chamar Gemini;
- executar transações de escrita ou commit.

## Integração futura

- GET /health
- GET /ready
- GET /internal/ready

A rota interna deverá ser protegida e desabilitada por padrão.
