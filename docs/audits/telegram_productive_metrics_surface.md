# F2H5-G1 — Superfície de métricas produtivas

## Resumo

- Arquivos analisados: 8
- Chamadas candidatas: 159

## Chamadas por arquivo

- `api/telegram_webhook.py`: 94
- `src/channels/telegram_update_worker.py`: 39
- `src/services/telegram_observability/contracts.py`: 17
- `src/services/telegram_observability/metrics.py`: 8
- `src/services/telegram_observability/sanitization.py`: 1

## Candidatos

### 1. `api/telegram_webhook.py:516`

- Função: `get_lang_from_session`
- Chamada: `session.get`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
session.get('lang', 'pt')
```

### 2. `api/telegram_webhook.py:531`

- Função: `get_chat_lang`
- Chamada: `session.get`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
session.get('lang')
```

### 3. `api/telegram_webhook.py:532`

- Função: `get_chat_lang`
- Chamada: `session.get`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
session.get('lang', 'pt')
```

### 4. `api/telegram_webhook.py:763`

- Função: `safe_record_telegram_event`
- Chamada: `record_event`
- Termos métricos: `['record']`
- Termos operacionais: `['update']`

```python
record_event(canal='telegram', usuario=str(payload.get('nome') or 'telegram-user'), usuario_id=f'telegram:{chat_id}', idioma=lang, moeda=moeda, status='success', diagnostico_id=resultado.get('id'), metadata={'origem': 'telegram_webhook', 'evento': 'diagnostico_telegram', 'identity_source': 'authenticated_telegram_update', 'simbolo_moeda': simbolo, 'persistence_status': resultado.get('persistence_status'), 'created': resultado.get('created'), 'score_financeiro': resultado.get('score_financeiro'),
```

### 5. `api/telegram_webhook.py:818`

- Função: `safe_record_telegram_event`
- Chamada: `_emit_telegram_operational_event_safely`
- Termos métricos: `['record']`
- Termos operacionais: `['fail', 'process', 'update']`

```python
_emit_telegram_operational_event_safely(name='telegram_event_persistence_failed', level='error', component='webhook', outcome='error', operation='process_update', error_category='persistence', stage='record_event')
```

### 6. `api/telegram_webhook.py:833`

- Função: `send_telegram_message`
- Chamada: `_emit_telegram_operational_event_safely`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'update']`

```python
_emit_telegram_operational_event_safely(name='telegram_delivery_configuration_missing', level='error', component='webhook', outcome='error', operation='process_update', error_category='configuration', stage='send_message')
```

### 7. `api/telegram_webhook.py:1276`

- Função: `_load_or_open_durable_telegram_session`
- Chamada: `conversation_bridge.load_or_open_session`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
conversation_bridge.load_or_open_session(telegram_user_id, chat_id, {'step': 'idioma', 'lang': 'pt'}, language='pt')
```

### 8. `api/telegram_webhook.py:1288`

- Função: `_load_or_open_durable_telegram_session`
- Chamada: `durable_session.to_processing_state`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'session']`

```python
durable_session.to_processing_state()
```

### 9. `api/telegram_webhook.py:1291`

- Função: `_load_or_open_durable_telegram_session`
- Chamada: `isinstance`
- Termos métricos: `[]`
- Termos operacionais: `['process']`

```python
isinstance(processing_state, dict)
```

### 10. `api/telegram_webhook.py:1299`

- Função: `_load_or_open_durable_telegram_session`
- Chamada: `processing_state.get`
- Termos métricos: `[]`
- Termos operacionais: `['process']`

```python
processing_state.get('step')
```

### 11. `api/telegram_webhook.py:1302`

- Função: `_load_or_open_durable_telegram_session`
- Chamada: `processing_state.get`
- Termos métricos: `[]`
- Termos operacionais: `['process']`

```python
processing_state.get('lang')
```

### 12. `api/telegram_webhook.py:1333`

- Função: `_conflict_observability_duration_ms`
- Chamada: `_conflict_observability_now`
- Termos métricos: `[]`
- Termos operacionais: `['conflict']`

```python
_conflict_observability_now(conversation_bridge)
```

### 13. `api/telegram_webhook.py:1341`

- Função: `_conflict_observability_duration_ms`
- Chamada: `max`
- Termos métricos: `['duration']`
- Termos operacionais: `[]`

```python
max(0.0, duration_ms)
```

### 14. `api/telegram_webhook.py:1393`

- Função: `_record_conflict_observability`
- Chamada: `TelegramConversationMetricRecord`
- Termos métricos: `['duration', 'metric', 'record']`
- Termos operacionais: `['conflict']`

```python
TelegramConversationMetricRecord(operation=operation, component='webhook', outcome=outcome, duration_ms=duration_ms, error_category=error_category, conflict_recovered=conflict_recovered)
```

### 15. `api/telegram_webhook.py:1404`

- Função: `_record_conflict_observability`
- Chamada: `conversation_bridge.metrics.record_operation`
- Termos métricos: `['metric', 'metrics', 'record']`
- Termos operacionais: `[]`

```python
conversation_bridge.metrics.record_operation(metric)
```

### 16. `api/telegram_webhook.py:1460`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `ValueError`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
ValueError('durable_session é obrigatória.')
```

### 17. `api/telegram_webhook.py:1464`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `isinstance`
- Termos métricos: `[]`
- Termos operacionais: `['process']`

```python
isinstance(processing_state, dict)
```

### 18. `api/telegram_webhook.py:1468`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `TypeError`
- Termos métricos: `[]`
- Termos operacionais: `['process']`

```python
TypeError('processing_state deve ser um dict.')
```

### 19. `api/telegram_webhook.py:1475`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `processing_state.get`
- Termos métricos: `[]`
- Termos operacionais: `['process']`

```python
processing_state.get('lang')
```

### 20. `api/telegram_webhook.py:1481`

- Função: `apply_transition`
- Chamada: `target_session.replace_state`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'session']`

```python
target_session.replace_state(processing_state)
```

### 21. `api/telegram_webhook.py:1485`

- Função: `apply_transition`
- Chamada: `target_session.set_language`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
target_session.set_language(resolved_language)
```

### 22. `api/telegram_webhook.py:1491`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `apply_transition`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
apply_transition(durable_session)
```

### 23. `api/telegram_webhook.py:1496`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `conversation_bridge.save_session`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
conversation_bridge.save_session(durable_session, only_if_changed=True)
```

### 24. `api/telegram_webhook.py:1508`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `isinstance`
- Termos métricos: `[]`
- Termos operacionais: `['conflict']`

```python
isinstance(error, conflict_type)
```

### 25. `api/telegram_webhook.py:1516`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_conflict_observability_now`
- Termos métricos: `[]`
- Termos operacionais: `['conflict']`

```python
_conflict_observability_now(conversation_bridge)
```

### 26. `api/telegram_webhook.py:1521`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_record_conflict_observability`
- Termos métricos: `['duration', 'record']`
- Termos operacionais: `['conflict', 'session']`

```python
_record_conflict_observability(conversation_bridge, operation='save_session', outcome='conflict', event_name='telegram_session_conflict_detected', level='warning', duration_ms=0.0, error_category='optimistic_conflict', conflict_recovered=False)
```

### 27. `api/telegram_webhook.py:1538`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `conversation_bridge.reload_session`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
conversation_bridge.reload_session(durable_session)
```

### 28. `api/telegram_webhook.py:1544`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_record_conflict_observability`
- Termos métricos: `['duration', 'record']`
- Termos operacionais: `['conflict', 'fail', 'session']`

```python
_record_conflict_observability(conversation_bridge, operation='reload_session', outcome='error', event_name='telegram_session_conflict_failed', level='error', duration_ms=_conflict_observability_duration_ms(conversation_bridge, started_at=started_at), error_category=_conflict_error_category(reload_error))
```

### 29. `api/telegram_webhook.py:1553`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_conflict_observability_duration_ms`
- Termos métricos: `['duration']`
- Termos operacionais: `['conflict']`

```python
_conflict_observability_duration_ms(conversation_bridge, started_at=started_at)
```

### 30. `api/telegram_webhook.py:1559`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_conflict_error_category`
- Termos métricos: `[]`
- Termos operacionais: `['conflict']`

```python
_conflict_error_category(reload_error)
```

### 31. `api/telegram_webhook.py:1568`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_record_conflict_observability`
- Termos métricos: `['duration', 'record']`
- Termos operacionais: `['conflict', 'fail', 'session']`

```python
_record_conflict_observability(conversation_bridge, operation='reload_session', outcome='error', event_name='telegram_session_conflict_failed', level='error', duration_ms=_conflict_observability_duration_ms(conversation_bridge, started_at=started_at), error_category='persistence')
```

### 32. `api/telegram_webhook.py:1577`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_conflict_observability_duration_ms`
- Termos métricos: `['duration']`
- Termos operacionais: `['conflict']`

```python
_conflict_observability_duration_ms(conversation_bridge, started_at=started_at)
```

### 33. `api/telegram_webhook.py:1587`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_record_conflict_observability`
- Termos métricos: `['duration', 'record']`
- Termos operacionais: `['complete', 'conflict', 'session']`

```python
_record_conflict_observability(conversation_bridge, operation='reload_session', outcome='success', event_name='telegram_session_conflict_reload_completed', level='info', duration_ms=_conflict_observability_duration_ms(conversation_bridge, started_at=started_at))
```

### 34. `api/telegram_webhook.py:1597`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_conflict_observability_duration_ms`
- Termos métricos: `['duration']`
- Termos operacionais: `['conflict']`

```python
_conflict_observability_duration_ms(conversation_bridge, started_at=started_at)
```

### 35. `api/telegram_webhook.py:1604`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `apply_transition`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
apply_transition(reloaded_session)
```

### 36. `api/telegram_webhook.py:1610`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `conversation_bridge.save_session`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
conversation_bridge.save_session(reloaded_session, only_if_changed=True)
```

### 37. `api/telegram_webhook.py:1618`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_conflict_error_category`
- Termos métricos: `[]`
- Termos operacionais: `['conflict']`

```python
_conflict_error_category(recovery_error)
```

### 38. `api/telegram_webhook.py:1630`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_record_conflict_observability`
- Termos métricos: `['duration', 'record']`
- Termos operacionais: `['conflict', 'fail', 'session']`

```python
_record_conflict_observability(conversation_bridge, operation='save_session', outcome=outcome, event_name='telegram_session_conflict_failed', level='error', duration_ms=_conflict_observability_duration_ms(conversation_bridge, started_at=started_at), error_category=category, conflict_recovered=False if outcome == 'conflict' else None)
```

### 39. `api/telegram_webhook.py:1639`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_conflict_observability_duration_ms`
- Termos métricos: `['duration']`
- Termos operacionais: `['conflict']`

```python
_conflict_observability_duration_ms(conversation_bridge, started_at=started_at)
```

### 40. `api/telegram_webhook.py:1654`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_record_conflict_observability`
- Termos métricos: `['duration', 'record']`
- Termos operacionais: `['conflict', 'session']`

```python
_record_conflict_observability(conversation_bridge, operation='save_session', outcome='recovered', event_name='telegram_session_conflict_recovered', level='info', duration_ms=_conflict_observability_duration_ms(conversation_bridge, started_at=started_at), conflict_recovered=True)
```

### 41. `api/telegram_webhook.py:1663`

- Função: `_sync_and_save_durable_telegram_session`
- Chamada: `_conflict_observability_duration_ms`
- Termos métricos: `['duration']`
- Termos operacionais: `['conflict']`

```python
_conflict_observability_duration_ms(conversation_bridge, started_at=started_at)
```

### 42. `api/telegram_webhook.py:1694`

- Função: `_delete_durable_telegram_session`
- Chamada: `ValueError`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
ValueError('durable_session é obrigatória.')
```

### 43. `api/telegram_webhook.py:1698`

- Função: `_delete_durable_telegram_session`
- Chamada: `conversation_bridge.delete_session`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
conversation_bridge.delete_session(durable_session)
```

### 44. `api/telegram_webhook.py:1706`

- Função: `_delete_durable_telegram_session`
- Chamada: `TypeError`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
TypeError('Resultado de delete_session inválido.')
```

### 45. `api/telegram_webhook.py:1736`

- Função: `_resolve_durable_telegram_language`
- Chamada: `isinstance`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
isinstance(session, dict)
```

### 46. `api/telegram_webhook.py:1737`

- Função: `_resolve_durable_telegram_language`
- Chamada: `session.get`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
session.get('lang')
```

### 47. `api/telegram_webhook.py:1742`

- Função: `_resolve_durable_telegram_language`
- Chamada: `get_chat_lang`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
get_chat_lang(chat_id, session)
```

### 48. `api/telegram_webhook.py:1773`

- Função: `process_telegram_update`
- Chamada: `TelegramUpdateIngressConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'update']`

```python
TelegramUpdateIngressConfigurationError('conversation_bridge é obrigatória para o processador Telegram produtivo.')
```

### 49. `api/telegram_webhook.py:1778`

- Função: `process_telegram_update`
- Chamada: `_process_telegram_update_core`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'update']`

```python
_process_telegram_update_core(update, conversation_bridge=conversation_bridge)
```

### 50. `api/telegram_webhook.py:1799`

- Função: `_process_telegram_update_core`
- Chamada: `TelegramUpdateIngressConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
TelegramUpdateIngressConfigurationError('conversation_bridge é obrigatória para o núcleo Telegram durável.')
```

### 51. `api/telegram_webhook.py:1806`

- Função: `_process_telegram_update_core`
- Chamada: `extrair_contexto_confiavel_telegram`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
extrair_contexto_confiavel_telegram(update)
```

### 52. `api/telegram_webhook.py:1812`

- Função: `_process_telegram_update_core`
- Chamada: `_emit_telegram_operational_event_safely`
- Termos métricos: `[]`
- Termos operacionais: `['fail', 'process', 'update']`

```python
_emit_telegram_operational_event_safely(name='telegram_update_processing_failed', level='warning', component='webhook', outcome='discarded', operation='process_update', error_category='validation', stage='validate_context')
```

### 53. `api/telegram_webhook.py:1825`

- Função: `_process_telegram_update_core`
- Chamada: `update.get`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
update.get('message', {})
```

### 54. `api/telegram_webhook.py:1844`

- Função: `_process_telegram_update_core`
- Chamada: `_load_or_open_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['session', 'update']`

```python
_load_or_open_durable_telegram_session(conversation_bridge=conversation_bridge, telegram_user_id=trusted_update.usuario_id, chat_id=chat_id)
```

### 55. `api/telegram_webhook.py:1853`

- Função: `_process_telegram_update_core`
- Chamada: `_resolve_durable_telegram_language`
- Termos métricos: `[]`
- Termos operacionais: `['session', 'update']`

```python
_resolve_durable_telegram_language(chat_id=chat_id, telegram_user_id=trusted_update.usuario_id, session=session, conversation_bridge=conversation_bridge, durable_session=durable_session)
```

### 56. `api/telegram_webhook.py:1860`

- Função: `_process_telegram_update_core`
- Chamada: `_sync_and_save_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'session']`

```python
_sync_and_save_durable_telegram_session(conversation_bridge=conversation_bridge, durable_session=durable_session, processing_state=session, language=lang)
```

### 57. `api/telegram_webhook.py:1874`

- Função: `_process_telegram_update_core`
- Chamada: `_resolve_durable_telegram_language`
- Termos métricos: `[]`
- Termos operacionais: `['session', 'update']`

```python
_resolve_durable_telegram_language(chat_id=chat_id, telegram_user_id=trusted_update.usuario_id, session=session, conversation_bridge=conversation_bridge, durable_session=durable_session)
```

### 58. `api/telegram_webhook.py:1882`

- Função: `_process_telegram_update_core`
- Chamada: `_resolve_durable_telegram_language`
- Termos métricos: `[]`
- Termos operacionais: `['session', 'update']`

```python
_resolve_durable_telegram_language(chat_id=chat_id, telegram_user_id=trusted_update.usuario_id, session=session, conversation_bridge=conversation_bridge, durable_session=durable_session)
```

### 59. `api/telegram_webhook.py:1890`

- Função: `_process_telegram_update_core`
- Chamada: `_resolve_durable_telegram_language`
- Termos métricos: `[]`
- Termos operacionais: `['session', 'update']`

```python
_resolve_durable_telegram_language(chat_id=chat_id, telegram_user_id=trusted_update.usuario_id, session=session, conversation_bridge=conversation_bridge, durable_session=durable_session)
```

### 60. `api/telegram_webhook.py:1892`

- Função: `_process_telegram_update_core`
- Chamada: `_delete_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
_delete_durable_telegram_session(conversation_bridge=conversation_bridge, durable_session=durable_session)
```

### 61. `api/telegram_webhook.py:1908`

- Função: `_process_telegram_update_core`
- Chamada: `_resolve_durable_telegram_language`
- Termos métricos: `[]`
- Termos operacionais: `['session', 'update']`

```python
_resolve_durable_telegram_language(chat_id=chat_id, telegram_user_id=trusted_update.usuario_id, session=None, conversation_bridge=conversation_bridge, durable_session=durable_session)
```

### 62. `api/telegram_webhook.py:1915`

- Função: `_process_telegram_update_core`
- Chamada: `_sync_and_save_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'session']`

```python
_sync_and_save_durable_telegram_session(conversation_bridge=conversation_bridge, durable_session=durable_session, processing_state=session, language=lang)
```

### 63. `api/telegram_webhook.py:1929`

- Função: `_process_telegram_update_core`
- Chamada: `session.get`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
session.get('step')
```

