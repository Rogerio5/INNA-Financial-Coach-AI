# F2H5-G6D1 — Contrato do resultado do runner

## Classe

- Módulo: `src.services.telegram_update_jobs.runner`
- Arquivo: `src/services/telegram_update_jobs/runner.py`
- Linha: 279
- Dataclass: `True`
- Assinatura: `(decision: 'RunnerDecision', stage: 'RunnerStage', update_id: 'int | None' = None, job_attempt_count: 'int | None' = None, job_max_attempts: 'int | None' = None, job_status: 'str | None' = None, error_code: 'str | None' = None, idempotent_replay: 'bool' = False) -> None`

## Campos

- `decision` — tipo `RunnerDecision`, default `<dataclasses._MISSING_TYPE object at 0x000001FF62A70EF0>`
- `stage` — tipo `RunnerStage`, default `<dataclasses._MISSING_TYPE object at 0x000001FF62A70EF0>`
- `update_id` — tipo `int | None`, default `None`
- `job_attempt_count` — tipo `int | None`, default `None`
- `job_max_attempts` — tipo `int | None`, default `None`
- `job_status` — tipo `str | None`, default `None`
- `error_code` — tipo `str | None`, default `None`
- `idempotent_replay` — tipo `bool`, default `False`

## Métodos

- `to_safe_dict(self) -> 'dict[str, object]'`

## Decisions literais

- `consistency_error`
- `idle`
- `unavailable`

## Stages literais

- `claim`
- `idle`
- `recovery`

## Códigos de erro literais

- `telegram.claim_inconsistent`
- `telegram.claim_unavailable`
- `telegram.recovery_unavailable`

## Construções do resultado

### 1. `src/services/telegram_update_jobs/runner.py:500`

- Função: `_result_for_lease`

```python
TelegramUpdateRunnerResult(decision=decision, stage=stage, update_id=lease.update_id, job_attempt_count=lease.job_attempt_count, job_max_attempts=lease.job_max_attempts, job_status=job_status, error_code=error_code, idempotent_replay=idempotent_replay)
```

### 2. `src/services/telegram_update_jobs/runner.py:692`

- Função: `run_one_telegram_update_job`

```python
TelegramUpdateRunnerResult(decision='unavailable', stage='claim', error_code='telegram.claim_unavailable')
```

### 3. `src/services/telegram_update_jobs/runner.py:706`

- Função: `run_one_telegram_update_job`

```python
TelegramUpdateRunnerResult(decision='consistency_error', stage='claim', error_code='telegram.claim_inconsistent')
```

### 4. `src/services/telegram_update_jobs/runner.py:715`

- Função: `run_one_telegram_update_job`

```python
TelegramUpdateRunnerResult(decision='unavailable', stage='claim', error_code='telegram.claim_unavailable')
```

### 5. `src/services/telegram_update_jobs/runner.py:724`

- Função: `run_one_telegram_update_job`

```python
TelegramUpdateRunnerResult(decision='idle', stage='idle')
```

### 6. `src/services/telegram_update_jobs/runner.py:1150`

- Função: `run_telegram_update_worker`

```python
TelegramUpdateRunnerResult(decision='unavailable', stage='recovery', error_code='telegram.recovery_unavailable')
```

## Serialização segura

```python
    def to_safe_dict(
        self,
    ) -> dict[str, object]:
        return {
            "decision": self.decision,
            "stage": self.stage,
            "update_id": self.update_id,
            "job_attempt_count": (
                self.job_attempt_count
            ),
            "job_max_attempts": (
                self.job_max_attempts
            ),
            "job_status": self.job_status,
            "error_code": self.error_code,
            "idempotent_replay": (
                self.idempotent_replay
            ),
        }
```

