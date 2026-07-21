# F2H5-G6A — Worker, receipts e fila

## Resumo

- Arquivos analisados: 165
- Funções candidatas: 62
- Classes candidatas: 38
- Chamadas candidatas: 278

## Candidatos por arquivo

- `api/main.py`: 2
- `api/telegram_webhook.py`: 7
- `src/agents/gemini_client.py`: 1
- `src/agents/supervisor_deadline.py`: 1
- `src/app.py`: 2
- `src/channels/telegram_update_worker.py`: 4
- `src/dashboard.py`: 3
- `src/database.py`: 1
- `src/database/connection.py`: 1
- `src/database/legacy.py`: 1
- `src/feedback.py`: 4
- `src/gemini_client.py`: 4
- `src/observability/timeline.py`: 2
- `src/repository.py`: 2
- `src/services/rag/document_repository.py`: 5
- `src/services/rag/vector_store.py`: 3
- `src/services/telegram_conversation_state/repository.py`: 14
- `src/services/telegram_update_jobs/execution.py`: 2
- `src/services/telegram_update_jobs/ingress.py`: 6
- `src/services/telegram_update_jobs/repository.py`: 2
- `src/services/telegram_update_jobs/runner.py`: 33
- `src/services/telegram_update_jobs/worker.py`: 125
- `src/services/telegram_update_receipts/repository.py`: 24
- `src/services/telegram_update_receipts/service.py`: 27
- `src/tools/observability.py`: 2

## Funções

### 1. `api/main.py:714`

- Classe: `<module>`
- Função: `registrar_feedback`
- Parâmetros: `['payload']`
- Termos: `['ack']`

### 2. `api/main.py:737`

- Classe: `<module>`
- Função: `listar_feedbacks`
- Parâmetros: `['limit']`
- Termos: `['ack']`

### 3. `api/telegram_webhook.py:2180`

- Classe: `<module>`
- Função: `_fail_claimed_telegram_update_safely`
- Parâmetros: `['lease']`
- Termos: `['claim', 'fail']`

### 4. `api/telegram_webhook.py:2220`

- Classe: `<module>`
- Função: `process_claimed_telegram_update`
- Parâmetros: `['update', 'lease', 'conversation_bridge']`
- Termos: `['claim', 'process_claimed']`

### 5. `src/agents/nodes.py:840`

- Classe: `<module>`
- Função: `fallback_agent_node`
- Parâmetros: `['state']`
- Termos: `['ack']`

### 6. `src/agents/supervisor_deadline.py:61`

- Classe: `<module>`
- Função: `_parse_worker_output`
- Parâmetros: `['stdout']`
- Termos: `['worker']`

### 7. `src/api_client.py:372`

- Classe: `<module>`
- Função: `enviar_feedback_api`
- Parâmetros: `['payload']`
- Termos: `['ack']`

### 8. `src/channels/telegram_update_worker.py:163`

- Classe: `<module>`
- Função: `load_worker_config_from_env`
- Parâmetros: `['environment']`
- Termos: `['worker']`

### 9. `src/dashboard.py:3504`

- Classe: `<module>`
- Função: `render_feedbacks`
- Parâmetros: `['feedbacks_df']`
- Termos: `['ack']`

### 10. `src/feedback.py:11`

- Classe: `<module>`
- Função: `save_feedback`
- Parâmetros: `['nome', 'util', 'comentario', 'score_financeiro', 'nivel_risco']`
- Termos: `['ack']`

### 11. `src/gemini_client.py:215`

- Classe: `<module>`
- Função: `generate_fallback_plan`
- Parâmetros: `['payload', 'diagnosis']`
- Termos: `['ack']`

### 12. `src/repository.py:36`

- Classe: `<module>`
- Função: `save_feedback_db`
- Parâmetros: `['nome', 'util', 'comentario', 'score_financeiro', 'nivel_risco']`
- Termos: `['ack']`

### 13. `src/repository.py:94`

- Classe: `<module>`
- Função: `list_feedbacks_db`
- Parâmetros: `['limit']`
- Termos: `['ack']`

### 14. `src/services/telegram_conversation_state/repository.py:396`

- Classe: `<module>`
- Função: `_safe_rollback`
- Parâmetros: `['connection']`
- Termos: `['ack']`

### 15. `src/services/telegram_update_jobs/execution.py:144`

- Classe: `<module>`
- Função: `_validate_worker_lease`
- Parâmetros: `['lease']`
- Termos: `['lease', 'worker']`

### 16. `src/services/telegram_update_jobs/execution.py:486`

- Classe: `<module>`
- Função: `decrypt_authenticated_telegram_worker_lease`
- Parâmetros: `['lease', 'keyring']`
- Termos: `['lease', 'worker']`

### 17. `src/services/telegram_update_jobs/ingress.py:228`

- Classe: `<module>`
- Função: `_generate_claim_token`
- Parâmetros: `[]`
- Termos: `['claim']`

### 18. `src/services/telegram_update_jobs/ingress.py:256`

- Classe: `<module>`
- Função: `_receipt_snapshot_from_row`
- Parâmetros: `['row']`
- Termos: `['receipt']`

### 19. `src/services/telegram_update_jobs/ingress.py:581`

- Classe: `<module>`
- Função: `enqueue_authenticated_telegram_update_atomic`
- Parâmetros: `['update', 'receipt_lease_seconds', 'max_attempts', 'keyring']`
- Termos: `['enqueue', 'queue']`

### 20. `src/services/telegram_update_jobs/repository.py:533`

- Classe: `<module>`
- Função: `_lease_from_row`
- Parâmetros: `['row']`
- Termos: `['lease']`

### 21. `src/services/telegram_update_jobs/repository.py:622`

- Classe: `<module>`
- Função: `enqueue_telegram_update_job`
- Parâmetros: `['update_id', 'payload_ciphertext', 'payload_nonce', 'payload_key_id', 'payload_version', 'max_attempts']`
- Termos: `['enqueue', 'queue']`

### 22. `src/services/telegram_update_jobs/repository.py:739`

- Classe: `<module>`
- Função: `claim_next_telegram_update_job`
- Parâmetros: `['lock_token', 'lease_seconds']`
- Termos: `['claim']`

### 23. `src/services/telegram_update_jobs/repository.py:799`

- Classe: `<module>`
- Função: `renew_telegram_update_job_lease`
- Parâmetros: `['update_id', 'lock_token', 'lease_seconds']`
- Termos: `['lease']`

### 24. `src/services/telegram_update_jobs/repository.py:871`

- Classe: `<module>`
- Função: `complete_telegram_update_job`
- Parâmetros: `['update_id', 'lock_token']`
- Termos: `['complete']`

### 25. `src/services/telegram_update_jobs/repository.py:932`

- Classe: `<module>`
- Função: `retry_or_dead_letter_telegram_update_job`
- Parâmetros: `['update_id', 'lock_token', 'error_code', 'retry_delay_seconds']`
- Termos: `['retry']`

### 26. `src/services/telegram_update_jobs/repository.py:1012`

- Classe: `<module>`
- Função: `recover_expired_telegram_update_jobs`
- Parâmetros: `['limit']`
- Termos: `['recover']`

### 27. `src/services/telegram_update_jobs/runner.py:454`

- Classe: `<module>`
- Função: `calculate_worker_retry_delay_seconds`
- Parâmetros: `['attempt_count', 'config']`
- Termos: `['retry', 'worker']`

### 28. `src/services/telegram_update_jobs/runner.py:491`

- Classe: `<module>`
- Função: `_result_for_lease`
- Parâmetros: `['lease', 'decision', 'stage', 'job_status', 'error_code', 'idempotent_replay']`
- Termos: `['lease']`

### 29. `src/services/telegram_update_jobs/runner.py:518`

- Classe: `<module>`
- Função: `_finalize_failure`
- Parâmetros: `['lease', 'dependencies', 'config', 'error_code', 'force_dead_letter']`
- Termos: `['fail']`

### 30. `src/services/telegram_update_jobs/runner.py:1006`

- Classe: `<module>`
- Função: `run_telegram_update_worker`
- Parâmetros: `['processor', 'stop_event', 'config', 'dependencies', 'keyring', 'on_result', 'max_cycles']`
- Termos: `['run_telegram_update_worker', 'worker']`

### 31. `src/services/telegram_update_jobs/service.py:733`

- Classe: `<module>`
- Função: `calculate_telegram_update_retry_delay`
- Parâmetros: `['attempt_count', 'base_seconds', 'max_seconds']`
- Termos: `['retry']`

### 32. `src/services/telegram_update_jobs/worker.py:384`

- Classe: `<module>`
- Função: `_worker_lease_from_rows`
- Parâmetros: `['candidate', 'job_row', 'receipt_row']`
- Termos: `['lease', 'worker']`

### 33. `src/services/telegram_update_jobs/worker.py:538`

- Classe: `<module>`
- Função: `claim_next_authenticated_telegram_update_job_atomic`
- Parâmetros: `['lease_seconds']`
- Termos: `['claim']`

### 34. `src/services/telegram_update_jobs/worker.py:866`

- Classe: `TelegramUpdateWorkerCompletionOutcome`
- Função: `completed`
- Parâmetros: `['self']`
- Termos: `['complete']`

### 35. `src/services/telegram_update_jobs/worker.py:961`

- Classe: `<module>`
- Função: `_validate_completion_lease`
- Parâmetros: `['lease']`
- Termos: `['lease']`

### 36. `src/services/telegram_update_jobs/worker.py:1067`

- Classe: `<module>`
- Função: `_owned_receipt_completion_from_row`
- Parâmetros: `['row']`
- Termos: `['receipt']`

### 37. `src/services/telegram_update_jobs/worker.py:1126`

- Classe: `<module>`
- Função: `_completed_job_from_row`
- Parâmetros: `['row']`
- Termos: `['complete']`

### 38. `src/services/telegram_update_jobs/worker.py:1187`

- Classe: `<module>`
- Função: `_completed_receipt_from_row`
- Parâmetros: `['row']`
- Termos: `['complete', 'receipt']`

### 39. `src/services/telegram_update_jobs/worker.py:1237`

- Classe: `<module>`
- Função: `_validate_completed_job_matches_lease`
- Parâmetros: `['lease', 'job']`
- Termos: `['complete', 'lease']`

### 40. `src/services/telegram_update_jobs/worker.py:1336`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Parâmetros: `['lease']`
- Termos: `['complete']`