### 64. `api/telegram_webhook.py:1930`

- Função: `_process_telegram_update_core`
- Chamada: `get_lang_from_session`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
get_lang_from_session(session)
```

### 65. `api/telegram_webhook.py:1945`

- Função: `_process_telegram_update_core`
- Chamada: `_sync_and_save_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'session']`

```python
_sync_and_save_durable_telegram_session(conversation_bridge=conversation_bridge, durable_session=durable_session, processing_state=session, language=lang)
```

### 66. `api/telegram_webhook.py:1966`

- Função: `_process_telegram_update_core`
- Chamada: `_sync_and_save_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'session']`

```python
_sync_and_save_durable_telegram_session(conversation_bridge=conversation_bridge, durable_session=durable_session, processing_state=session, language=lang)
```

### 67. `api/telegram_webhook.py:1986`

- Função: `_process_telegram_update_core`
- Chamada: `_sync_and_save_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'session']`

```python
_sync_and_save_durable_telegram_session(conversation_bridge=conversation_bridge, durable_session=durable_session, processing_state=session, language=lang)
```

### 68. `api/telegram_webhook.py:2009`

- Função: `_process_telegram_update_core`
- Chamada: `_sync_and_save_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'session']`

```python
_sync_and_save_durable_telegram_session(conversation_bridge=conversation_bridge, durable_session=durable_session, processing_state=session, language=lang)
```

### 69. `api/telegram_webhook.py:2032`

- Função: `_process_telegram_update_core`
- Chamada: `_sync_and_save_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'session']`

```python
_sync_and_save_durable_telegram_session(conversation_bridge=conversation_bridge, durable_session=durable_session, processing_state=session, language=lang)
```

### 70. `api/telegram_webhook.py:2055`

- Função: `_process_telegram_update_core`
- Chamada: `_sync_and_save_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'session']`

```python
_sync_and_save_durable_telegram_session(conversation_bridge=conversation_bridge, durable_session=durable_session, processing_state=session, language=lang)
```

### 71. `api/telegram_webhook.py:2078`

- Função: `_process_telegram_update_core`
- Chamada: `_sync_and_save_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'session']`

```python
_sync_and_save_durable_telegram_session(conversation_bridge=conversation_bridge, durable_session=durable_session, processing_state=session, language=lang)
```

### 72. `api/telegram_webhook.py:2095`

- Função: `_process_telegram_update_core`
- Chamada: `float`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
float(session.get('dividas_mensais', 0))
```

