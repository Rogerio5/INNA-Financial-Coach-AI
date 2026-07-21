# F2H5-H5A — Superfície FastAPI da INNA

## Resumo

- Arquivos analisados: 173
- Aplicações FastAPI: 1
- APIRouters: 2
- Rotas: 16
- Routers incluídos: 2
- Hooks de lifecycle: 0
- Candidatos de segurança: 64
- Rotas operacionais existentes: 1

## Aplicações FastAPI

- `api/main.py:290` — `app` com `FastAPI`

## Routers

- `api/resend_webhook.py:27` — `router`; prefixo `/webhooks`
- `api/telegram_webhook.py:71` — `router`; prefixo `/telegram`

## Routers incluídos

- `api/main.py:793` — `telegram_router`; prefixo `None`
- `api/main.py:794` — `resend_router`; prefixo `None`

## Rotas existentes

- `api/main.py:298` — `GET /` → `root`
- `api/main.py:308` — `GET /health` → `health_check`
- `api/main.py:619` — `POST /diagnostico` → `gerar_diagnostico`
- `api/main.py:642` — `POST /internal/telegram/diagnostico` → `gerar_diagnostico_telegram_interno`
- `api/main.py:714` — `POST /feedback` → `registrar_feedback`
- `api/main.py:732` — `GET /diagnosticos` → `listar_diagnosticos`
- `api/main.py:737` — `GET /feedbacks` → `listar_feedbacks`
- `api/main.py:742` — `GET /diagnosticos/{diagnostico_id}/relatorio` → `baixar_relatorio_diagnostico`
- `api/main.py:786` — `GET /diagnosticos/usuario/{nome}` → `listar_diagnosticos_por_usuario`
- `api/main.py:798` — `POST /diagnosticos/{diagnostico_id}/enviar-email` → `enviar_diagnostico_por_email`
- `api/main.py:967` — `POST /eventos` → `registrar_evento`
- `api/main.py:996` — `POST /rag/setup` → `rag_setup`
- `api/main.py:1040` — `GET /rag/search` → `rag_search`
- `api/main.py:1063` — `POST /rag/ask` → `rag_ask`
- `api/resend_webhook.py:34` — `POST /resend` → `receber_webhook_resend`
- `api/telegram_webhook.py:2302` — `POST /webhook` → `telegram_webhook`

## Lifecycle

- Nenhum hook identificado.

## Segurança e autenticação