### 41. `src/services/telegram_update_jobs/worker.py:1853`

- Classe: `TelegramUpdateWorkerFailureOutcome`
- Função: `retry_scheduled`
- Parâmetros: `['self']`
- Termos: `['retry']`

### 42. `src/services/telegram_update_jobs/worker.py:1926`

- Classe: `<module>`
- Função: `_validate_worker_error_code`
- Parâmetros: `['value']`
- Termos: `['worker']`

### 43. `src/services/telegram_update_jobs/worker.py:1969`

- Classe: `<module>`
- Função: `_failure_receipt_from_row`
- Parâmetros: `['row']`
- Termos: `['fail', 'receipt']`

### 44. `src/services/telegram_update_jobs/worker.py:2053`

- Classe: `<module>`
- Função: `_failed_job_from_row`
- Parâmetros: `['row']`
- Termos: `['fail']`

### 45. `src/services/telegram_update_jobs/worker.py:2159`

- Classe: `<module>`
- Função: `_failed_receipt_result_from_row`
- Parâmetros: `['row']`
- Termos: `['fail', 'receipt']`

### 46. `src/services/telegram_update_jobs/worker.py:2217`

- Classe: `<module>`
- Função: `_validate_failed_job_matches_lease`
- Parâmetros: `['lease', 'job', 'error_code']`
- Termos: `['fail', 'lease']`

### 47. `src/services/telegram_update_jobs/worker.py:2262`

- Classe: `<module>`
- Função: `_build_failure_outcome`
- Parâmetros: `['lease', 'decision', 'job', 'receipt_attempt_count', 'retry_delay_seconds', 'error_code']`
- Termos: `['fail']`

### 48. `src/services/telegram_update_jobs/worker.py:2313`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Parâmetros: `['lease', 'error_code', 'retry_delay_seconds', 'force_dead_letter']`
- Termos: `['retry']`

### 49. `src/services/telegram_update_jobs/worker.py:2885`

- Classe: `TelegramUpdateWorkerRecoveryRecord`
- Função: `retry_scheduled`
- Parâmetros: `['self']`
- Termos: `['retry']`

### 50. `src/services/telegram_update_jobs/worker.py:2981`

- Classe: `<module>`
- Função: `_recovery_record_from_row`
- Parâmetros: `['row']`
- Termos: `['recover']`

### 51. `src/services/telegram_update_jobs/worker.py:3077`

- Classe: `<module>`
- Função: `recover_expired_authenticated_telegram_update_jobs_atomic`
- Parâmetros: `['limit']`
- Termos: `['recover']`

### 52. `src/services/telegram_update_receipts/repository.py:284`

- Classe: `<module>`
- Função: `_validar_lease_seconds`
- Parâmetros: `['value']`
- Termos: `['lease']`

### 53. `src/services/telegram_update_receipts/repository.py:374`

- Classe: `<module>`
- Função: `_resultado_claim`
- Parâmetros: `['row', 'status', 'claim_token']`
- Termos: `['claim']`

### 54. `src/services/telegram_update_receipts/repository.py:410`

- Classe: `<module>`
- Função: `_resultado_lifecycle`
- Parâmetros: `['row', 'expected_status']`
- Termos: `['cycle']`

### 55. `src/services/telegram_update_receipts/repository.py:453`

- Classe: `<module>`
- Função: `claim_telegram_update`
- Parâmetros: `['update_id', 'update_fingerprint', 'claim_token', 'lease_seconds']`
- Termos: `['claim']`

### 56. `src/services/telegram_update_receipts/repository.py:672`

- Classe: `<module>`
- Função: `complete_telegram_update`
- Parâmetros: `['update_id', 'claim_token']`
- Termos: `['complete']`

### 57. `src/services/telegram_update_receipts/repository.py:744`

- Classe: `<module>`
- Função: `fail_telegram_update`
- Parâmetros: `['update_id', 'claim_token', 'error_code']`
- Termos: `['fail']`

### 58. `src/services/telegram_update_receipts/service.py:260`

- Classe: `<module>`
- Função: `_generate_claim_token`
- Parâmetros: `[]`
- Termos: `['claim']`

### 59. `src/services/telegram_update_receipts/service.py:275`

- Classe: `<module>`
- Função: `claim_authenticated_telegram_update`
- Parâmetros: `['update', 'lease_seconds']`
- Termos: `['claim']`

### 60. `src/services/telegram_update_receipts/service.py:381`

- Classe: `<module>`
- Função: `_validate_lease`
- Parâmetros: `['lease']`
- Termos: `['lease']`

### 61. `src/services/telegram_update_receipts/service.py:424`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update`
- Parâmetros: `['lease']`
- Termos: `['complete']`

### 62. `src/services/telegram_update_receipts/service.py:472`

- Classe: `<module>`
- Função: `fail_authenticated_telegram_update`
- Parâmetros: `['lease', 'error_code']`
- Termos: `['fail']`

## Chamadas

### 1. `api/main.py:717`

- Classe: `<module>`
- Função: `registrar_feedback`
- Chamada: `save_feedback_db`
- Termos: `['ack']`

```python
save_feedback_db(nome=payload_dict['nome'], util=payload_dict['util'], comentario=payload_dict['comentario'], score_financeiro=payload_dict['score_financeiro'], nivel_risco=payload_dict['nivel_risco'])
```

### 2. `api/main.py:738`

- Classe: `<module>`
- Função: `listar_feedbacks`
- Chamada: `list_feedbacks_db`
- Termos: `['ack']`

```python
list_feedbacks_db(limit=limit)
```

### 3. `api/telegram_webhook.py:2184`

- Classe: `<module>`
- Função: `_fail_claimed_telegram_update_safely`
- Chamada: `fail_authenticated_telegram_update`
- Termos: `['fail']`

```python
fail_authenticated_telegram_update(lease, error_code='telegram.processing_failed')
```

### 4. `api/telegram_webhook.py:2250`

- Classe: `<module>`
- Função: `process_claimed_telegram_update`
- Chamada: `_fail_claimed_telegram_update_safely`
- Termos: `['claim', 'fail']`

```python
_fail_claimed_telegram_update_safely(lease)
```

### 5. `api/telegram_webhook.py:2256`

- Classe: `<module>`
- Função: `process_claimed_telegram_update`
- Chamada: `_fail_claimed_telegram_update_safely`
- Termos: `['claim', 'fail']`

```python
_fail_claimed_telegram_update_safely(lease)
```

### 6. `api/telegram_webhook.py:2262`

- Classe: `<module>`
- Função: `process_claimed_telegram_update`
- Chamada: `complete_authenticated_telegram_update`
- Termos: `['complete']`

```python
complete_authenticated_telegram_update(lease)
```

### 7. `api/telegram_webhook.py:2279`

- Classe: `<module>`
- Função: `process_claimed_telegram_update`
- Chamada: `_fail_claimed_telegram_update_safely`
- Termos: `['claim', 'fail']`

```python
_fail_claimed_telegram_update_safely(lease)
```

### 8. `api/telegram_webhook.py:2296`

- Classe: `<module>`
- Função: `process_claimed_telegram_update`
- Chamada: `_fail_claimed_telegram_update_safely`
- Termos: `['claim', 'fail']`

```python
_fail_claimed_telegram_update_safely(lease)
```

### 9. `api/telegram_webhook.py:2345`

- Classe: `<module>`
- Função: `telegram_webhook`
- Chamada: `enqueue_authenticated_telegram_update_atomic`
- Termos: `['enqueue', 'queue']`

```python
enqueue_authenticated_telegram_update_atomic(update)
```

### 10. `src/agents/gemini_client.py:38`

- Classe: `<module>`
- Função: `get_supervisor_client`
- Chamada: `types.HttpRetryOptions`
- Termos: `['retry']`

```python
types.HttpRetryOptions(attempts=config.retry_attempts, initial_delay=1.0, max_delay=3.0, exp_base=2.0, jitter=0.2, http_status_codes=_TRANSIENT_STATUS_CODES)
```

### 11. `src/agents/supervisor_deadline.py:151`

- Classe: `<module>`
- Função: `classificar_com_gemini_com_deadline`
- Chamada: `_parse_worker_output`
- Termos: `['worker']`

```python
_parse_worker_output(completed.stdout)
```

### 12. `src/app.py:6349`

- Classe: `<module>`
- Função: `<module>`
- Chamada: `enviar_feedback_api`
- Termos: `['ack']`

```python
enviar_feedback_api(feedback_payload)
```

### 13. `src/app.py:6682`

- Classe: `<module>`
- Função: `<module>`
- Chamada: `enviar_feedback_api`
- Termos: `['ack']`

```python
enviar_feedback_api(feedback_payload)
```

### 14. `src/channels/telegram_update_worker.py:180`

- Classe: `<module>`
- Função: `load_worker_config_from_env`
- Chamada: `TelegramUpdateWorkerConfig`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConfig()
```

### 15. `src/channels/telegram_update_worker.py:184`

- Classe: `<module>`
- Função: `load_worker_config_from_env`
- Chamada: `TelegramUpdateWorkerConfig`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConfig(lease_seconds=_read_integer(resolved_environment, ENV_LEASE_SECONDS, defaults.lease_seconds), idle_sleep_seconds=_read_float(resolved_environment, ENV_IDLE_SLEEP_SECONDS, defaults.idle_sleep_seconds), unavailable_sleep_seconds=_read_float(resolved_environment, ENV_UNAVAILABLE_SLEEP_SECONDS, defaults.unavailable_sleep_seconds), recovery_interval_seconds=_read_float(resolved_environment, ENV_RECOVERY_INTERVAL_SECONDS, defaults.recovery_interval_seconds), recovery_batch_size=_read_integer(resolved_environment, ENV_RECOVERY_BATCH_SIZE, defaults.recovery_batch_size), retry_base_delay_seconds=_read_integer(resolved_environment, ENV_RETRY_BASE_DELAY_SECONDS, defaults.retr
```

### 16. `src/channels/telegram_update_worker.py:968`

- Classe: `<module>`
- Função: `main`
- Chamada: `load_worker_config_from_env`
- Termos: `['worker']`

```python
load_worker_config_from_env()
```

### 17. `src/channels/telegram_update_worker.py:1039`

- Classe: `<module>`
- Função: `main`
- Chamada: `run_telegram_update_worker`
- Termos: `['run_telegram_update_worker', 'worker']`