### 73. `api/telegram_webhook.py:2095`

- Função: `_process_telegram_update_core`
- Chamada: `session.get`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
session.get('dividas_mensais', 0)
```

### 74. `api/telegram_webhook.py:2125`

- Função: `_process_telegram_update_core`
- Chamada: `gerar_diagnostico_pelo_payload`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
gerar_diagnostico_pelo_payload(payload, lang, usuario_id_confiavel=trusted_update.usuario_id, request_id=trusted_update.request_id)
```

### 75. `api/telegram_webhook.py:2139`

- Função: `_process_telegram_update_core`
- Chamada: `safe_record_telegram_event`
- Termos métricos: `['record']`
- Termos operacionais: `[]`

```python
safe_record_telegram_event(chat_id=chat_id, lang=lang, payload=payload, resultado=resultado, resposta=resposta_final)
```

### 76. `api/telegram_webhook.py:2147`

- Função: `_process_telegram_update_core`
- Chamada: `_delete_durable_telegram_session`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
_delete_durable_telegram_session(conversation_bridge=conversation_bridge, durable_session=durable_session)
```

### 77. `api/telegram_webhook.py:2156`

- Função: `_process_telegram_update_core`
- Chamada: `_emit_telegram_operational_event_safely`
- Termos métricos: `[]`
- Termos operacionais: `['fail', 'process', 'update']`

```python
_emit_telegram_operational_event_safely(name='telegram_update_processing_failed', level='error', component='webhook', outcome='error', operation='process_update', error_category='unknown', stage='process_update')
```

### 78. `api/telegram_webhook.py:2184`

- Função: `_fail_claimed_telegram_update_safely`
- Chamada: `fail_authenticated_telegram_update`
- Termos métricos: `[]`
- Termos operacionais: `['fail', 'lease', 'process', 'update']`

```python
fail_authenticated_telegram_update(lease, error_code='telegram.processing_failed')
```

### 79. `api/telegram_webhook.py:2192`

- Função: `_fail_claimed_telegram_update_safely`
- Chamada: `_emit_telegram_operational_event_safely`
- Termos métricos: `['record']`
- Termos operacionais: `['fail', 'receipt']`

```python
_emit_telegram_operational_event_safely(name='telegram_receipt_failure_recording_failed', level='error', component='receipt', outcome='error', operation='fail_receipt', error_category='persistence', stage='record_failure')
```

### 80. `api/telegram_webhook.py:2205`

- Função: `_fail_claimed_telegram_update_safely`
- Chamada: `_emit_telegram_operational_event_safely`
- Termos métricos: `['record']`
- Termos operacionais: `['fail', 'receipt']`

```python
_emit_telegram_operational_event_safely(name='telegram_receipt_failure_recording_failed', level='error', component='receipt', outcome='error', operation='fail_receipt', error_category='persistence', stage='record_failure')
```

### 81. `api/telegram_webhook.py:2232`

- Função: `process_claimed_telegram_update`
- Chamada: `process_telegram_update`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'update']`

