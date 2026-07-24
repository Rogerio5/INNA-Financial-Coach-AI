# Telegram Structured Logging JSON

## Objetivo

Definir o contrato canônico dos logs operacionais Telegram emitidos pela INNA.

Cada evento deve produzir exatamente uma linha JSON.

## Schema obrigatório

| Campo | Tipo | Regra |
|---|---|---|
| `timestamp` | string | ISO-8601 UTC com sufixo `Z` |
| `level` | string | `debug`, `info`, `warning`, `error` ou `critical` |
| `event` | string | Nome iniciado por `telegram_` |
| `component` | string | Componente permitido pelo contrato |
| `outcome` | string | Resultado permitido pelo contrato |
| `fields` | object | Mapa sanitizado e de baixa cardinalidade |

## Exemplo canônico

```json
{
  "component": "webhook",
  "event": "telegram_session_conflict_detected",
  "fields": {
    "conflict_recovered": false,
    "error_category": "optimistic_conflict",
    "operation": "save_session"
  },
  "level": "warning",
  "outcome": "conflict",
  "timestamp": "2026-07-20T03:15:00.000Z"
}
```

## Mapeamento de níveis

- `debug` → `10`
- `info` → `20`
- `warning` → `30`
- `error` → `40`
- `critical` → `50`

## Serialização

- Uma linha JSON por evento.
- UTF-8 preservado com `ensure_ascii=False`.
- `allow_nan=False`.
- Chaves ordenadas para saída determinística.
- Sem traceback ou mensagem interna de exceção.

## Campos proibidos

- `authorization`
- `chat_id`
- `database_url`
- `exception_message`
- `financial_data`
- `message_text`
- `password`
- `payload`
- `processing_state`
- `secret`
- `telegram_user_id`
- `token`
- `traceback`

## Política de falhas

- Valores não serializáveis devem ser convertidos para marcador seguro.
- `NaN` e infinito não podem aparecer no JSON final.
- Falha do logger não pode derrubar a operação principal.
- Sanitização deve ocorrer imediatamente antes da serialização.
