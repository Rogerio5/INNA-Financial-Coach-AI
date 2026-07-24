# F2H5-G6D2 — Semântica das decisões do runner

## Tipos

### `RunnerDecision`

- Linha: 17
- Expressão: `Literal['idle', 'completed', 'retry_scheduled', 'dead_lettered', 'ownership_lost', 'unavailable', 'consistency_error']`
- Valores literais: `['completed', 'consistency_error', 'dead_lettered', 'idle', 'ownership_lost', 'retry_scheduled', 'unavailable']`

### `RunnerStage`

- Linha: 27
- Expressão: `Literal['idle', 'claim', 'decrypt', 'process', 'complete', 'failure', 'recovery']`
- Valores literais: `['claim', 'complete', 'decrypt', 'failure', 'idle', 'process', 'recovery']`

## Valores resolvidos

- Decisions: `['completed', 'consistency_error', 'dead_lettered', 'idle', 'ownership_lost', 'retry_scheduled', 'unavailable']`
- Stages: `['claim', 'complete', 'decrypt', 'failure', 'idle', 'process', 'recovery']`
- Job statuses: `['completed', 'dead_letter', 'queued']`

## `_result_for_lease`

- Linha: 491
- Parâmetros: `['lease', 'decision', 'stage', 'job_status', 'error_code', 'idempotent_replay']`

```python
def _result_for_lease(
    *,
    lease: Any,
    decision: RunnerDecision,
    stage: RunnerStage,
    job_status: str | None = None,
    error_code: str | None = None,
    idempotent_replay: bool = False,
) -> TelegramUpdateRunnerResult:
    return TelegramUpdateRunnerResult(
        decision=decision,
        stage=stage,
        update_id=lease.update_id,
        job_attempt_count=(
            lease.job_attempt_count
        ),
        job_max_attempts=(
            lease.job_max_attempts
        ),
        job_status=job_status,
        error_code=error_code,
        idempotent_replay=(
            idempotent_replay
        ),
    )
```

## Chamadas de `_result_for_lease`

### 1. Linha 632

- Função: `_finalize_failure`
- Parâmetros: `{'lease': 'lease', 'decision': "'consistency_error'", 'stage': "'failure'", 'error_code': 'normalized_error'}`

```python
_result_for_lease(lease=lease, decision='consistency_error', stage='failure', error_code=normalized_error)
```

### 2. Linha 972

- Função: `run_one_telegram_update_job`
- Parâmetros: `{'lease': 'lease', 'decision': "'completed'", 'stage': "'complete'", 'job_status': "'completed'", 'idempotent_replay': "bool(getattr(outcome, 'idempotent_replay', False))"}`

```python
_result_for_lease(lease=lease, decision='completed', stage='complete', job_status='completed', idempotent_replay=bool(getattr(outcome, 'idempotent_replay', False)))
```

### 3. Linha 613

- Função: `_finalize_failure`
- Parâmetros: `{'lease': 'lease', 'decision': "'retry_scheduled'", 'stage': "'failure'", 'job_status': "'queued'", 'error_code': 'normalized_error', 'idempotent_replay': 'replay'}`

```python
_result_for_lease(lease=lease, decision='retry_scheduled', stage='failure', job_status='queued', error_code=normalized_error, idempotent_replay=replay)
```

### 4. Linha 623

- Função: `_finalize_failure`
- Parâmetros: `{'lease': 'lease', 'decision': "'dead_lettered'", 'stage': "'failure'", 'job_status': "'dead_letter'", 'error_code': 'normalized_error', 'idempotent_replay': 'replay'}`

```python
_result_for_lease(lease=lease, decision='dead_lettered', stage='failure', job_status='dead_letter', error_code=normalized_error, idempotent_replay=replay)
```

### 5. Linha 963

- Função: `run_one_telegram_update_job`
- Parâmetros: `{'lease': 'lease', 'decision': "'consistency_error'", 'stage': "'complete'", 'error_code': "'telegram.completion_inconsistent'"}`

```python
_result_for_lease(lease=lease, decision='consistency_error', stage='complete', error_code='telegram.completion_inconsistent')
```

### 6. Linha 559

- Função: `_finalize_failure`
- Parâmetros: `{'lease': 'lease', 'decision': "'ownership_lost'", 'stage': "'failure'", 'error_code': 'normalized_error'}`

```python
_result_for_lease(lease=lease, decision='ownership_lost', stage='failure', error_code=normalized_error)
```

### 7. Linha 570

- Função: `_finalize_failure`
- Parâmetros: `{'lease': 'lease', 'decision': "'unavailable'", 'stage': "'failure'", 'error_code': 'normalized_error'}`

```python
_result_for_lease(lease=lease, decision='unavailable', stage='failure', error_code=normalized_error)
```

### 8. Linha 583

- Função: `_finalize_failure`
- Parâmetros: `{'lease': 'lease', 'decision': "'consistency_error'", 'stage': "'failure'", 'error_code': 'normalized_error'}`