```python
process_telegram_update(update, conversation_bridge=conversation_bridge)
```

### 82. `api/telegram_webhook.py:2238`

- Função: `process_claimed_telegram_update`
- Chamada: `_emit_telegram_operational_event_safely`
- Termos métricos: `[]`
- Termos operacionais: `['fail', 'process', 'update', 'worker']`

```python
_emit_telegram_operational_event_safely(name='telegram_worker_processing_failed', level='error', component='worker', outcome='error', operation='process_update', error_category='unknown', stage='worker_processing')
```

### 83. `api/telegram_webhook.py:2250`

- Função: `process_claimed_telegram_update`
- Chamada: `_fail_claimed_telegram_update_safely`
- Termos métricos: `[]`
- Termos operacionais: `['claim', 'fail', 'lease', 'update']`

```python
_fail_claimed_telegram_update_safely(lease)
```

### 84. `api/telegram_webhook.py:2256`

- Função: `process_claimed_telegram_update`
- Chamada: `_fail_claimed_telegram_update_safely`
- Termos métricos: `[]`
- Termos operacionais: `['claim', 'fail', 'lease', 'update']`

```python
_fail_claimed_telegram_update_safely(lease)
```

### 85. `api/telegram_webhook.py:2262`

- Função: `process_claimed_telegram_update`
- Chamada: `complete_authenticated_telegram_update`
- Termos métricos: `[]`
- Termos operacionais: `['complete', 'lease', 'update']`

