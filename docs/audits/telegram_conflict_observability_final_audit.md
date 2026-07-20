# F2H5-E10 — Auditoria final da observabilidade de conflito

## Resumo

- Chamadas `save_session`: 2
- Chamadas `reload_session`: 1
- Chamadas de observabilidade no orquestrador: 6
- Eventos distintos: 4
- Eventos ausentes: 0
- Eventos inesperados: 0
- Violações de dados sensíveis: 0

## Eventos

- `telegram_session_conflict_detected`: 1 caminho(s)
- `telegram_session_conflict_failed`: 3 caminho(s)
- `telegram_session_conflict_recovered`: 1 caminho(s)
- `telegram_session_conflict_reload_completed`: 1 caminho(s)

## Chamadas observáveis

### Linha 1438

- Operação: `save_session`
- Outcome: `conflict`
- Evento: `telegram_session_conflict_detected`
- Nível: `warning`
- Categoria: `optimistic_conflict`
- Recuperado: `False`

### Linha 1504

- Operação: `reload_session`
- Outcome: `success`
- Evento: `telegram_session_conflict_reload_completed`
- Nível: `info`
- Categoria: `None`
- Recuperado: `None`

### Linha 1571

- Operação: `save_session`
- Outcome: `recovered`
- Evento: `telegram_session_conflict_recovered`
- Nível: `info`
- Categoria: `None`
- Recuperado: `True`

### Linha 1485

- Operação: `reload_session`
- Outcome: `error`
- Evento: `telegram_session_conflict_failed`
- Nível: `error`
- Categoria: `persistence`
- Recuperado: `None`

### Linha 1461

- Operação: `reload_session`
- Outcome: `error`
- Evento: `telegram_session_conflict_failed`
- Nível: `error`
- Categoria: `_conflict_error_category(reload_error)`
- Recuperado: `None`

### Linha 1547

- Operação: `save_session`
- Outcome: `outcome`
- Evento: `telegram_session_conflict_failed`
- Nível: `error`
- Categoria: `category`
- Recuperado: `False if outcome == 'conflict' else None`

## Métodos instrumentados na bridge

- `delete_session`
- `load_or_open_session`
- `reload_session`
- `resolve_language`
- `save_session`