- `src/context_engineering/token_budget.py:21` — `estimate_tokens`
- `src/context_engineering/token_budget.py:108` — `truncate_text_to_token_budget`
- `src/dashboard.py:2` — `normalizar_risco_admin`
- `src/observability/llm_costs.py:219` — `extrair_tokens_resposta`
- `src/rag_engine.py:88` — `tokenize`
- `src/services/telegram_conversation_state/contracts.py:103` — `_validate_integer`
- `src/services/telegram_conversation_state/contracts.py:146` — `validate_telegram_identity`
- `src/services/telegram_conversation_state/contracts.py:377` — `validate_state_ttl_seconds`
- `src/services/telegram_conversation_state/contracts.py:392` — `validate_expected_version`
- `src/services/telegram_conversation_state/contracts.py:402` — `validate_cleanup_limit`
- `src/services/telegram_conversation_state/contracts.py:413` — `_validate_datetime`
- `src/services/telegram_conversation_state/store.py:155` — `_validate_record_identity`
- `src/services/telegram_conversation_state/webhook_bridge.py:112` — `_validate_session`
- `src/services/telegram_observability/contracts.py:70` — `_validate_choice`
- `src/services/telegram_observability/contracts.py:86` — `_validate_duration`
- `src/services/telegram_observability/operational_http.py:207` — `_internal_runtime_payload`
- `src/services/telegram_observability/prometheus_exporter.py:53` — `_validate_metric_name`
- `src/services/telegram_observability/prometheus_exporter.py:71` — `_validate_label_name`
- `src/services/telegram_observability/readiness_runtime.py:19` — `_validate_non_negative_finite`
- `src/services/telegram_observability/readiness_runtime.py:180` — `invalidate`
- `src/services/telegram_update_jobs/execution.py:89` — `_validate_integer`
- `src/services/telegram_update_jobs/execution.py:109` — `_validate_bytes`
- `src/services/telegram_update_jobs/execution.py:144` — `_validate_worker_lease`
- `src/services/telegram_update_jobs/execution.py:486` — `decrypt_authenticated_telegram_worker_lease`
- `src/services/telegram_update_jobs/ingress.py:189` — `_validate_integer`
- `src/services/telegram_update_jobs/ingress.py:211` — `_validate_fingerprint`
- `src/services/telegram_update_jobs/ingress.py:228` — `_generate_claim_token`
- `src/services/telegram_update_jobs/ingress.py:581` — `enqueue_authenticated_telegram_update_atomic`
- `src/services/telegram_update_jobs/repository.py:365` — `_validate_integer`
- `src/services/telegram_update_jobs/repository.py:385` — `_validate_update_id`
- `src/services/telegram_update_jobs/repository.py:396` — `_validate_sha256`
- `src/services/telegram_update_jobs/repository.py:413` — `_validate_key_id`
- `src/services/telegram_update_jobs/repository.py:428` — `_validate_error_code`
- `src/services/telegram_update_jobs/repository.py:443` — `_validate_bytes`
- `src/services/telegram_update_jobs/runner.py:368` — `_validate_integer`
- `src/services/telegram_update_jobs/runner.py:388` — `_validate_positive_float`
- `src/services/telegram_update_jobs/runner.py:427` — `_validate_error_code`
- `src/services/telegram_update_jobs/service.py:96` — `_validate_key_id`
- `src/services/telegram_update_jobs/service.py:111` — `_validate_update_id`
- `src/services/telegram_update_jobs/service.py:127` — `_validate_integer`
- `src/services/telegram_update_jobs/service.py:147` — `_validate_bytes`
- `src/services/telegram_update_jobs/service.py:180` — `_validate_aes_key`
- `src/services/telegram_update_jobs/service.py:494` — `_build_authenticated_data`
- `src/services/telegram_update_jobs/service.py:525` — `encrypt_authenticated_telegram_update`
- `src/services/telegram_update_jobs/service.py:593` — `decrypt_authenticated_telegram_update`
- `src/services/telegram_update_jobs/service.py:717` — `generate_telegram_update_job_lock_token`
- `src/services/telegram_update_jobs/worker.py:238` — `_validate_integer`
- `src/services/telegram_update_jobs/worker.py:258` — `_validate_sha256`
- `src/services/telegram_update_jobs/worker.py:275` — `_validate_key_id`
- `src/services/telegram_update_jobs/worker.py:290` — `_validate_bytes`
- `src/services/telegram_update_jobs/worker.py:538` — `claim_next_authenticated_telegram_update_job_atomic`
- `src/services/telegram_update_jobs/worker.py:961` — `_validate_completion_lease`
- `src/services/telegram_update_jobs/worker.py:1237` — `_validate_completed_job_matches_lease`
- `src/services/telegram_update_jobs/worker.py:1336` — `complete_authenticated_telegram_update_job_atomic`
- `src/services/telegram_update_jobs/worker.py:1926` — `_validate_worker_error_code`
- `src/services/telegram_update_jobs/worker.py:1953` — `_validate_boolean`
- `src/services/telegram_update_jobs/worker.py:2217` — `_validate_failed_job_matches_lease`
- `src/services/telegram_update_jobs/worker.py:2313` — `retry_or_dead_letter_authenticated_telegram_update_job_atomic`
- `src/services/telegram_update_jobs/worker.py:3077` — `recover_expired_authenticated_telegram_update_jobs_atomic`
- `src/services/telegram_update_receipts/service.py:260` — `_generate_claim_token`
- `src/services/telegram_update_receipts/service.py:275` — `claim_authenticated_telegram_update`
- `src/services/telegram_update_receipts/service.py:381` — `_validate_lease`
- `src/services/telegram_update_receipts/service.py:424` — `complete_authenticated_telegram_update`
- `src/services/telegram_update_receipts/service.py:472` — `fail_authenticated_telegram_update`

## Rotas operacionais existentes

- `api/main.py:308` — `GET /health`