```python
complete_authenticated_telegram_update(lease)
```

### 86. `api/telegram_webhook.py:2267`

- Função: `process_claimed_telegram_update`
- Chamada: `_emit_telegram_operational_event_safely`
- Termos métricos: `[]`
- Termos operacionais: `['complete', 'fail', 'process', 'receipt', 'worker']`

```python
_emit_telegram_operational_event_safely(name='telegram_worker_processing_failed', level='error', component='receipt', outcome='error', operation='complete_receipt', error_category='persistence', stage='complete_receipt')
```

### 87. `api/telegram_webhook.py:2279`

- Função: `process_claimed_telegram_update`
- Chamada: `_fail_claimed_telegram_update_safely`
- Termos métricos: `[]`
- Termos operacionais: `['claim', 'fail', 'lease', 'update']`

```python
_fail_claimed_telegram_update_safely(lease)
```

### 88. `api/telegram_webhook.py:2284`

- Função: `process_claimed_telegram_update`
- Chamada: `_emit_telegram_operational_event_safely`
- Termos métricos: `[]`
- Termos operacionais: `['complete', 'fail', 'process', 'receipt', 'worker']`

```python
_emit_telegram_operational_event_safely(name='telegram_worker_processing_failed', level='error', component='receipt', outcome='error', operation='complete_receipt', error_category='persistence', stage='complete_receipt')
```

### 89. `api/telegram_webhook.py:2296`

- Função: `process_claimed_telegram_update`
- Chamada: `_fail_claimed_telegram_update_safely`
- Termos métricos: `[]`
- Termos operacionais: `['claim', 'fail', 'lease', 'update']`

```python
_fail_claimed_telegram_update_safely(lease)
```

### 90. `api/telegram_webhook.py:2332`

- Função: `telegram_webhook`
- Chamada: `isinstance`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
isinstance(update, dict)
```

### 91. `api/telegram_webhook.py:2345`

- Função: `telegram_webhook`
- Chamada: `enqueue_authenticated_telegram_update_atomic`
- Termos métricos: `[]`
- Termos operacionais: `['enqueue', 'update']`

```python
enqueue_authenticated_telegram_update_atomic(update)
```

### 92. `api/telegram_webhook.py:2359`

- Função: `telegram_webhook`
- Chamada: `HTTPException`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
HTTPException(status_code=409, detail='Conflito no update Telegram.')
```

### 93. `api/telegram_webhook.py:2371`

- Função: `telegram_webhook`
- Chamada: `HTTPException`
- Termos métricos: `[]`
- Termos operacionais: `['process']`

```python
HTTPException(status_code=503, detail='Processamento Telegram temporariamente indisponível.')
```

### 94. `api/telegram_webhook.py:2380`

- Função: `telegram_webhook`
- Chamada: `HTTPException`
- Termos métricos: `[]`
- Termos operacionais: `['process']`

```python
HTTPException(status_code=503, detail='Processamento Telegram temporariamente indisponível.')
```

### 95. `src/channels/telegram_update_worker.py:83`

- Função: `_configuration_error`
- Chamada: `TelegramUpdateRunnerConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['update', 'worker']`

```python
TelegramUpdateRunnerConfigurationError('A configuração do worker Telegram é inválida.')
```

### 96. `src/channels/telegram_update_worker.py:176`

- Função: `load_worker_config_from_env`
- Chamada: `TelegramUpdateWorkerConfig`
- Termos métricos: `[]`
- Termos operacionais: `['update', 'worker']`

```python
TelegramUpdateWorkerConfig()
```

### 97. `src/channels/telegram_update_worker.py:180`

- Função: `load_worker_config_from_env`
- Chamada: `TelegramUpdateWorkerConfig`
- Termos métricos: `[]`
- Termos operacionais: `['lease', 'retry', 'update', 'worker']`

```python
TelegramUpdateWorkerConfig(lease_seconds=_read_integer(resolved_environment, ENV_LEASE_SECONDS, defaults.lease_seconds), idle_sleep_seconds=_read_float(resolved_environment, ENV_IDLE_SLEEP_SECONDS, defaults.idle_sleep_seconds), unavailable_sleep_seconds=_read_float(resolved_environment, ENV_UNAVAILABLE_SLEEP_SECONDS, defaults.unavailable_sleep_seconds), recovery_interval_seconds=_read_float(resolved_environment, ENV_RECOVERY_INTERVAL_SECONDS, defaults.recovery_interval_seconds), recovery_batch_s
```

### 98. `src/channels/telegram_update_worker.py:181`

- Função: `load_worker_config_from_env`
- Chamada: `_read_integer`
- Termos métricos: `[]`
- Termos operacionais: `['lease']`

```python
_read_integer(resolved_environment, ENV_LEASE_SECONDS, defaults.lease_seconds)
```

### 99. `src/channels/telegram_update_worker.py:216`

- Função: `load_worker_config_from_env`
- Chamada: `_read_integer`
- Termos métricos: `[]`
- Termos operacionais: `['retry']`

```python
_read_integer(resolved_environment, ENV_RETRY_BASE_DELAY_SECONDS, defaults.retry_base_delay_seconds)
```

### 100. `src/channels/telegram_update_worker.py:224`

- Função: `load_worker_config_from_env`
- Chamada: `_read_integer`
- Termos métricos: `[]`
- Termos operacionais: `['retry']`