```python
run_telegram_update_worker(processor, stop_event=stop_event, config=config, keyring=keyring, on_result=lambda result: emit_runner_result(result, stream=resolved_stdout), max_cycles=arguments.max_cycles)
```

### 18. `src/dashboard.py:3529`

- Classe: `<module>`
- Função: `render_feedbacks`
- Chamada: `feedbacks_df.head`
- Termos: `['ack']`

```python
feedbacks_df.head(50)
```

### 19. `src/dashboard.py:4615`

- Classe: `<module>`
- Função: `render_export`
- Chamada: `feedbacks_df.to_csv`
- Termos: `['ack']`

```python
feedbacks_df.to_csv(index=False)
```

### 20. `src/dashboard.py:8002`

- Classe: `<module>`
- Função: `main`
- Chamada: `render_feedbacks`
- Termos: `['ack']`

```python
render_feedbacks(feedbacks_filtrados)
```

### 21. `src/database.py:43`

- Classe: `<module>`
- Função: `get_db_session`
- Chamada: `session.rollback`
- Termos: `['ack']`

```python
session.rollback()
```

### 22. `src/database/connection.py:526`

- Classe: `<module>`
- Função: `conexao_postgres`
- Chamada: `conexao.rollback`
- Termos: `['ack']`

```python
conexao.rollback()
```

### 23. `src/database/legacy.py:47`

- Classe: `<module>`
- Função: `get_db_session`
- Chamada: `session.rollback`
- Termos: `['ack']`

```python
session.rollback()
```

### 24. `src/feedback.py:18`

- Classe: `<module>`
- Função: `save_feedback`
- Chamada: `FEEDBACK_PATH.parent.mkdir`
- Termos: `['ack']`

```python
FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
```

### 25. `src/feedback.py:20`

- Classe: `<module>`
- Função: `save_feedback`
- Chamada: `FEEDBACK_PATH.exists`
- Termos: `['ack']`

```python
FEEDBACK_PATH.exists()
```

### 26. `src/feedback.py:22`

- Classe: `<module>`
- Função: `save_feedback`
- Chamada: `FEEDBACK_PATH.open`
- Termos: `['ack']`

```python
FEEDBACK_PATH.open('a', newline='', encoding='utf-8')
```

### 27. `src/feedback.py:48`

- Classe: `<module>`
- Função: `save_feedback`
- Chamada: `save_feedback_db`
- Termos: `['ack']`

```python
save_feedback_db(nome=nome, util=util, comentario=comentario, score_financeiro=score_financeiro, nivel_risco=nivel_risco)
```

### 28. `src/gemini_client.py:661`

- Classe: `<module>`
- Função: `generate_ai_plan`
- Chamada: `generate_fallback_plan`
- Termos: `['ack']`

```python
generate_fallback_plan(payload, diagnosis)
```

### 29. `src/gemini_client.py:664`

- Classe: `<module>`
- Função: `generate_ai_plan`
- Chamada: `generate_fallback_plan`
- Termos: `['ack']`

```python
generate_fallback_plan(payload, diagnosis)
```

### 30. `src/gemini_client.py:691`

- Classe: `<module>`
- Função: `generate_ai_plan`
- Chamada: `generate_fallback_plan`
- Termos: `['ack']`

```python
generate_fallback_plan(payload, diagnosis)
```

### 31. `src/gemini_client.py:696`

- Classe: `<module>`
- Função: `generate_ai_plan`
- Chamada: `generate_fallback_plan`
- Termos: `['ack']`

```python
generate_fallback_plan(payload, diagnosis)
```

### 32. `src/observability/timeline.py:177`

- Classe: `<module>`
- Função: `preparar_tabela_timeline`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

### 33. `src/observability/timeline.py:344`

- Classe: `<module>`
- Função: `registrar_evento_timeline`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

### 34. `src/repository.py:46`

- Classe: `<module>`
- Função: `save_feedback_db`
- Chamada: `FeedbackUsuario`
- Termos: `['ack']`

```python
FeedbackUsuario(nome=nome, util=util, comentario=comentario, score_financeiro=int(score_financeiro), nivel_risco=nivel_risco)
```

### 35. `src/repository.py:100`

- Classe: `<module>`
- Função: `list_feedbacks_db`
- Chamada: `FeedbackUsuario.id.desc`
- Termos: `['ack']`

```python
FeedbackUsuario.id.desc()
```

### 36. `src/services/rag/document_repository.py:169`

- Classe: `<module>`
- Função: `preparar_tabelas_documentos`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

### 37. `src/services/rag/document_repository.py:283`

- Classe: `<module>`
- Função: `registrar_historico_documento`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

### 38. `src/services/rag/document_repository.py:409`

- Classe: `<module>`
- Função: `registrar_documento`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

### 39. `src/services/rag/document_repository.py:671`

- Classe: `<module>`
- Função: `atualizar_processamento_documento`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

### 40. `src/services/rag/document_repository.py:778`

- Classe: `<module>`
- Função: `atualizar_status_documento`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

### 41. `src/services/rag/vector_store.py:172`

- Classe: `<module>`
- Função: `preparar_tabela_embeddings`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

### 42. `src/services/rag/vector_store.py:234`

- Classe: `<module>`
- Função: `excluir_embeddings_documento`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

### 43. `src/services/rag/vector_store.py:443`

- Classe: `<module>`
- Função: `salvar_chunks_embeddings`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

### 44. `src/services/telegram_conversation_state/repository.py:400`

- Classe: `<module>`
- Função: `_safe_rollback`
- Chamada: `connection.rollback`
- Termos: `['ack']`

```python
connection.rollback()
```

### 45. `src/services/telegram_conversation_state/repository.py:444`

- Classe: `<module>`
- Função: `load_telegram_conversation_state`
- Chamada: `connection.rollback`
- Termos: `['ack']`

```python
connection.rollback()
```

### 46. `src/services/telegram_conversation_state/repository.py:447`

- Classe: `<module>`
- Função: `load_telegram_conversation_state`
- Chamada: `_safe_rollback`
- Termos: `['ack']`

```python
_safe_rollback(connection)
```

### 47. `src/services/telegram_conversation_state/repository.py:453`

- Classe: `<module>`
- Função: `load_telegram_conversation_state`
- Chamada: `_safe_rollback`
- Termos: `['ack']`

```python
_safe_rollback(connection)
```

### 48. `src/services/telegram_conversation_state/repository.py:535`

- Classe: `<module>`
- Função: `create_telegram_conversation_state`
- Chamada: `connection.rollback`
- Termos: `['ack']`

```python
connection.rollback()
```

### 49. `src/services/telegram_conversation_state/repository.py:556`

- Classe: `<module>`
- Função: `create_telegram_conversation_state`
- Chamada: `_safe_rollback`
- Termos: `['ack']`

```python
_safe_rollback(connection)
```

### 50. `src/services/telegram_conversation_state/repository.py:562`

- Classe: `<module>`
- Função: `create_telegram_conversation_state`
- Chamada: `_safe_rollback`
- Termos: `['ack']`

```python
_safe_rollback(connection)
```

### 51. `src/services/telegram_conversation_state/repository.py:639`

- Classe: `<module>`
- Função: `save_telegram_conversation_state`
- Chamada: `connection.rollback`
- Termos: `['ack']`

```python
connection.rollback()
```

### 52. `src/services/telegram_conversation_state/repository.py:661`

- Classe: `<module>`
- Função: `save_telegram_conversation_state`
- Chamada: `_safe_rollback`
- Termos: `['ack']`

```python
_safe_rollback(connection)
```

### 53. `src/services/telegram_conversation_state/repository.py:667`

- Classe: `<module>`
- Função: `save_telegram_conversation_state`
- Chamada: `_safe_rollback`
- Termos: `['ack']`

```python
_safe_rollback(connection)
```

### 54. `src/services/telegram_conversation_state/repository.py:721`

- Classe: `<module>`
- Função: `delete_telegram_conversation_state`
- Chamada: `_safe_rollback`
- Termos: `['ack']`

```python
_safe_rollback(connection)
```

### 55. `src/services/telegram_conversation_state/repository.py:727`

- Classe: `<module>`
- Função: `delete_telegram_conversation_state`
- Chamada: `_safe_rollback`
- Termos: `['ack']`

```python
_safe_rollback(connection)
```

### 56. `src/services/telegram_conversation_state/repository.py:776`

- Classe: `<module>`
- Função: `delete_expired_telegram_conversation_states`
- Chamada: `_safe_rollback`
- Termos: `['ack']`

```python
_safe_rollback(connection)
```

### 57. `src/services/telegram_conversation_state/repository.py:782`

- Classe: `<module>`
- Função: `delete_expired_telegram_conversation_states`
- Chamada: `_safe_rollback`
- Termos: `['ack']`

```python
_safe_rollback(connection)
```

### 58. `src/services/telegram_update_jobs/execution.py:503`

- Classe: `<module>`
- Função: `decrypt_authenticated_telegram_worker_lease`
- Chamada: `_validate_worker_lease`
- Termos: `['lease', 'worker']`

```python
_validate_worker_lease(lease)
```

### 59. `src/services/telegram_update_jobs/execution.py:610`

- Classe: `<module>`
- Função: `decrypt_authenticated_telegram_worker_lease`
- Chamada: `TelegramUpdateWorkerPayload`
- Termos: `['worker']`

```python
TelegramUpdateWorkerPayload(update_id=normalized_lease.update_id, job_attempt_count=normalized_lease.job_attempt_count, job_max_attempts=normalized_lease.job_max_attempts, receipt_attempt_count=normalized_lease.receipt_attempt_count, payload_version=normalized_lease.payload_version, payload_key_id=normalized_lease.payload_key_id, _payload=frozen_payload)
```

### 60. `src/services/telegram_update_jobs/ingress.py:329`

- Classe: `<module>`
- Função: `_receipt_snapshot_from_row`
- Chamada: `_ReceiptSnapshot`
- Termos: `['receipt']`

```python
_ReceiptSnapshot(update_id=update_id, status=status, attempt_count=attempt_count, update_fingerprint=fingerprint_value, lease_active=lease_active)
```

### 61. `src/services/telegram_update_jobs/ingress.py:650`

- Classe: `<module>`
- Função: `enqueue_authenticated_telegram_update_atomic`
- Chamada: `receipt_service.fingerprint_telegram_update`
- Termos: `['receipt']`

```python
receipt_service.fingerprint_telegram_update(normalized_update)
```

### 62. `src/services/telegram_update_jobs/ingress.py:669`