```python
_result_for_lease(lease=lease, decision='consistency_error', stage='failure', error_code=normalized_error)
```

### 9. Linha 591

- Função: `_finalize_failure`
- Parâmetros: `{'lease': 'lease', 'decision': "'unavailable'", 'stage': "'failure'", 'error_code': 'normalized_error'}`

```python
_result_for_lease(lease=lease, decision='unavailable', stage='failure', error_code=normalized_error)
```

### 10. Linha 775

- Função: `run_one_telegram_update_job`
- Parâmetros: `{'lease': 'lease', 'decision': "'consistency_error'", 'stage': "'decrypt'", 'error_code': "'telegram.lease_invalid'"}`

```python
_result_for_lease(lease=lease, decision='consistency_error', stage='decrypt', error_code='telegram.lease_invalid')
```

### 11. Linha 911

- Função: `run_one_telegram_update_job`
- Parâmetros: `{'lease': 'lease', 'decision': "'ownership_lost'", 'stage': "'complete'", 'error_code': "'telegram.completion_ownership_lost'"}`

```python
_result_for_lease(lease=lease, decision='ownership_lost', stage='complete', error_code='telegram.completion_ownership_lost')
```

### 12. Linha 924

- Função: `run_one_telegram_update_job`
- Parâmetros: `{'lease': 'lease', 'decision': "'unavailable'", 'stage': "'complete'", 'error_code': "'telegram.completion_unavailable'"}`

```python
_result_for_lease(lease=lease, decision='unavailable', stage='complete', error_code='telegram.completion_unavailable')
```

### 13. Linha 939

- Função: `run_one_telegram_update_job`
- Parâmetros: `{'lease': 'lease', 'decision': "'consistency_error'", 'stage': "'complete'", 'error_code': "'telegram.completion_inconsistent'"}`

```python
_result_for_lease(lease=lease, decision='consistency_error', stage='complete', error_code='telegram.completion_inconsistent')
```

### 14. Linha 949

- Função: `run_one_telegram_update_job`
- Parâmetros: `{'lease': 'lease', 'decision': "'unavailable'", 'stage': "'complete'", 'error_code': "'telegram.completion_unavailable'"}`

```python
_result_for_lease(lease=lease, decision='unavailable', stage='complete', error_code='telegram.completion_unavailable')
```

## Construções diretas

### 1. Linha 500

- Função: `_result_for_lease`
- Parâmetros: `{'decision': 'decision', 'stage': 'stage', 'update_id': 'lease.update_id', 'job_attempt_count': 'lease.job_attempt_count', 'job_max_attempts': 'lease.job_max_attempts', 'job_status': 'job_status', 'error_code': 'error_code', 'idempotent_replay': 'idempotent_replay'}`

```python
TelegramUpdateRunnerResult(decision=decision, stage=stage, update_id=lease.update_id, job_attempt_count=lease.job_attempt_count, job_max_attempts=lease.job_max_attempts, job_status=job_status, error_code=error_code, idempotent_replay=idempotent_replay)
```

### 2. Linha 724

- Função: `run_one_telegram_update_job`
- Parâmetros: `{'decision': "'idle'", 'stage': "'idle'"}`

```python
TelegramUpdateRunnerResult(decision='idle', stage='idle')
```

### 3. Linha 692

- Função: `run_one_telegram_update_job`
- Parâmetros: `{'decision': "'unavailable'", 'stage': "'claim'", 'error_code': "'telegram.claim_unavailable'"}`

```python
TelegramUpdateRunnerResult(decision='unavailable', stage='claim', error_code='telegram.claim_unavailable')
```

### 4. Linha 706

- Função: `run_one_telegram_update_job`
- Parâmetros: `{'decision': "'consistency_error'", 'stage': "'claim'", 'error_code': "'telegram.claim_inconsistent'"}`

```python
TelegramUpdateRunnerResult(decision='consistency_error', stage='claim', error_code='telegram.claim_inconsistent')
```

### 5. Linha 715

- Função: `run_one_telegram_update_job`
- Parâmetros: `{'decision': "'unavailable'", 'stage': "'claim'", 'error_code': "'telegram.claim_unavailable'"}`

```python
TelegramUpdateRunnerResult(decision='unavailable', stage='claim', error_code='telegram.claim_unavailable')
```

### 6. Linha 1150

- Função: `run_telegram_update_worker`
- Parâmetros: `{'decision': "'unavailable'", 'stage': "'recovery'", 'error_code': "'telegram.recovery_unavailable'"}`

```python
TelegramUpdateRunnerResult(decision='unavailable', stage='recovery', error_code='telegram.recovery_unavailable')
```

## Replay idempotente

- Linha 972 — `run_one_telegram_update_job` — `bool(getattr(outcome, 'idempotent_replay', False))`
- Linha 613 — `_finalize_failure` — `replay`
- Linha 623 — `_finalize_failure` — `replay`