```python
_read_integer(resolved_environment, ENV_RETRY_MAX_DELAY_SECONDS, defaults.retry_max_delay_seconds)
```

### 101. `src/channels/telegram_update_worker.py:271`

- Função: `_observable_bridge_factory_kwargs`
- Chamada: `signature.bind`
- Termos métricos: `['metric', 'metrics']`
- Termos operacionais: `[]`

```python
signature.bind(metrics=metrics, event_sink=event_sink, clock=clock)
```

### 102. `src/channels/telegram_update_worker.py:342`

- Função: `_resolve_telegram_operational_log_level`
- Chamada: `TelegramUpdateRunnerConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
TelegramUpdateRunnerConfigurationError(f'Nível de logging Telegram inválido. Valores permitidos: {allowed}.')
```

### 103. `src/channels/telegram_update_worker.py:374`

- Função: `create_production_telegram_event_sink`
- Chamada: `TelegramUpdateRunnerConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
TelegramUpdateRunnerConfigurationError('Logger operacional Telegram inválido.')
```

### 104. `src/channels/telegram_update_worker.py:493`

- Função: `load_telegram_processor`
- Chamada: `callable`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'update']`

```python
callable(process_telegram_update)
```

### 105. `src/channels/telegram_update_worker.py:496`

- Função: `load_telegram_processor`
- Chamada: `TelegramUpdateRunnerConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'update']`

```python
TelegramUpdateRunnerConfigurationError('O processador Telegram é inválido.')
```

### 106. `src/channels/telegram_update_worker.py:503`

- Função: `load_telegram_processor`
- Chamada: `TelegramUpdateRunnerConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
TelegramUpdateRunnerConfigurationError('A factory da conversation bridge é inválida.')
```

### 107. `src/channels/telegram_update_worker.py:507`

- Função: `load_telegram_processor`
- Chamada: `callable`
- Termos métricos: `['metric', 'metrics']`
- Termos operacionais: `[]`

```python
callable(metrics_factory)
```

### 108. `src/channels/telegram_update_worker.py:508`

- Função: `load_telegram_processor`
- Chamada: `TelegramUpdateRunnerConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
TelegramUpdateRunnerConfigurationError('A factory de métricas é inválida.')
```

### 109. `src/channels/telegram_update_worker.py:513`

- Função: `load_telegram_processor`
- Chamada: `TelegramUpdateRunnerConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
TelegramUpdateRunnerConfigurationError('A factory de eventos é inválida.')
```

### 110. `src/channels/telegram_update_worker.py:518`

- Função: `load_telegram_processor`
- Chamada: `TelegramUpdateRunnerConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
TelegramUpdateRunnerConfigurationError('O relógio de observabilidade é inválido.')
```

### 111. `src/channels/telegram_update_worker.py:523`

- Função: `load_telegram_processor`
- Chamada: `metrics_factory`
- Termos métricos: `['metric', 'metrics']`
- Termos operacionais: `[]`

```python
metrics_factory()
```

### 112. `src/channels/telegram_update_worker.py:526`

- Função: `load_telegram_processor`
- Chamada: `isinstance`
- Termos métricos: `['metric', 'metrics']`
- Termos operacionais: `[]`

```python
isinstance(metrics, TelegramConversationMetrics)
```

### 113. `src/channels/telegram_update_worker.py:543`

- Função: `load_telegram_processor`
- Chamada: `_observable_bridge_factory_kwargs`
- Termos métricos: `['metric', 'metrics']`
- Termos operacionais: `[]`

```python
_observable_bridge_factory_kwargs(create_postgres_telegram_webhook_conversation_bridge, metrics=metrics, event_sink=event_sink, clock=clock)
```

### 114. `src/channels/telegram_update_worker.py:558`

- Função: `load_telegram_processor`
- Chamada: `TelegramUpdateRunnerConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
TelegramUpdateRunnerConfigurationError('Não foi possível compor o estado conversacional durável.')
```

### 115. `src/channels/telegram_update_worker.py:564`

- Função: `load_telegram_processor`
- Chamada: `TelegramUpdateRunnerConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
TelegramUpdateRunnerConfigurationError('A conversation bridge criada é inválida.')
```

### 116. `src/channels/telegram_update_worker.py:571`

- Função: `process_with_durable_conversation_state`
- Chamada: `process_telegram_update`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'update']`

```python
process_telegram_update(update, conversation_bridge=conversation_bridge)
```

### 117. `src/channels/telegram_update_worker.py:593`

- Função: `_emit_event`
- Chamada: `json.dumps`
- Termos métricos: `['record']`
- Termos operacionais: `[]`

```python
json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
```

### 118. `src/channels/telegram_update_worker.py:625`

- Função: `emit_runner_result`
- Chamada: `_emit_event`
- Termos métricos: `[]`
- Termos operacionais: `['worker']`

```python
_emit_event('telegram_worker_result', result.to_safe_dict(), stream=stream)
```

### 119. `src/channels/telegram_update_worker.py:637`

- Função: `emit_runner_summary`
- Chamada: `_emit_event`
- Termos métricos: `[]`
- Termos operacionais: `['worker']`

```python
_emit_event('telegram_worker_summary', summary.to_safe_dict(), stream=stream)
```

### 120. `src/channels/telegram_update_worker.py:688`

- Função: `_install_signal_handlers`
- Chamada: `TelegramUpdateRunnerConfigurationError`
- Termos métricos: `[]`
- Termos operacionais: `['update', 'worker']`

```python
TelegramUpdateRunnerConfigurationError('O stop_event do worker é inválido.')
```

### 121. `src/channels/telegram_update_worker.py:789`

- Função: `_build_parser`
- Chamada: `argparse.ArgumentParser`
- Termos métricos: `[]`
- Termos operacionais: `['update', 'worker']`

```python
argparse.ArgumentParser(prog='run_telegram_update_worker', description='Executa o worker durável da fila Telegram da INNA.')
```

### 122. `src/channels/telegram_update_worker.py:833`