- Classe: `<module>`
- Função: `enqueue_authenticated_telegram_update_atomic`
- Chamada: `_generate_claim_token`
- Termos: `['claim']`

```python
_generate_claim_token()
```

### 63. `src/services/telegram_update_jobs/ingress.py:701`

- Classe: `<module>`
- Função: `enqueue_authenticated_telegram_update_atomic`
- Chamada: `_receipt_snapshot_from_row`
- Termos: `['receipt']`

```python
_receipt_snapshot_from_row(inserted_receipt_row)
```

### 64. `src/services/telegram_update_jobs/ingress.py:740`

- Classe: `<module>`
- Função: `enqueue_authenticated_telegram_update_atomic`
- Chamada: `_receipt_snapshot_from_row`
- Termos: `['receipt']`

```python
_receipt_snapshot_from_row(existing_row)
```

### 65. `src/services/telegram_update_jobs/ingress.py:823`

- Classe: `<module>`
- Função: `enqueue_authenticated_telegram_update_atomic`
- Chamada: `_receipt_snapshot_from_row`
- Termos: `['receipt']`

```python
_receipt_snapshot_from_row(reclaimed_row)
```

### 66. `src/services/telegram_update_jobs/repository.py:537`

- Classe: `<module>`
- Função: `_lease_from_row`
- Chamada: `TelegramUpdateJobLease`
- Termos: `['lease']`

```python
TelegramUpdateJobLease(update_id=int(row['update_id']), attempt_count=int(row['attempt_count']), max_attempts=int(row['max_attempts']), payload_version=int(row['payload_version']), payload_ciphertext=bytes(row['payload_ciphertext']), payload_nonce=bytes(row['payload_nonce']), payload_key_id=str(row['payload_key_id']), lock_token=str(row['lock_token']))
```

### 67. `src/services/telegram_update_jobs/repository.py:782`

- Classe: `<module>`
- Função: `claim_next_telegram_update_job`
- Chamada: `_lease_from_row`
- Termos: `['lease']`

```python
_lease_from_row(row)
```

### 68. `src/services/telegram_update_jobs/runner.py:535`

- Classe: `<module>`
- Função: `_finalize_failure`
- Chamada: `calculate_worker_retry_delay_seconds`
- Termos: `['retry', 'worker']`

```python
calculate_worker_retry_delay_seconds(attempt_count=lease.job_attempt_count, config=config)
```

### 69. `src/services/telegram_update_jobs/runner.py:544`

- Classe: `<module>`
- Função: `_finalize_failure`
- Chamada: `dependencies.fail`
- Termos: `['fail']`

```python
dependencies.fail(lease, error_code=normalized_error, retry_delay_seconds=retry_delay, force_dead_letter=force_dead_letter)
```

### 70. `src/services/telegram_update_jobs/runner.py:559`

- Classe: `<module>`
- Função: `_finalize_failure`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='ownership_lost', stage='failure', error_code=normalized_error)
```

### 71. `src/services/telegram_update_jobs/runner.py:570`

- Classe: `<module>`
- Função: `_finalize_failure`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='unavailable', stage='failure', error_code=normalized_error)
```

### 72. `src/services/telegram_update_jobs/runner.py:583`

- Classe: `<module>`
- Função: `_finalize_failure`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='consistency_error', stage='failure', error_code=normalized_error)
```

### 73. `src/services/telegram_update_jobs/runner.py:591`

- Classe: `<module>`
- Função: `_finalize_failure`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='unavailable', stage='failure', error_code=normalized_error)
```

### 74. `src/services/telegram_update_jobs/runner.py:613`

- Classe: `<module>`
- Função: `_finalize_failure`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='retry_scheduled', stage='failure', job_status='queued', error_code=normalized_error, idempotent_replay=replay)
```

### 75. `src/services/telegram_update_jobs/runner.py:623`

- Classe: `<module>`
- Função: `_finalize_failure`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='dead_lettered', stage='failure', job_status='dead_letter', error_code=normalized_error, idempotent_replay=replay)
```

### 76. `src/services/telegram_update_jobs/runner.py:632`

- Classe: `<module>`
- Função: `_finalize_failure`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='consistency_error', stage='failure', error_code=normalized_error)
```

### 77. `src/services/telegram_update_jobs/runner.py:672`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `TelegramUpdateWorkerConfig`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConfig()
```

### 78. `src/services/telegram_update_jobs/runner.py:677`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `TelegramUpdateWorkerDependencies`
- Termos: `['worker']`

```python
TelegramUpdateWorkerDependencies()
```

### 79. `src/services/telegram_update_jobs/runner.py:681`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `resolved_dependencies.claim`
- Termos: `['claim']`

```python
resolved_dependencies.claim(lease_seconds=resolved_config.lease_seconds)
```

### 80. `src/services/telegram_update_jobs/runner.py:741`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_finalize_failure`
- Termos: `['fail']`

```python
_finalize_failure(lease=lease, dependencies=resolved_dependencies, config=resolved_config, error_code='telegram.keyring_unavailable', force_dead_letter=False)
```

### 81. `src/services/telegram_update_jobs/runner.py:759`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_finalize_failure`
- Termos: `['fail']`

```python
_finalize_failure(lease=lease, dependencies=resolved_dependencies, config=resolved_config, error_code='telegram.payload_invalid', force_dead_letter=True)
```

### 82. `src/services/telegram_update_jobs/runner.py:775`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='consistency_error', stage='decrypt', error_code='telegram.lease_invalid')
```

### 83. `src/services/telegram_update_jobs/runner.py:785`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_finalize_failure`
- Termos: `['fail']`

```python
_finalize_failure(lease=lease, dependencies=resolved_dependencies, config=resolved_config, error_code='telegram.decrypt_failed', force_dead_letter=False)
```

### 84. `src/services/telegram_update_jobs/runner.py:804`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_finalize_failure`
- Termos: `['fail']`

```python
_finalize_failure(lease=lease, dependencies=resolved_dependencies, config=resolved_config, error_code='telegram.payload_invalid', force_dead_letter=True)
```

### 85. `src/services/telegram_update_jobs/runner.py:833`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_finalize_failure`
- Termos: `['fail']`

```python
_finalize_failure(lease=lease, dependencies=resolved_dependencies, config=resolved_config, error_code='telegram.async_processor_unsupported', force_dead_letter=True)
```

### 86. `src/services/telegram_update_jobs/runner.py:848`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_finalize_failure`
- Termos: `['fail']`

```python
_finalize_failure(lease=lease, dependencies=resolved_dependencies, config=resolved_config, error_code=error.error_code, force_dead_letter=True)
```

### 87. `src/services/telegram_update_jobs/runner.py:861`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_finalize_failure`
- Termos: `['fail']`

```python
_finalize_failure(lease=lease, dependencies=resolved_dependencies, config=resolved_config, error_code=error.error_code, force_dead_letter=False)
```

### 88. `src/services/telegram_update_jobs/runner.py:872`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_finalize_failure`
- Termos: `['fail']`

```python
_finalize_failure(lease=lease, dependencies=resolved_dependencies, config=resolved_config, error_code='telegram.processing_failed', force_dead_letter=False)
```

### 89. `src/services/telegram_update_jobs/runner.py:888`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_finalize_failure`
- Termos: `['fail']`

```python
_finalize_failure(lease=lease, dependencies=resolved_dependencies, config=resolved_config, error_code='telegram.processing_failed', force_dead_letter=False)
```

### 90. `src/services/telegram_update_jobs/runner.py:902`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `resolved_dependencies.complete`
- Termos: `['complete']`

```python
resolved_dependencies.complete(lease)
```

### 91. `src/services/telegram_update_jobs/runner.py:911`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='ownership_lost', stage='complete', error_code='telegram.completion_ownership_lost')
```

### 92. `src/services/telegram_update_jobs/runner.py:924`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='unavailable', stage='complete', error_code='telegram.completion_unavailable')
```

### 93. `src/services/telegram_update_jobs/runner.py:939`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='consistency_error', stage='complete', error_code='telegram.completion_inconsistent')
```

### 94. `src/services/telegram_update_jobs/runner.py:949`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='unavailable', stage='complete', error_code='telegram.completion_unavailable')
```

### 95. `src/services/telegram_update_jobs/runner.py:963`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='consistency_error', stage='complete', error_code='telegram.completion_inconsistent')
```

### 96. `src/services/telegram_update_jobs/runner.py:972`

- Classe: `<module>`
- Função: `run_one_telegram_update_job`
- Chamada: `_result_for_lease`
- Termos: `['lease']`

```python
_result_for_lease(lease=lease, decision='completed', stage='complete', job_status='completed', idempotent_replay=bool(getattr(outcome, 'idempotent_replay', False)))
```

### 97. `src/services/telegram_update_jobs/runner.py:998`

- Classe: `<module>`
- Função: `_notify_safely`
- Chamada: `callback`
- Termos: `['ack']`

```python
callback(result)
```

### 98. `src/services/telegram_update_jobs/runner.py:1048`

- Classe: `<module>`
- Função: `run_telegram_update_worker`
- Chamada: `TelegramUpdateWorkerConfig`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConfig()
```

### 99. `src/services/telegram_update_jobs/runner.py:1053`

- Classe: `<module>`
- Função: `run_telegram_update_worker`
- Chamada: `TelegramUpdateWorkerDependencies`
- Termos: `['worker']`

```python
TelegramUpdateWorkerDependencies()
```

### 100. `src/services/telegram_update_jobs/runner.py:1118`

- Classe: `<module>`
- Função: `run_telegram_update_worker`
- Chamada: `resolved_dependencies.recover`
- Termos: `['recover']`

```python
resolved_dependencies.recover(limit=resolved_config.recovery_batch_size)
```

### 101. `src/services/telegram_update_jobs/worker.py:251`

- Classe: `<module>`
- Função: `_validate_integer`
- Chamada: `TelegramUpdateWorkerValidationError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerValidationError(f'{field_name} inválido.')
```

### 102. `src/services/telegram_update_jobs/worker.py:268`

- Classe: `<module>`
- Função: `_validate_sha256`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError(f'{field_name} inválido.')
```

### 103. `src/services/telegram_update_jobs/worker.py:283`

- Classe: `<module>`
- Função: `_validate_key_id`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('payload_key_id inválido.')
```

### 104. `src/services/telegram_update_jobs/worker.py:305`

