# F2H5-F8A — Migração dos prints operacionais

## Resumo

- Prints encontrados: 10

## Classificação

- `context_specific`: 5
- `preserve_cli_contract`: 1
- `structured_event`: 4

## Prints

### 1. `api/telegram_webhook.py:752`

- Função: `safe_record_telegram_event`
- Dentro de except: `True`
- Tipo do except: `Exception`
- Estratégia: `structured_event`
- Evento: `telegram_event_persistence_failed`
- Nível: `error`
- Componente: `webhook`
- Outcome: `error`
- Categoria: `persistence`

```python
print(
            "[telegram-event-log] "
            "Falha segura ao registrar evento."
        )
```

### 2. `api/telegram_webhook.py:760`

- Função: `send_telegram_message`
- Dentro de except: `False`
- Tipo do except: `None`
- Estratégia: `structured_event`
- Evento: `telegram_delivery_configuration_missing`
- Nível: `error`
- Componente: `webhook`
- Outcome: `error`
- Categoria: `configuration`

```python
print("TELEGRAM_BOT_TOKEN não configurado.")
```

### 3. `api/telegram_webhook.py:1729`

- Função: `_process_telegram_update_core`
- Dentro de except: `True`
- Tipo do except: `TelegramUpdateContextError`
- Estratégia: `context_specific`
- Evento: `telegram_update_processing_failed`
- Nível: `warning`
- Componente: `webhook`
- Outcome: `error`
- Categoria: `unknown`

```python
print(
            "[telegram-webhook] "
            "Update inválido descartado."
        )
```

### 4. `api/telegram_webhook.py:2066`

- Função: `_process_telegram_update_core`
- Dentro de except: `True`
- Tipo do except: `Exception`
- Estratégia: `context_specific`
- Evento: `telegram_update_processing_failed`
- Nível: `warning`
- Componente: `webhook`
- Outcome: `error`
- Categoria: `unknown`

```python
print(
            "[telegram-webhook] "
            "Falha segura ao processar atualização."
        )
```

### 5. `api/telegram_webhook.py:2095`

- Função: `_fail_claimed_telegram_update_safely`
- Dentro de except: `True`
- Tipo do except: `TelegramUpdateReceiptServiceError`
- Estratégia: `structured_event`
- Evento: `telegram_receipt_failure_recording_failed`
- Nível: `error`
- Componente: `receipt`
- Outcome: `error`
- Categoria: `persistence`

```python
print(
            "[telegram-webhook] "
            "Falha segura ao atualizar receipt."
        )
```

### 6. `api/telegram_webhook.py:2101`

- Função: `_fail_claimed_telegram_update_safely`
- Dentro de except: `True`
- Tipo do except: `Exception`
- Estratégia: `structured_event`
- Evento: `telegram_receipt_failure_recording_failed`
- Nível: `error`
- Componente: `receipt`
- Outcome: `error`
- Categoria: `persistence`

```python
print(
            "[telegram-webhook] "
            "Falha segura ao atualizar receipt."
        )
```

### 7. `api/telegram_webhook.py:2127`

- Função: `process_claimed_telegram_update`
- Dentro de except: `True`
- Tipo do except: `Exception`
- Estratégia: `context_specific`
- Evento: `telegram_worker_processing_failed`
- Nível: `error`
- Componente: `worker`
- Outcome: `error`
- Categoria: `unknown`

```python
print(
            "[telegram-webhook] "
            "Falha segura no worker Telegram."
        )
```

### 8. `api/telegram_webhook.py:2149`

- Função: `process_claimed_telegram_update`
- Dentro de except: `True`
- Tipo do except: `TelegramUpdateReceiptServiceError`
- Estratégia: `context_specific`
- Evento: `telegram_worker_processing_failed`
- Nível: `error`
- Componente: `worker`
- Outcome: `error`
- Categoria: `unknown`

```python
print(
            "[telegram-webhook] "
            "Falha segura ao concluir receipt."
        )
```

### 9. `api/telegram_webhook.py:2159`

- Função: `process_claimed_telegram_update`
- Dentro de except: `True`
- Tipo do except: `Exception`
- Estratégia: `context_specific`
- Evento: `telegram_worker_processing_failed`
- Nível: `error`
- Componente: `worker`
- Outcome: `error`
- Categoria: `unknown`

```python
print(
            "[telegram-webhook] "
            "Falha segura ao concluir receipt."
        )
```

### 10. `src/channels/telegram_update_worker.py:604`

- Função: `_emit_event`
- Dentro de except: `False`
- Tipo do except: `None`
- Estratégia: `preserve_cli_contract`
- Evento: `None`
- Nível: `None`
- Componente: `worker`
- Outcome: `None`
- Categoria: `None`

```python
print(
        serialized,
        file=stream,
        flush=True,
    )
```