- Função: `_load_productive_telegram_processor`
- Chamada: `inspect.signature`
- Termos métricos: `[]`
- Termos operacionais: `['process']`

```python
inspect.signature(load_telegram_processor)
```

### 123. `src/channels/telegram_update_worker.py:852`

- Função: `_load_productive_telegram_processor`
- Chamada: `load_telegram_processor`
- Termos métricos: `[]`
- Termos operacionais: `['process']`

```python
load_telegram_processor(**loader_kwargs)
```

### 124. `src/channels/telegram_update_worker.py:891`

- Função: `main`
- Chamada: `load_worker_config_from_env`
- Termos métricos: `[]`
- Termos operacionais: `['worker']`

```python
load_worker_config_from_env()
```

### 125. `src/channels/telegram_update_worker.py:895`

- Função: `main`
- Chamada: `load_telegram_update_keyring_from_env`
- Termos métricos: `[]`
- Termos operacionais: `['update']`

```python
load_telegram_update_keyring_from_env()
```

### 126. `src/channels/telegram_update_worker.py:899`

- Função: `main`
- Chamada: `_load_productive_telegram_processor`
- Termos métricos: `[]`
- Termos operacionais: `['process']`

```python
_load_productive_telegram_processor(stderr=resolved_stderr)
```

### 127. `src/channels/telegram_update_worker.py:908`

- Função: `main`
- Chamada: `_emit_event`
- Termos métricos: `[]`
- Termos operacionais: `['worker']`

```python
_emit_event('telegram_worker_error', {'error_code': 'telegram.worker_configuration_invalid'}, stream=resolved_stderr)
```

### 128. `src/channels/telegram_update_worker.py:922`

- Função: `main`
- Chamada: `_emit_event`
- Termos métricos: `[]`
- Termos operacionais: `['fail', 'worker']`

```python
_emit_event('telegram_worker_error', {'error_code': 'telegram.worker_initialization_failed'}, stream=resolved_stderr)
```

### 129. `src/channels/telegram_update_worker.py:948`

- Função: `main`
- Chamada: `_emit_event`
- Termos métricos: `[]`
- Termos operacionais: `['worker']`

```python
_emit_event('telegram_worker_started', _config_to_safe_dict(config), stream=resolved_stdout)
```

### 130. `src/channels/telegram_update_worker.py:957`

- Função: `main`
- Chamada: `run_telegram_update_worker`
- Termos métricos: `[]`
- Termos operacionais: `['process', 'update', 'worker']`

```python
run_telegram_update_worker(processor, stop_event=stop_event, config=config, keyring=keyring, on_result=lambda result: emit_runner_result(result, stream=resolved_stdout), max_cycles=arguments.max_cycles)
```

### 131. `src/channels/telegram_update_worker.py:979`

- Função: `main`
- Chamada: `_emit_event`
- Termos métricos: `[]`
- Termos operacionais: `['worker']`

```python
_emit_event('telegram_worker_stopped', {'reason': 'keyboard_interrupt'}, stream=resolved_stdout)
```

### 132. `src/channels/telegram_update_worker.py:993`

- Função: `main`
- Chamada: `_emit_event`
- Termos métricos: `[]`
- Termos operacionais: `['worker']`

```python
_emit_event('telegram_worker_error', {'error_code': 'telegram.worker_configuration_invalid'}, stream=resolved_stderr)
```

### 133. `src/channels/telegram_update_worker.py:1007`

- Função: `main`
- Chamada: `_emit_event`
- Termos métricos: `[]`
- Termos operacionais: `['fail', 'worker']`

```python
_emit_event('telegram_worker_error', {'error_code': 'telegram.worker_runtime_failed'}, stream=resolved_stderr)
```

### 134. `src/services/telegram_observability/contracts.py:8`

- Função: `<module>`
- Chamada: `frozenset`
- Termos métricos: `[]`
- Termos operacionais: `['claim', 'complete', 'fail', 'process', 'receipt', 'session', 'update']`

```python
frozenset({'load_or_open_session', 'save_session', 'reload_session', 'delete_session', 'resolve_language', 'claim_update', 'process_update', 'complete_receipt', 'fail_receipt', 'rollback'})
```

### 135. `src/services/telegram_observability/contracts.py:23`

- Função: `<module>`
- Chamada: `frozenset`
- Termos métricos: `[]`
- Termos operacionais: `['receipt', 'worker']`

```python
frozenset({'bridge', 'worker', 'webhook', 'receipt', 'repository'})
```

### 136. `src/services/telegram_observability/contracts.py:33`

- Função: `<module>`
- Chamada: `frozenset`
- Termos métricos: `[]`
- Termos operacionais: `['conflict']`

```python
frozenset({'success', 'error', 'conflict', 'recovered', 'discarded', 'skipped'})
```

### 137. `src/services/telegram_observability/contracts.py:44`

- Função: `<module>`
- Chamada: `frozenset`
- Termos métricos: `[]`
- Termos operacionais: `['conflict']`

```python
frozenset({'configuration', 'validation', 'security', 'identity', 'persistence', 'external_service', 'optimistic_conflict', 'timeout', 'unavailable', 'unknown'})
```

### 138. `src/services/telegram_observability/contracts.py:92`

- Função: `_validate_duration`
- Chamada: `ValueError`
- Termos métricos: `['duration']`
- Termos operacionais: `[]`

```python
ValueError('duration_ms não pode ser negativa.')
```

### 139. `src/services/telegram_observability/contracts.py:97`

- Função: `_validate_duration`
- Chamada: `ValueError`
- Termos métricos: `['duration']`
- Termos operacionais: `[]`

```python
ValueError('duration_ms não pode ser NaN.')
```

### 140. `src/services/telegram_observability/contracts.py:105`

- Função: `_validate_duration`
- Chamada: `ValueError`
- Termos métricos: `['duration']`
- Termos operacionais: `[]`

```python
ValueError('duration_ms deve ser finita.')
```

### 141. `src/services/telegram_observability/contracts.py:125`