- Classe: `<module>`
- Função: `_validate_bytes`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError(f'{field_name} inválido.')
```

### 105. `src/services/telegram_update_jobs/worker.py:318`

- Classe: `<module>`
- Função: `_validate_bytes`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError(f'{field_name} inválido.')
```

### 106. `src/services/telegram_update_jobs/worker.py:358`

- Classe: `<module>`
- Função: `_candidate_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou um receipt inválido.')
```

### 107. `src/services/telegram_update_jobs/worker.py:371`

- Classe: `<module>`
- Função: `_candidate_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou um receipt inválido.')
```

### 108. `src/services/telegram_update_jobs/worker.py:375`

- Classe: `<module>`
- Função: `_candidate_from_row`
- Chamada: `_ReceiptCandidate`
- Termos: `['receipt']`

```python
_ReceiptCandidate(update_id=update_id, receipt_status=receipt_status, receipt_attempt_count=receipt_attempt_count)
```

### 109. `src/services/telegram_update_jobs/worker.py:467`

- Classe: `<module>`
- Função: `_worker_lease_from_rows`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou um lease inválido.')
```

### 110. `src/services/telegram_update_jobs/worker.py:476`

- Classe: `<module>`
- Função: `_worker_lease_from_rows`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('Job e receipt pertencem a updates diferentes.')
```

### 111. `src/services/telegram_update_jobs/worker.py:488`

- Classe: `<module>`
- Função: `_worker_lease_from_rows`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('Tentativas ou versão inválidas.')
```

### 112. `src/services/telegram_update_jobs/worker.py:493`

- Classe: `<module>`
- Função: `_worker_lease_from_rows`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('Receipt não foi transferido ao worker.')
```

### 113. `src/services/telegram_update_jobs/worker.py:499`

- Classe: `<module>`
- Função: `_worker_lease_from_rows`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('Tentativas do receipt inválidas.')
```

### 114. `src/services/telegram_update_jobs/worker.py:504`

- Classe: `<module>`
- Função: `_worker_lease_from_rows`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('Tentativas do receipt estão atrás do job.')
```

### 115. `src/services/telegram_update_jobs/worker.py:510`

- Classe: `<module>`
- Função: `_worker_lease_from_rows`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('A propriedade do job e do receipt não coincide.')
```

### 116. `src/services/telegram_update_jobs/worker.py:515`

- Classe: `<module>`
- Função: `_worker_lease_from_rows`
- Chamada: `TelegramUpdateWorkerLease`
- Termos: `['lease', 'worker']`

```python
TelegramUpdateWorkerLease(update_id=candidate.update_id, job_status='processing', receipt_status='processing', job_attempt_count=job_attempt_count, job_max_attempts=job_max_attempts, receipt_attempt_count=receipt_attempt_count, payload_version=payload_version, payload_key_id=payload_key_id, payload_ciphertext=payload_ciphertext, payload_nonce=payload_nonce, lock_token=lock_token)
```

### 117. `src/services/telegram_update_jobs/worker.py:573`

- Classe: `<module>`
- Função: `claim_next_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerUnavailableError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerUnavailableError('Não foi possível gerar a propriedade do worker.')
```

### 118. `src/services/telegram_update_jobs/worker.py:585`

- Classe: `<module>`
- Função: `claim_next_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerUnavailableError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerUnavailableError('Não foi possível gerar a propriedade do worker.')
```

### 119. `src/services/telegram_update_jobs/worker.py:633`

- Classe: `<module>`
- Função: `claim_next_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O job deixou de estar disponível durante o claim.')
```

### 120. `src/services/telegram_update_jobs/worker.py:650`

- Classe: `<module>`
- Função: `claim_next_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou tentativas do job inválidas.')
```

### 121. `src/services/telegram_update_jobs/worker.py:678`

- Classe: `<module>`
- Função: `claim_next_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O receipt não pôde ser transferido ao worker.')
```

### 122. `src/services/telegram_update_jobs/worker.py:684`

- Classe: `<module>`
- Função: `claim_next_authenticated_telegram_update_job_atomic`
- Chamada: `_worker_lease_from_rows`
- Termos: `['lease', 'worker']`

```python
_worker_lease_from_rows(candidate=candidate, job_row=job_row, receipt_row=receipt_row)
```

### 123. `src/services/telegram_update_jobs/worker.py:697`

- Classe: `<module>`
- Função: `claim_next_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerUnavailableError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerUnavailableError('Não foi possível obter um job Telegram.')
```

### 124. `src/services/telegram_update_jobs/worker.py:968`

- Classe: `<module>`
- Função: `_validate_completion_lease`
- Chamada: `TelegramUpdateWorkerValidationError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerValidationError('Lease do worker inválido.')
```

### 125. `src/services/telegram_update_jobs/worker.py:982`

- Classe: `<module>`
- Função: `_validate_completion_lease`
- Chamada: `TelegramUpdateWorkerValidationError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerValidationError('O job não está em processamento.')
```

### 126. `src/services/telegram_update_jobs/worker.py:987`

- Classe: `<module>`
- Função: `_validate_completion_lease`
- Chamada: `TelegramUpdateWorkerValidationError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerValidationError('O receipt não está em processamento.')
```

### 127. `src/services/telegram_update_jobs/worker.py:1016`

- Classe: `<module>`
- Função: `_validate_completion_lease`
- Chamada: `TelegramUpdateWorkerValidationError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerValidationError('As tentativas do job são inválidas.')
```

### 128. `src/services/telegram_update_jobs/worker.py:1024`

- Classe: `<module>`
- Função: `_validate_completion_lease`
- Chamada: `TelegramUpdateWorkerValidationError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerValidationError('As tentativas do receipt estão atrasadas.')
```

### 129. `src/services/telegram_update_jobs/worker.py:1046`

- Classe: `<module>`
- Função: `_validate_completion_lease`
- Chamada: `TelegramUpdateWorkerValidationError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerValidationError('payload_key_id inválido.')
```

### 130. `src/services/telegram_update_jobs/worker.py:1060`

- Classe: `<module>`
- Função: `_validate_completion_lease`
- Chamada: `TelegramUpdateWorkerValidationError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerValidationError('lock_token inválido.')
```

### 131. `src/services/telegram_update_jobs/worker.py:1096`

- Classe: `<module>`
- Função: `_owned_receipt_completion_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou um receipt inválido.')
```

### 132. `src/services/telegram_update_jobs/worker.py:1113`

- Classe: `<module>`
- Função: `_owned_receipt_completion_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou um receipt inválido.')
```

### 133. `src/services/telegram_update_jobs/worker.py:1117`

- Classe: `<module>`
- Função: `_owned_receipt_completion_from_row`
- Chamada: `_OwnedReceiptCompletionSnapshot`
- Termos: `['receipt']`

```python
_OwnedReceiptCompletionSnapshot(update_id=update_id, status=status, attempt_count=attempt_count, claim_token=claim_token, lease_active=lease_active)
```

### 134. `src/services/telegram_update_jobs/worker.py:1130`

- Classe: `<module>`
- Função: `_completed_job_from_row`
- Chamada: `_CompletedJobSnapshot`
- Termos: `['complete']`

```python
_CompletedJobSnapshot(update_id=int(row['update_id']), status=str(row['status']), attempt_count=int(row['attempt_count']), max_attempts=int(row['max_attempts']), payload_version=int(row['payload_version']), payload_cleared=bool(row['payload_cleared']), ownership_cleared=bool(row['ownership_cleared']), completed_at_set=bool(row['completed_at_set']))
```

### 135. `src/services/telegram_update_jobs/worker.py:1162`

- Classe: `<module>`
- Função: `_completed_job_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou um job concluído inválido.')
```

### 136. `src/services/telegram_update_jobs/worker.py:1179`

- Classe: `<module>`
- Função: `_completed_job_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O job não foi concluído de forma consistente.')
```

### 137. `src/services/telegram_update_jobs/worker.py:1192`

- Classe: `<module>`
- Função: `_completed_receipt_from_row`
- Chamada: `_CompletedReceiptSnapshot`
- Termos: `['complete', 'receipt']`

```python
_CompletedReceiptSnapshot(update_id=int(row['update_id']), status=str(row['status']), attempt_count=int(row['attempt_count']), completed_at_set=bool(row['completed_at_set']), lease_closed=bool(row['lease_closed']))
```

### 138. `src/services/telegram_update_jobs/worker.py:1216`

- Classe: `<module>`
- Função: `_completed_receipt_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou um receipt concluído inválido.')
```

### 139. `src/services/telegram_update_jobs/worker.py:1228`

- Classe: `<module>`
- Função: `_completed_receipt_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O receipt não foi concluído de forma consistente.')
```

### 140. `src/services/telegram_update_jobs/worker.py:1251`

- Classe: `<module>`
- Função: `_validate_completed_job_matches_lease`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O job concluído pertence a outro update.')
```

### 141. `src/services/telegram_update_jobs/worker.py:1260`

- Classe: `<module>`
- Função: `_validate_completed_job_matches_lease`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('A tentativa concluída não corresponde ao lease.')
```

### 142. `src/services/telegram_update_jobs/worker.py:1269`

- Classe: `<module>`
- Função: `_validate_completed_job_matches_lease`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O limite de tentativas do job não corresponde ao lease.')
```

### 143. `src/services/telegram_update_jobs/worker.py:1278`

- Classe: `<module>`
- Função: `_validate_completed_job_matches_lease`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('A versão do payload não corresponde ao lease.')
```

### 144. `src/services/telegram_update_jobs/worker.py:1290`

- Classe: `<module>`
- Função: `_build_completion_outcome`
- Chamada: `_validate_completed_job_matches_lease`
- Termos: `['complete', 'lease']`

```python
_validate_completed_job_matches_lease(lease=lease, job=job)
```

### 145. `src/services/telegram_update_jobs/worker.py:1299`

- Classe: `<module>`
- Função: `_build_completion_outcome`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O job concluído pertence a outro update.')
```

### 146. `src/services/telegram_update_jobs/worker.py:1308`

- Classe: `<module>`
- Função: `_build_completion_outcome`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('A tentativa concluída não corresponde ao lease.')
```

### 147. `src/services/telegram_update_jobs/worker.py:1313`

- Classe: `<module>`
- Função: `_build_completion_outcome`
- Chamada: `TelegramUpdateWorkerCompletionOutcome`
- Termos: `['worker']`

```python
TelegramUpdateWorkerCompletionOutcome(update_id=lease.update_id, decision=decision, job_status='completed', receipt_status='completed', job_attempt_count=job.attempt_count, job_max_attempts=job.max_attempts, receipt_attempt_count=receipt_attempt_count, payload_cleared=job.payload_cleared, ownership_cleared=job.ownership_cleared)
```

### 148. `src/services/telegram_update_jobs/worker.py:1350`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `_validate_completion_lease`
- Termos: `['lease']`

```python
_validate_completion_lease(lease)
```

### 149. `src/services/telegram_update_jobs/worker.py:1385`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O receipt do worker não foi localizado.')
```

### 150. `src/services/telegram_update_jobs/worker.py:1391`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `_owned_receipt_completion_from_row`
- Termos: `['receipt']`

```python
_owned_receipt_completion_from_row(receipt_row)
```

### 151. `src/services/telegram_update_jobs/worker.py:1400`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O receipt pertence a outro update.')
```

### 152. `src/services/telegram_update_jobs/worker.py:1409`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O worker não possui mais o receipt.')
```

### 153. `src/services/telegram_update_jobs/worker.py:1433`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('Receipt concluído sem job correspondente.')
```

### 154. `src/services/telegram_update_jobs/worker.py:1440`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `_completed_job_from_row`
- Termos: `['complete']`

```python
_completed_job_from_row(completed_job_row)
```

### 155. `src/services/telegram_update_jobs/worker.py:1459`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O receipt não está mais em processamento.')
```

### 156. `src/services/telegram_update_jobs/worker.py:1465`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O lease do receipt expirou.')
```

### 157. `src/services/telegram_update_jobs/worker.py:1479`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O lease do job não está mais ativo.')
```

### 158. `src/services/telegram_update_jobs/worker.py:1485`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `_completed_job_from_row`
- Termos: `['complete']`

```python
_completed_job_from_row(completed_job_row)
```

### 159. `src/services/telegram_update_jobs/worker.py:1490`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `_validate_completed_job_matches_lease`
- Termos: `['complete', 'lease']`

```python
_validate_completed_job_matches_lease(lease=normalized_lease, job=completed_job)
```

### 160. `src/services/telegram_update_jobs/worker.py:1505`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O receipt não pôde ser concluído.')
```

### 161. `src/services/telegram_update_jobs/worker.py:1511`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `_completed_receipt_from_row`
- Termos: `['complete', 'receipt']`

```python
_completed_receipt_from_row(completed_receipt_row)
```

### 162. `src/services/telegram_update_jobs/worker.py:1520`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O receipt concluído pertence a outro update.')
```

### 163. `src/services/telegram_update_jobs/worker.py:1529`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('As tentativas do receipt estão atrás do job.')
```

### 164. `src/services/telegram_update_jobs/worker.py:1552`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerUnavailableError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerUnavailableError('Não foi possível concluir o job Telegram.')
```

### 165. `src/services/telegram_update_jobs/worker.py:1933`

- Classe: `<module>`
- Função: `_validate_worker_error_code`
- Chamada: `TelegramUpdateWorkerValidationError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerValidationError('error_code inválido.')
```

### 166. `src/services/telegram_update_jobs/worker.py:1941`

- Classe: `<module>`
- Função: `_validate_worker_error_code`
- Chamada: `WORKER_ERROR_CODE_PATTERN.fullmatch`
- Termos: `['worker']`

```python
WORKER_ERROR_CODE_PATTERN.fullmatch(normalized)
```

### 167. `src/services/telegram_update_jobs/worker.py:1946`

- Classe: `<module>`
- Função: `_validate_worker_error_code`
- Chamada: `TelegramUpdateWorkerValidationError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerValidationError('error_code inválido.')
```

### 168. `src/services/telegram_update_jobs/worker.py:1962`

- Classe: `<module>`
- Função: `_validate_boolean`
- Chamada: `TelegramUpdateWorkerValidationError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerValidationError(f'{field_name} inválido.')
```

### 169. `src/services/telegram_update_jobs/worker.py:2009`

- Classe: `<module>`
- Função: `_failure_receipt_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou um receipt de falha inválido.')
```

### 170. `src/services/telegram_update_jobs/worker.py:2027`

- Classe: `<module>`
- Função: `_failure_receipt_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou um receipt de falha inválido.')
```

### 171. `src/services/telegram_update_jobs/worker.py:2034`

- Classe: `<module>`
- Função: `_failure_receipt_from_row`
- Chamada: `WORKER_ERROR_CODE_PATTERN.fullmatch`
- Termos: `['worker']`

```python
WORKER_ERROR_CODE_PATTERN.fullmatch(last_error_code)
```

### 172. `src/services/telegram_update_jobs/worker.py:2039`

- Classe: `<module>`
- Função: `_failure_receipt_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O receipt contém error_code inválido.')
```

### 173. `src/services/telegram_update_jobs/worker.py:2043`

- Classe: `<module>`
- Função: `_failure_receipt_from_row`
- Chamada: `_FailureReceiptSnapshot`
- Termos: `['fail', 'receipt']`

```python
_FailureReceiptSnapshot(update_id=update_id, status=status, attempt_count=attempt_count, claim_token=claim_token, last_error_code=last_error_code, lease_active=lease_active)
```

### 174. `src/services/telegram_update_jobs/worker.py:2061`

- Classe: `<module>`
- Função: `_failed_job_from_row`
- Chamada: `_FailedJobSnapshot`
- Termos: `['fail']`

```python
_FailedJobSnapshot(update_id=int(row['update_id']), status=status, attempt_count=int(row['attempt_count']), max_attempts=int(row['max_attempts']), payload_version=int(row['payload_version']), last_error_code=str(row['last_error_code']), payload_retained=bool(row['payload_retained']), ownership_cleared=bool(row['ownership_cleared']), completed_at_cleared=bool(row['completed_at_cleared']), retry_state_valid=bool(row['retry_state_valid']), dead_letter_state_valid=bool(row['dead_letter_state_valid']))
```

### 175. `src/services/telegram_update_jobs/worker.py:2100`

- Classe: `<module>`
- Função: `_failed_job_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou um job de falha inválido.')
```

### 176. `src/services/telegram_update_jobs/worker.py:2109`

- Classe: `<module>`
- Função: `_failed_job_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O job retornou estado de falha inválido.')
```

### 177. `src/services/telegram_update_jobs/worker.py:2121`

- Classe: `<module>`
- Função: `_failed_job_from_row`
- Chamada: `WORKER_ERROR_CODE_PATTERN.fullmatch`
- Termos: `['worker']`

```python
WORKER_ERROR_CODE_PATTERN.fullmatch(snapshot.last_error_code)
```

### 178. `src/services/telegram_update_jobs/worker.py:2129`

- Classe: `<module>`
- Função: `_failed_job_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O job não foi finalizado de forma consistente.')
```

### 179. `src/services/telegram_update_jobs/worker.py:2141`

- Classe: `<module>`
- Função: `_failed_job_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O estado de retry é inconsistente.')
```

### 180. `src/services/telegram_update_jobs/worker.py:2152`

- Classe: `<module>`
- Função: `_failed_job_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O estado dead-letter é inconsistente.')
```

### 181. `src/services/telegram_update_jobs/worker.py:2163`

- Classe: `<module>`
- Função: `_failed_receipt_result_from_row`
- Chamada: `_FailedReceiptResult`
- Termos: `['fail', 'receipt']`

```python
_FailedReceiptResult(update_id=int(row['update_id']), status=str(row['status']), attempt_count=int(row['attempt_count']), last_error_code=str(row['last_error_code']), completed_at_cleared=bool(row['completed_at_cleared']), failed_at_set=bool(row['failed_at_set']), lease_closed=bool(row['lease_closed']))
```

### 182. `src/services/telegram_update_jobs/worker.py:2192`

- Classe: `<module>`
- Função: `_failed_receipt_result_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou um receipt falho inválido.')
```

### 183. `src/services/telegram_update_jobs/worker.py:2201`

- Classe: `<module>`
- Função: `_failed_receipt_result_from_row`
- Chamada: `WORKER_ERROR_CODE_PATTERN.fullmatch`
- Termos: `['worker']`

```python
WORKER_ERROR_CODE_PATTERN.fullmatch(result.last_error_code)
```

### 184. `src/services/telegram_update_jobs/worker.py:2209`

- Classe: `<module>`
- Função: `_failed_receipt_result_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O receipt não foi marcado como falho corretamente.')
```

### 185. `src/services/telegram_update_jobs/worker.py:2224`

- Classe: `<module>`
- Função: `_validate_failed_job_matches_lease`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O job de falha pertence a outro update.')
```

### 186. `src/services/telegram_update_jobs/worker.py:2233`

- Classe: `<module>`
- Função: `_validate_failed_job_matches_lease`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('A tentativa do job não corresponde ao lease.')
```

### 187. `src/services/telegram_update_jobs/worker.py:2242`

- Classe: `<module>`
- Função: `_validate_failed_job_matches_lease`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O limite de tentativas não corresponde ao lease.')
```

### 188. `src/services/telegram_update_jobs/worker.py:2251`

- Classe: `<module>`
- Função: `_validate_failed_job_matches_lease`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('A versão do payload não corresponde ao lease.')
```

### 189. `src/services/telegram_update_jobs/worker.py:2257`

- Classe: `<module>`
- Função: `_validate_failed_job_matches_lease`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O error_code persistido não confere.')
```

### 190. `src/services/telegram_update_jobs/worker.py:2271`

- Classe: `<module>`
- Função: `_build_failure_outcome`
- Chamada: `_validate_failed_job_matches_lease`
- Termos: `['fail', 'lease']`

```python
_validate_failed_job_matches_lease(lease=lease, job=job, error_code=error_code)
```

### 191. `src/services/telegram_update_jobs/worker.py:2278`

- Classe: `<module>`
- Função: `_build_failure_outcome`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('As tentativas do receipt estão atrás do job.')
```

### 192. `src/services/telegram_update_jobs/worker.py:2283`

- Classe: `<module>`
- Função: `_build_failure_outcome`
- Chamada: `TelegramUpdateWorkerFailureOutcome`
- Termos: `['fail', 'worker']`

```python
TelegramUpdateWorkerFailureOutcome(update_id=lease.update_id, decision=decision, job_status=job.status, receipt_status='failed', job_attempt_count=job.attempt_count, job_max_attempts=job.max_attempts, receipt_attempt_count=receipt_attempt_count, payload_version=job.payload_version, last_error_code=error_code, retry_delay_seconds=retry_delay_seconds, payload_retained=job.payload_retained, ownership_cleared=job.ownership_cleared)
```