- Função: `__post_init__`
- Chamada: `object.__setattr__`
- Termos métricos: `['metric']`
- Termos operacionais: `[]`

```python
object.__setattr__(self, 'operation', _validate_choice(field_name='operation', value=self.operation, allowed=ALLOWED_METRIC_OPERATIONS))
```

### 142. `src/services/telegram_observability/contracts.py:128`

- Função: `__post_init__`
- Chamada: `_validate_choice`
- Termos métricos: `['metric']`
- Termos operacionais: `[]`

```python
_validate_choice(field_name='operation', value=self.operation, allowed=ALLOWED_METRIC_OPERATIONS)
```

### 143. `src/services/telegram_observability/contracts.py:135`

- Função: `__post_init__`
- Chamada: `object.__setattr__`
- Termos métricos: `['metric']`
- Termos operacionais: `[]`

```python
object.__setattr__(self, 'component', _validate_choice(field_name='component', value=self.component, allowed=ALLOWED_METRIC_COMPONENTS))
```

### 144. `src/services/telegram_observability/contracts.py:138`

- Função: `__post_init__`
- Chamada: `_validate_choice`
- Termos métricos: `['metric']`
- Termos operacionais: `[]`

```python
_validate_choice(field_name='component', value=self.component, allowed=ALLOWED_METRIC_COMPONENTS)
```

### 145. `src/services/telegram_observability/contracts.py:155`

- Função: `__post_init__`
- Chamada: `object.__setattr__`
- Termos métricos: `['duration']`
- Termos operacionais: `[]`

```python
object.__setattr__(self, 'duration_ms', _validate_duration(self.duration_ms))
```

### 146. `src/services/telegram_observability/contracts.py:158`

- Função: `__post_init__`
- Chamada: `_validate_duration`
- Termos métricos: `['duration']`
- Termos operacionais: `[]`

```python
_validate_duration(self.duration_ms)
```

### 147. `src/services/telegram_observability/contracts.py:182`

- Função: `__post_init__`
- Chamada: `ValueError`
- Termos métricos: `[]`
- Termos operacionais: `['conflict']`

```python
ValueError('error_category é obrigatória para outcomes error ou conflict.')
```

### 148. `src/services/telegram_observability/contracts.py:195`

- Função: `__post_init__`
- Chamada: `ValueError`
- Termos métricos: `[]`
- Termos operacionais: `['conflict']`

```python
ValueError('conflict_recovered somente pode ser usado em conflito ou recuperação.')
```

### 149. `src/services/telegram_observability/contracts.py:247`

- Função: `__post_init__`
- Chamada: `object.__setattr__`
- Termos métricos: `['metric']`
- Termos operacionais: `[]`

```python
object.__setattr__(self, 'component', _validate_choice(field_name='component', value=self.component, allowed=ALLOWED_METRIC_COMPONENTS))
```

### 150. `src/services/telegram_observability/contracts.py:250`

- Função: `__post_init__`
- Chamada: `_validate_choice`
- Termos métricos: `['metric']`
- Termos operacionais: `[]`

```python
_validate_choice(field_name='component', value=self.component, allowed=ALLOWED_METRIC_COMPONENTS)
```

### 151. `src/services/telegram_observability/metrics.py:43`

- Função: `record_operation`
- Chamada: `isinstance`
- Termos métricos: `['metric', 'record']`
- Termos operacionais: `[]`

```python
isinstance(record, TelegramConversationMetricRecord)
```

### 152. `src/services/telegram_observability/metrics.py:47`

- Função: `record_operation`
- Chamada: `TypeError`
- Termos métricos: `['metric', 'record']`
- Termos operacionais: `[]`

```python
TypeError('record deve ser TelegramConversationMetricRecord.')
```

### 153. `src/services/telegram_observability/metrics.py:53`

- Função: `record_operation`
- Chamada: `self._records.append`
- Termos métricos: `['record']`
- Termos operacionais: `[]`

```python
self._records.append(record)
```

### 154. `src/services/telegram_observability/metrics.py:62`

- Função: `snapshot`
- Chamada: `tuple`
- Termos métricos: `['record']`
- Termos operacionais: `[]`

```python
tuple(self._records)
```

### 155. `src/services/telegram_observability/metrics.py:68`

- Função: `clear`
- Chamada: `self._records.clear`
- Termos métricos: `['record']`
- Termos operacionais: `[]`

```python
self._records.clear()
```

### 156. `src/services/telegram_observability/metrics.py:78`

- Função: `count`
- Chamada: `sum`
- Termos métricos: `['record']`
- Termos operacionais: `[]`

```python
sum((1 for record in self.snapshot() if (operation is None or record.operation == operation) and (component is None or record.component == component) and (outcome is None or record.outcome == outcome) and (error_category is None or record.error_category == error_category)))
```

### 157. `src/services/telegram_observability/metrics.py:106`

- Função: `operation_counts`
- Chamada: `Counter`
- Termos métricos: `['counter', 'record']`
- Termos operacionais: `[]`

```python
Counter(((record.component, record.operation, record.outcome) for record in self.snapshot()))
```

### 158. `src/services/telegram_observability/metrics.py:122`

- Função: `durations_ms`
- Chamada: `tuple`
- Termos métricos: `['duration', 'record']`
- Termos operacionais: `[]`

```python
tuple((record.duration_ms for record in self.snapshot() if operation is None or record.operation == operation))
```

### 159. `src/services/telegram_observability/sanitization.py:10`

- Função: `<module>`
- Chamada: `frozenset`
- Termos métricos: `[]`
- Termos operacionais: `['session']`

```python
frozenset({'chat_id', 'telegram_user_id', 'session_id', 'payload', 'encrypted_payload', 'decrypted_payload', 'message_text', 'text', 'state', 'financial_data', 'nome', 'renda', 'renda_mensal', 'gastos', 'gastos_fixos', 'gastos_variaveis', 'dividas', 'dividas_mensais', 'reserva', 'reserva_atual', 'objetivo', 'token', 'secret', 'password', 'database_url', 'configuration_value', 'query', 'parameters', 'exception_message_raw'})
```