### 193. `src/services/telegram_update_jobs/worker.py:2340`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `_validate_completion_lease`
- Termos: `['lease']`

```python
_validate_completion_lease(lease)
```

### 194. `src/services/telegram_update_jobs/worker.py:2346`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `_validate_worker_error_code`
- Termos: `['worker']`

```python
_validate_worker_error_code(error_code)
```

### 195. `src/services/telegram_update_jobs/worker.py:2415`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O receipt do worker não foi localizado.')
```

### 196. `src/services/telegram_update_jobs/worker.py:2421`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `_failure_receipt_from_row`
- Termos: `['fail', 'receipt']`

```python
_failure_receipt_from_row(receipt_row)
```

### 197. `src/services/telegram_update_jobs/worker.py:2430`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O receipt pertence a outro update.')
```

### 198. `src/services/telegram_update_jobs/worker.py:2439`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O worker não possui mais o receipt.')
```

### 199. `src/services/telegram_update_jobs/worker.py:2449`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O receipt já foi finalizado com outro error_code.')
```

### 200. `src/services/telegram_update_jobs/worker.py:2468`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('Receipt falho sem job correspondente.')
```

### 201. `src/services/telegram_update_jobs/worker.py:2474`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `_failed_job_from_row`
- Termos: `['fail']`

```python
_failed_job_from_row(existing_job_row)
```

### 202. `src/services/telegram_update_jobs/worker.py:2491`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `_build_failure_outcome`
- Termos: `['fail']`

```python
_build_failure_outcome(lease=normalized_lease, decision=replay_decision, job=existing_job, receipt_attempt_count=receipt.attempt_count, retry_delay_seconds=None, error_code=normalized_error)
```

### 203. `src/services/telegram_update_jobs/worker.py:2503`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O receipt não está mais em processamento.')
```

### 204. `src/services/telegram_update_jobs/worker.py:2509`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O lease do receipt expirou.')
```

### 205. `src/services/telegram_update_jobs/worker.py:2521`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O lease do job não está mais ativo.')
```

### 206. `src/services/telegram_update_jobs/worker.py:2526`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `_failed_job_from_row`
- Termos: `['fail']`

```python
_failed_job_from_row(failed_job_row)
```

### 207. `src/services/telegram_update_jobs/worker.py:2530`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `_validate_failed_job_matches_lease`
- Termos: `['fail', 'lease']`

```python
_validate_failed_job_matches_lease(lease=normalized_lease, job=failed_job, error_code=normalized_error)
```

### 208. `src/services/telegram_update_jobs/worker.py:2546`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerOwnershipError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerOwnershipError('O receipt não pôde ser marcado como falho.')
```

### 209. `src/services/telegram_update_jobs/worker.py:2552`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `_failed_receipt_result_from_row`
- Termos: `['fail', 'receipt']`

```python
_failed_receipt_result_from_row(failed_receipt_row)
```

### 210. `src/services/telegram_update_jobs/worker.py:2561`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O receipt falho pertence a outro update.')
```

### 211. `src/services/telegram_update_jobs/worker.py:2570`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O error_code do receipt não confere.')
```

### 212. `src/services/telegram_update_jobs/worker.py:2588`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `_build_failure_outcome`
- Termos: `['fail']`

```python
_build_failure_outcome(lease=normalized_lease, decision=decision, job=failed_job, receipt_attempt_count=failed_receipt.attempt_count, retry_delay_seconds=outcome_delay, error_code=normalized_error)
```

### 213. `src/services/telegram_update_jobs/worker.py:2610`

- Classe: `<module>`
- Função: `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- Chamada: `TelegramUpdateWorkerUnavailableError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerUnavailableError('Não foi possível finalizar a falha do job Telegram.')
```

### 214. `src/services/telegram_update_jobs/worker.py:2990`

- Classe: `<module>`
- Função: `_recovery_record_from_row`
- Chamada: `TelegramUpdateWorkerRecoveryRecord`
- Termos: `['recover', 'worker']`

```python
TelegramUpdateWorkerRecoveryRecord(update_id=int(row['update_id']), job_status=status, job_attempt_count=int(row['attempt_count']), job_max_attempts=int(row['max_attempts']), receipt_attempt_count=int(row['receipt_attempt_count']), payload_version=int(row['payload_version']), last_error_code=str(row['last_error_code']), payload_retained=bool(row['payload_retained']), ownership_cleared=bool(row['ownership_cleared']))
```

### 215. `src/services/telegram_update_jobs/worker.py:3038`

- Classe: `<module>`
- Função: `_recovery_record_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou recuperação Telegram inválida.')
```

### 216. `src/services/telegram_update_jobs/worker.py:3047`

- Classe: `<module>`
- Função: `_recovery_record_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('A recuperação retornou status inválido.')
```

### 217. `src/services/telegram_update_jobs/worker.py:3069`

- Classe: `<module>`
- Função: `_recovery_record_from_row`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('Job e receipt não foram recuperados consistentemente.')
```

### 218. `src/services/telegram_update_jobs/worker.py:3120`

- Classe: `<module>`
- Função: `recover_expired_authenticated_telegram_update_jobs_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco não retornou o resumo da recuperação.')
```

### 219. `src/services/telegram_update_jobs/worker.py:3154`

- Classe: `<module>`
- Função: `recover_expired_authenticated_telegram_update_jobs_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('O banco retornou resumo de recuperação inválido.')
```

### 220. `src/services/telegram_update_jobs/worker.py:3169`

- Classe: `<module>`
- Função: `recover_expired_authenticated_telegram_update_jobs_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('A recuperação de jobs e receipts ficou divergente.')
```

### 221. `src/services/telegram_update_jobs/worker.py:3178`

- Classe: `<module>`
- Função: `recover_expired_authenticated_telegram_update_jobs_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('A lista de recuperação é inválida.')
```

### 222. `src/services/telegram_update_jobs/worker.py:3184`

- Classe: `<module>`
- Função: `recover_expired_authenticated_telegram_update_jobs_atomic`
- Chamada: `_recovery_record_from_row`
- Termos: `['recover']`

```python
_recovery_record_from_row(row)
```

### 223. `src/services/telegram_update_jobs/worker.py:3191`

- Classe: `<module>`
- Função: `recover_expired_authenticated_telegram_update_jobs_atomic`
- Chamada: `TelegramUpdateWorkerConsistencyError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerConsistencyError('A quantidade recuperada não corresponde ao resumo.')
```

### 224. `src/services/telegram_update_jobs/worker.py:3197`

- Classe: `<module>`
- Função: `recover_expired_authenticated_telegram_update_jobs_atomic`
- Chamada: `TelegramUpdateWorkerRecoveryBatch`
- Termos: `['recover', 'worker']`

```python
TelegramUpdateWorkerRecoveryBatch(records=records)
```

### 225. `src/services/telegram_update_jobs/worker.py:3209`

- Classe: `<module>`
- Função: `recover_expired_authenticated_telegram_update_jobs_atomic`
- Chamada: `TelegramUpdateWorkerUnavailableError`
- Termos: `['worker']`

```python
TelegramUpdateWorkerUnavailableError('Não foi possível recuperar leases Telegram expirados.')
```

### 226. `src/services/telegram_update_receipts/repository.py:323`

- Classe: `<module>`
- Função: `_validar_attempt_count`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('O banco retornou attempt_count inválido.')
```

### 227. `src/services/telegram_update_receipts/repository.py:343`

- Classe: `<module>`
- Função: `_extrair_update_id`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('O banco retornou update_id inválido.')
```

### 228. `src/services/telegram_update_receipts/repository.py:358`

- Classe: `<module>`
- Função: `_extrair_status_banco`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('O banco retornou status inválido.')
```

### 229. `src/services/telegram_update_receipts/repository.py:367`

- Classe: `<module>`
- Função: `_extrair_status_banco`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('O banco retornou status inválido.')
```

### 230. `src/services/telegram_update_receipts/repository.py:396`

- Classe: `<module>`
- Função: `_resultado_claim`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('O banco retornou receipt inválido.')
```

### 231. `src/services/telegram_update_receipts/repository.py:400`

- Classe: `<module>`
- Função: `_resultado_claim`
- Chamada: `TelegramUpdateClaimResult`
- Termos: `['claim']`

```python
TelegramUpdateClaimResult(update_id=_extrair_update_id(row), status=status, attempt_count=attempt_count, claim_token=claim_token)
```

### 232. `src/services/telegram_update_receipts/repository.py:425`

- Classe: `<module>`
- Função: `_resultado_lifecycle`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('O banco retornou transição inválida.')
```

### 233. `src/services/telegram_update_receipts/repository.py:440`

- Classe: `<module>`
- Função: `_resultado_lifecycle`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('O banco retornou receipt inválido.')
```

### 234. `src/services/telegram_update_receipts/repository.py:444`

- Classe: `<module>`
- Função: `_resultado_lifecycle`
- Chamada: `TelegramUpdateLifecycleResult`
- Termos: `['cycle']`

```python
TelegramUpdateLifecycleResult(update_id=_extrair_update_id(row), status=expected_status, attempt_count=attempt_count)
```

### 235. `src/services/telegram_update_receipts/repository.py:489`

- Classe: `<module>`
- Função: `claim_telegram_update`
- Chamada: `_validar_lease_seconds`
- Termos: `['lease']`

```python
_validar_lease_seconds(lease_seconds)
```

### 236. `src/services/telegram_update_receipts/repository.py:532`

- Classe: `<module>`
- Função: `claim_telegram_update`
- Chamada: `_resultado_claim`
- Termos: `['claim']`

```python
_resultado_claim(inserted, status='claimed', claim_token=normalized_claim_token)
```

### 237. `src/services/telegram_update_receipts/repository.py:553`

- Classe: `<module>`
- Função: `claim_telegram_update`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('Receipt não localizado após conflito de update_id.')
```

### 238. `src/services/telegram_update_receipts/repository.py:571`

- Classe: `<module>`
- Função: `claim_telegram_update`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('O banco retornou fingerprint inválido.')
```

### 239. `src/services/telegram_update_receipts/repository.py:604`

- Classe: `<module>`
- Função: `claim_telegram_update`
- Chamada: `_resultado_claim`
- Termos: `['claim']`

```python
_resultado_claim(existing, status='duplicate', claim_token=None)
```

### 240. `src/services/telegram_update_receipts/repository.py:630`

- Classe: `<module>`
- Função: `claim_telegram_update`
- Chamada: `_resultado_claim`
- Termos: `['claim']`

```python
_resultado_claim(existing, status='in_progress', claim_token=None)
```

### 241. `src/services/telegram_update_receipts/repository.py:645`

- Classe: `<module>`
- Função: `claim_telegram_update`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('Não foi possível recuperar o receipt Telegram.')
```

### 242. `src/services/telegram_update_receipts/repository.py:651`

- Classe: `<module>`
- Função: `claim_telegram_update`
- Chamada: `_resultado_claim`
- Termos: `['claim']`

```python
_resultado_claim(reclaimed, status='reclaimed', claim_token=normalized_claim_token)
```

### 243. `src/services/telegram_update_receipts/repository.py:666`

- Classe: `<module>`
- Função: `claim_telegram_update`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('Não foi possível registrar o update Telegram.')
```

### 244. `src/services/telegram_update_receipts/repository.py:721`

- Classe: `<module>`
- Função: `complete_telegram_update`
- Chamada: `TelegramUpdateClaimOwnershipError`
- Termos: `['claim']`

```python
TelegramUpdateClaimOwnershipError('O claim não está mais ativo.')
```

### 245. `src/services/telegram_update_receipts/repository.py:726`

- Classe: `<module>`
- Função: `complete_telegram_update`
- Chamada: `_resultado_lifecycle`
- Termos: `['cycle']`

```python
_resultado_lifecycle(row, expected_status='completed')
```

### 246. `src/services/telegram_update_receipts/repository.py:738`

- Classe: `<module>`
- Função: `complete_telegram_update`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('Não foi possível concluir o update Telegram.')
```

### 247. `src/services/telegram_update_receipts/repository.py:803`

- Classe: `<module>`
- Função: `fail_telegram_update`
- Chamada: `TelegramUpdateClaimOwnershipError`
- Termos: `['claim']`

```python
TelegramUpdateClaimOwnershipError('O claim não está mais ativo.')
```

### 248. `src/services/telegram_update_receipts/repository.py:808`

- Classe: `<module>`
- Função: `fail_telegram_update`
- Chamada: `_resultado_lifecycle`
- Termos: `['cycle']`

```python
_resultado_lifecycle(row, expected_status='failed')
```

### 249. `src/services/telegram_update_receipts/repository.py:820`

- Classe: `<module>`
- Função: `fail_telegram_update`
- Chamada: `TelegramUpdateReceiptRepositoryError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptRepositoryError('Não foi possível marcar a falha do update Telegram.')
```

### 250. `src/services/telegram_update_receipts/service.py:186`

- Classe: `<module>`
- Função: `_extract_update_id`
- Chamada: `TelegramUpdateReceiptValidationError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptValidationError('O update Telegram é inválido.')
```

### 251. `src/services/telegram_update_receipts/service.py:205`

- Classe: `<module>`
- Função: `serialize_telegram_update_canonical`
- Chamada: `TelegramUpdateReceiptValidationError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptValidationError('O update Telegram é inválido.')
```

### 252. `src/services/telegram_update_receipts/service.py:230`

- Classe: `<module>`
- Função: `serialize_telegram_update_canonical`
- Chamada: `TelegramUpdateReceiptValidationError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptValidationError('O update Telegram é inválido.')
```

### 253. `src/services/telegram_update_receipts/service.py:239`

- Classe: `<module>`
- Função: `serialize_telegram_update_canonical`
- Chamada: `TelegramUpdateReceiptValidationError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptValidationError('O update Telegram possui tamanho inválido.')
```

### 254. `src/services/telegram_update_receipts/service.py:268`

- Classe: `<module>`
- Função: `_generate_claim_token`
- Chamada: `TelegramUpdateReceiptServiceError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptServiceError('Não foi possível criar um lease seguro.')
```

### 255. `src/services/telegram_update_receipts/service.py:288`

- Classe: `<module>`
- Função: `claim_authenticated_telegram_update`
- Chamada: `TelegramUpdateReceiptValidationError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptValidationError('O update Telegram é inválido.')
```

### 256. `src/services/telegram_update_receipts/service.py:303`

- Classe: `<module>`
- Função: `claim_authenticated_telegram_update`
- Chamada: `_generate_claim_token`
- Termos: `['claim']`

```python
_generate_claim_token()
```

### 257. `src/services/telegram_update_receipts/service.py:308`

- Classe: `<module>`
- Função: `claim_authenticated_telegram_update`
- Chamada: `repository.claim_telegram_update`
- Termos: `['claim']`

```python
repository.claim_telegram_update(update_id=update_id, update_fingerprint=fingerprint, claim_token=claim_token, lease_seconds=lease_seconds)
```

### 258. `src/services/telegram_update_receipts/service.py:322`

- Classe: `<module>`
- Função: `claim_authenticated_telegram_update`
- Chamada: `TelegramUpdateReceiptValidationError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptValidationError('Não foi possível validar o claim do update Telegram.')
```

### 259. `src/services/telegram_update_receipts/service.py:331`

- Classe: `<module>`
- Função: `claim_authenticated_telegram_update`
- Chamada: `TelegramUpdateReceiptConflictError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptConflictError('O update Telegram conflita com um registro existente.')
```

### 260. `src/services/telegram_update_receipts/service.py:340`

- Classe: `<module>`
- Função: `claim_authenticated_telegram_update`
- Chamada: `TelegramUpdateReceiptUnavailableError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptUnavailableError('O controle de updates Telegram está temporariamente indisponível.')
```

### 261. `src/services/telegram_update_receipts/service.py:356`

- Classe: `<module>`
- Função: `claim_authenticated_telegram_update`
- Chamada: `TelegramUpdateReceiptServiceError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptServiceError('O repositório retornou um lease inválido.')
```

### 262. `src/services/telegram_update_receipts/service.py:360`

- Classe: `<module>`
- Função: `claim_authenticated_telegram_update`
- Chamada: `TelegramUpdateProcessingLease`
- Termos: `['lease']`

```python
TelegramUpdateProcessingLease(update_id=result.update_id, attempt_count=result.attempt_count, claim_token=claim_token, update_fingerprint=fingerprint)
```

### 263. `src/services/telegram_update_receipts/service.py:371`

- Classe: `<module>`
- Função: `claim_authenticated_telegram_update`
- Chamada: `TelegramUpdateClaimDecision`
- Termos: `['claim']`

```python
TelegramUpdateClaimDecision(update_id=result.update_id, status=result.status, attempt_count=result.attempt_count, lease=lease)
```

### 264. `src/services/telegram_update_receipts/service.py:388`

- Classe: `<module>`
- Função: `_validate_lease`
- Chamada: `TelegramUpdateReceiptValidationError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptValidationError('O lease Telegram é inválido.')
```

### 265. `src/services/telegram_update_receipts/service.py:403`

- Classe: `<module>`
- Função: `_validate_lease`
- Chamada: `TelegramUpdateReceiptValidationError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptValidationError('O lease Telegram é inválido.')
```

### 266. `src/services/telegram_update_receipts/service.py:410`

- Classe: `<module>`
- Função: `_validate_lease`
- Chamada: `TelegramUpdateReceiptValidationError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptValidationError('O lease Telegram é inválido.')
```

### 267. `src/services/telegram_update_receipts/service.py:417`

- Classe: `<module>`
- Função: `_validate_lease`
- Chamada: `TelegramUpdateReceiptValidationError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptValidationError('O lease Telegram é inválido.')
```

### 268. `src/services/telegram_update_receipts/service.py:428`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update`
- Chamada: `_validate_lease`
- Termos: `['lease']`

```python
_validate_lease(lease)
```

### 269. `src/services/telegram_update_receipts/service.py:435`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update`
- Chamada: `repository.complete_telegram_update`
- Termos: `['complete']`

```python
repository.complete_telegram_update(update_id=validated_lease.update_id, claim_token=validated_lease.claim_token)
```

### 270. `src/services/telegram_update_receipts/service.py:450`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update`
- Chamada: `TelegramUpdateReceiptOwnershipError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptOwnershipError('O lease Telegram não está mais ativo.')
```

### 271. `src/services/telegram_update_receipts/service.py:458`

- Classe: `<module>`
- Função: `complete_authenticated_telegram_update`
- Chamada: `TelegramUpdateReceiptUnavailableError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptUnavailableError('Não foi possível concluir o update Telegram.')
```

### 272. `src/services/telegram_update_receipts/service.py:480`

- Classe: `<module>`
- Função: `fail_authenticated_telegram_update`
- Chamada: `_validate_lease`
- Termos: `['lease']`

```python
_validate_lease(lease)
```

### 273. `src/services/telegram_update_receipts/service.py:493`

- Classe: `<module>`
- Função: `fail_authenticated_telegram_update`
- Chamada: `TelegramUpdateReceiptValidationError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptValidationError('O código de falha Telegram é inválido.')
```

### 274. `src/services/telegram_update_receipts/service.py:499`

- Classe: `<module>`
- Função: `fail_authenticated_telegram_update`
- Chamada: `repository.fail_telegram_update`
- Termos: `['fail']`

```python
repository.fail_telegram_update(update_id=validated_lease.update_id, claim_token=validated_lease.claim_token, error_code=error_code)
```

### 275. `src/services/telegram_update_receipts/service.py:515`

- Classe: `<module>`
- Função: `fail_authenticated_telegram_update`
- Chamada: `TelegramUpdateReceiptOwnershipError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptOwnershipError('O lease Telegram não está mais ativo.')
```

### 276. `src/services/telegram_update_receipts/service.py:523`

- Classe: `<module>`
- Função: `fail_authenticated_telegram_update`
- Chamada: `TelegramUpdateReceiptUnavailableError`
- Termos: `['receipt']`

```python
TelegramUpdateReceiptUnavailableError('Não foi possível registrar a falha do update Telegram.')
```

### 277. `src/tools/observability.py:137`

- Classe: `<module>`
- Função: `preparar_tabela_eventos_tools`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

### 278. `src/tools/observability.py:298`

- Classe: `<module>`
- Função: `registrar_evento_tool`
- Chamada: `conn.rollback`
- Termos: `['ack']`

```python
conn.rollback()
```

