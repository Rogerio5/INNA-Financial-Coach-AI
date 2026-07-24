# F2H5-H5A — Símbolos FastAPI em runtime

## `api.main`

- `app(scope: MutableMapping[str, Any], receive: Callable[[], Awaitable[MutableMapping[str, Any]]], send: Callable[[MutableMapping[str, Any]], Awaitable[NoneType]]) -> None` — FastAPI; definido em `fastapi.applications`
- `health_check()` — function; definido em `api.main`
- `resend_router(scope: 'Scope', receive: 'Receive', send: 'Send') -> 'None'` — APIRouter; definido em `fastapi.routing`
- `telegram_router(scope: 'Scope', receive: 'Receive', send: 'Send') -> 'None'` — APIRouter; definido em `fastapi.routing`

## `api.resend_webhook`

- `APIRouter(*, prefix: Annotated[str, Doc('An optional path prefix for the router.')] = '', tags: Annotated[Optional[List[Union[str, enum.Enum]]], Doc('\n                A list of tags to be applied to all the *path operations* in this\n                router.\n\n                It will be added to the generated OpenAPI (e.g. visible at `/docs`).\n\n                Read more about it in the\n                [FastAPI docs for Path Operation Configuration](https://fastapi.tiangolo.com/tutorial/path-operation-configuration/).\n                ')] = None, dependencies: Annotated[Optional[Sequence[fastapi.params.Depends]], Doc('\n                A list of dependencies (using `Depends()`) to be applied to all the\n                *path operations* in this router.\n\n                Read more about it in the\n                [FastAPI docs for Bigger Applications - Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-an-apirouter-with-a-custom-prefix-tags-responses-and-dependencies).\n                ')] = None, default_response_class: Annotated[Type[starlette.responses.Response], Doc('\n                The default response class to be used.\n\n                Read more in the\n                [FastAPI docs for Custom Response - HTML, Stream, File, others](https://fastapi.tiangolo.com/advanced/custom-response/#default-response-class).\n                ')] = <fastapi.datastructures.DefaultPlaceholder object at 0x0000018DCDE2A570>, responses: Annotated[Optional[Dict[Union[int, str], Dict[str, Any]]], Doc('\n                Additional responses to be shown in OpenAPI.\n\n                It will be added to the generated OpenAPI (e.g. visible at `/docs`).\n\n                Read more about it in the\n                [FastAPI docs for Additional Responses in OpenAPI](https://fastapi.tiangolo.com/advanced/additional-responses/).\n\n                And in the\n                [FastAPI docs for Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-an-apirouter-with-a-custom-prefix-tags-responses-and-dependencies).\n                ')] = None, callbacks: Annotated[Optional[List[starlette.routing.BaseRoute]], Doc('\n                OpenAPI callbacks that should apply to all *path operations* in this\n                router.\n\n                It will be added to the generated OpenAPI (e.g. visible at `/docs`).\n\n                Read more about it in the\n                [FastAPI docs for OpenAPI Callbacks](https://fastapi.tiangolo.com/advanced/openapi-callbacks/).\n                ')] = None, routes: Annotated[Optional[List[starlette.routing.BaseRoute]], Doc("\n                **Note**: you probably shouldn't use this parameter, it is inherited\n                from Starlette and supported for compatibility.\n\n                ---\n\n                A list of routes to serve incoming HTTP and WebSocket requests.\n                "), <typing_extensions.deprecated object at 0x0000018DCDE2A9C0>] = None, redirect_slashes: Annotated[bool, Doc("\n                Whether to detect and redirect slashes in URLs when the client doesn't\n                use the same format.\n                ")] = True, default: Annotated[Optional[Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[NoneType]]], Awaitable[NoneType]]], Doc('\n                Default function handler for this router. Used to handle\n                404 Not Found errors.\n                ')] = None, dependency_overrides_provider: Annotated[Optional[Any], Doc("\n                Only used internally by FastAPI to handle dependency overrides.\n\n                You shouldn't need to use it. It normally points to the `FastAPI` app\n                object.\n                ")] = None, route_class: Annotated[Type[fastapi.routing.APIRoute], Doc('\n                Custom route (*path operation*) class to be used by this router.\n\n                Read more about it in the\n                [FastAPI docs for Custom Request and APIRoute class](https://fastapi.tiangolo.com/how-to/custom-request-and-route/#custom-apiroute-class-in-a-router).\n                ')] = <class 'fastapi.routing.APIRoute'>, on_startup: Annotated[Optional[Sequence[Callable[[], Any]]], Doc('\n                A list of startup event handler functions.\n\n                You should instead use the `lifespan` handlers.\n\n                Read more in the [FastAPI docs for `lifespan`](https://fastapi.tiangolo.com/advanced/events/).\n                ')] = None, on_shutdown: Annotated[Optional[Sequence[Callable[[], Any]]], Doc('\n                A list of shutdown event handler functions.\n\n                You should instead use the `lifespan` handlers.\n\n                Read more in the\n                [FastAPI docs for `lifespan`](https://fastapi.tiangolo.com/advanced/events/).\n                ')] = None, lifespan: Annotated[Union[Callable[[Any], AsyncContextManager[NoneType]], Callable[[Any], AsyncContextManager[Mapping[str, Any]]], NoneType], Doc('\n                A `Lifespan` context manager handler. This replaces `startup` and\n                `shutdown` functions with a single context manager.\n\n                Read more in the\n                [FastAPI docs for `lifespan`](https://fastapi.tiangolo.com/advanced/events/).\n                ')] = None, deprecated: Annotated[Optional[bool], Doc('\n                Mark all *path operations* in this router as deprecated.\n\n                It will be added to the generated OpenAPI (e.g. visible at `/docs`).\n\n                Read more about it in the\n                [FastAPI docs for Path Operation Configuration](https://fastapi.tiangolo.com/tutorial/path-operation-configuration/).\n                ')] = None, include_in_schema: Annotated[bool, Doc('\n                To include (or not) all the *path operations* in this router in the\n                generated OpenAPI.\n\n                This affects the generated OpenAPI (e.g. visible at `/docs`).\n\n                Read more about it in the\n                [FastAPI docs for Query Parameters and String Validations](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/#exclude-from-openapi).\n                ')] = True, generate_unique_id_function: Annotated[Callable[[fastapi.routing.APIRoute], str], Doc('\n                Customize the function used to generate unique IDs for the *path\n                operations* shown in the generated OpenAPI.\n\n                This is particularly useful when automatically generating clients or\n                SDKs for your API.\n\n                Read more about it in the\n                [FastAPI docs about how to Generate Clients](https://fastapi.tiangolo.com/advanced/generate-clients/#custom-generate-unique-id-function).\n                ')] = <fastapi.datastructures.DefaultPlaceholder object at 0x0000018DCDE2A600>) -> None` — type; definido em `fastapi.routing`
- `router(scope: 'Scope', receive: 'Receive', send: 'Send') -> 'None'` — APIRouter; definido em `fastapi.routing`

## `api.telegram_webhook`

- `APIRouter(*, prefix: Annotated[str, Doc('An optional path prefix for the router.')] = '', tags: Annotated[Optional[List[Union[str, enum.Enum]]], Doc('\n                A list of tags to be applied to all the *path operations* in this\n                router.\n\n                It will be added to the generated OpenAPI (e.g. visible at `/docs`).\n\n                Read more about it in the\n                [FastAPI docs for Path Operation Configuration](https://fastapi.tiangolo.com/tutorial/path-operation-configuration/).\n                ')] = None, dependencies: Annotated[Optional[Sequence[fastapi.params.Depends]], Doc('\n                A list of dependencies (using `Depends()`) to be applied to all the\n                *path operations* in this router.\n\n                Read more about it in the\n                [FastAPI docs for Bigger Applications - Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-an-apirouter-with-a-custom-prefix-tags-responses-and-dependencies).\n                ')] = None, default_response_class: Annotated[Type[starlette.responses.Response], Doc('\n                The default response class to be used.\n\n                Read more in the\n                [FastAPI docs for Custom Response - HTML, Stream, File, others](https://fastapi.tiangolo.com/advanced/custom-response/#default-response-class).\n                ')] = <fastapi.datastructures.DefaultPlaceholder object at 0x0000018DCDE2A570>, responses: Annotated[Optional[Dict[Union[int, str], Dict[str, Any]]], Doc('\n                Additional responses to be shown in OpenAPI.\n\n                It will be added to the generated OpenAPI (e.g. visible at `/docs`).\n\n                Read more about it in the\n                [FastAPI docs for Additional Responses in OpenAPI](https://fastapi.tiangolo.com/advanced/additional-responses/).\n\n                And in the\n                [FastAPI docs for Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/#include-an-apirouter-with-a-custom-prefix-tags-responses-and-dependencies).\n                ')] = None, callbacks: Annotated[Optional[List[starlette.routing.BaseRoute]], Doc('\n                OpenAPI callbacks that should apply to all *path operations* in this\n                router.\n\n                It will be added to the generated OpenAPI (e.g. visible at `/docs`).\n\n                Read more about it in the\n                [FastAPI docs for OpenAPI Callbacks](https://fastapi.tiangolo.com/advanced/openapi-callbacks/).\n                ')] = None, routes: Annotated[Optional[List[starlette.routing.BaseRoute]], Doc("\n                **Note**: you probably shouldn't use this parameter, it is inherited\n                from Starlette and supported for compatibility.\n\n                ---\n\n                A list of routes to serve incoming HTTP and WebSocket requests.\n                "), <typing_extensions.deprecated object at 0x0000018DCDE2A9C0>] = None, redirect_slashes: Annotated[bool, Doc("\n                Whether to detect and redirect slashes in URLs when the client doesn't\n                use the same format.\n                ")] = True, default: Annotated[Optional[Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[NoneType]]], Awaitable[NoneType]]], Doc('\n                Default function handler for this router. Used to handle\n                404 Not Found errors.\n                ')] = None, dependency_overrides_provider: Annotated[Optional[Any], Doc("\n                Only used internally by FastAPI to handle dependency overrides.\n\n                You shouldn't need to use it. It normally points to the `FastAPI` app\n                object.\n                ")] = None, route_class: Annotated[Type[fastapi.routing.APIRoute], Doc('\n                Custom route (*path operation*) class to be used by this router.\n\n                Read more about it in the\n                [FastAPI docs for Custom Request and APIRoute class](https://fastapi.tiangolo.com/how-to/custom-request-and-route/#custom-apiroute-class-in-a-router).\n                ')] = <class 'fastapi.routing.APIRoute'>, on_startup: Annotated[Optional[Sequence[Callable[[], Any]]], Doc('\n                A list of startup event handler functions.\n\n                You should instead use the `lifespan` handlers.\n\n                Read more in the [FastAPI docs for `lifespan`](https://fastapi.tiangolo.com/advanced/events/).\n                ')] = None, on_shutdown: Annotated[Optional[Sequence[Callable[[], Any]]], Doc('\n                A list of shutdown event handler functions.\n\n                You should instead use the `lifespan` handlers.\n\n                Read more in the\n                [FastAPI docs for `lifespan`](https://fastapi.tiangolo.com/advanced/events/).\n                ')] = None, lifespan: Annotated[Union[Callable[[Any], AsyncContextManager[NoneType]], Callable[[Any], AsyncContextManager[Mapping[str, Any]]], NoneType], Doc('\n                A `Lifespan` context manager handler. This replaces `startup` and\n                `shutdown` functions with a single context manager.\n\n                Read more in the\n                [FastAPI docs for `lifespan`](https://fastapi.tiangolo.com/advanced/events/).\n                ')] = None, deprecated: Annotated[Optional[bool], Doc('\n                Mark all *path operations* in this router as deprecated.\n\n                It will be added to the generated OpenAPI (e.g. visible at `/docs`).\n\n                Read more about it in the\n                [FastAPI docs for Path Operation Configuration](https://fastapi.tiangolo.com/tutorial/path-operation-configuration/).\n                ')] = None, include_in_schema: Annotated[bool, Doc('\n                To include (or not) all the *path operations* in this router in the\n                generated OpenAPI.\n\n                This affects the generated OpenAPI (e.g. visible at `/docs`).\n\n                Read more about it in the\n                [FastAPI docs for Query Parameters and String Validations](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/#exclude-from-openapi).\n                ')] = True, generate_unique_id_function: Annotated[Callable[[fastapi.routing.APIRoute], str], Doc('\n                Customize the function used to generate unique IDs for the *path\n                operations* shown in the generated OpenAPI.\n\n                This is particularly useful when automatically generating clients or\n                SDKs for your API.\n\n                Read more about it in the\n                [FastAPI docs about how to Generate Clients](https://fastapi.tiangolo.com/advanced/generate-clients/#custom-generate-unique-id-function).\n                ')] = <fastapi.datastructures.DefaultPlaceholder object at 0x0000018DCDE2A600>) -> None` — type; definido em `fastapi.routing`
- `TELEGRAM_BOT_TOKEN` — str; definido em `None`
- `TelegramConversationMetricRecord(operation: 'str', component: 'str', outcome: 'str', duration_ms: 'float', error_category: 'str | None' = None, conflict_recovered: 'bool | None' = None) -> None` — type; definido em `src.services.telegram_observability.contracts`
- `claim_authenticated_telegram_update(update: 'Mapping[str, Any]', *, lease_seconds: 'int' = 120) -> 'TelegramUpdateClaimDecision'` — function; definido em `src.services.telegram_update_receipts.service`
- `complete_authenticated_telegram_update(lease: 'TelegramUpdateProcessingLease') -> 'TelegramUpdateTransitionOutcome'` — function; definido em `src.services.telegram_update_receipts.service`
- `enqueue_authenticated_telegram_update_atomic(update: 'Mapping[str, Any]', *, receipt_lease_seconds: 'int' = 120, max_attempts: 'int' = 5, keyring: 'crypto_service.TelegramUpdateEncryptionKeyring | None' = None) -> 'TelegramUpdateIngressOutcome'` — function; definido em `src.services.telegram_update_jobs.ingress`
- `fail_authenticated_telegram_update(lease: 'TelegramUpdateProcessingLease', *, error_code: 'str' = 'telegram.processing_failed') -> 'TelegramUpdateTransitionOutcome'` — function; definido em `src.services.telegram_update_receipts.service`
- `router(scope: 'Scope', receive: 'Receive', send: 'Send') -> 'None'` — APIRouter; definido em `fastapi.routing`

## `src.context_engineering.token_budget`

- `AVERAGE_CHARACTERS_PER_TOKEN` — int; definido em `None`
- `DEFAULT_MAX_CONTEXT_TOKENS` — int; definido em `None`
- `DEFAULT_RESERVED_OUTPUT_TOKENS` — int; definido em `None`
- `estimate_tokens(value: 'Any') -> 'int'` — function; definido em `src.context_engineering.token_budget`
- `truncate_text_to_token_budget(text: 'str', *, max_tokens: 'int') -> 'str'` — function; definido em `src.context_engineering.token_budget`

## `src.dashboard`

- `normalizar_risco_admin(valor)` — function; definido em `src.dashboard`
- `render_main_metrics(diagnosticos_df, feedbacks_df)` — function; definido em `src.dashboard`

## `src.observability.llm_costs`

- `extrair_tokens_resposta(resposta: 'Any') -> 'dict[str, int]'` — function; definido em `src.observability.llm_costs`

## `src.rag_engine`

- `tokenize(text: str) -> list[str]` — function; definido em `src.rag_engine`

## `src.services.telegram_conversation_state.contracts`

- `Mapping()` — ABCMeta; definido em `collections.abc`
- `MappingProxyType` — type; definido em `builtins`

## `src.services.telegram_conversation_state.store`

- `Mapping()` — ABCMeta; definido em `collections.abc`

## `src.services.telegram_conversation_state.webhook_bridge`

- `Mapping()` — ABCMeta; definido em `collections.abc`
- `NoOpTelegramConversationMetrics()` — type; definido em `src.services.telegram_observability.metrics`
- `TelegramConversationMetricRecord(operation: 'str', component: 'str', outcome: 'str', duration_ms: 'float', error_category: 'str | None' = None, conflict_recovered: 'bool | None' = None) -> None` — type; definido em `src.services.telegram_observability.contracts`
- `TelegramConversationMetrics(*args, **kwargs)` — _ProtocolMeta; definido em `src.services.telegram_observability.contracts`
- `_safe_record_bridge_metric(bridge: 'Any', record: 'TelegramConversationMetricRecord') -> 'None'` — function; definido em `src.services.telegram_conversation_state.webhook_bridge`

## `src.services.telegram_observability.contracts`

- `ALLOWED_METRIC_COMPONENTS` — frozenset; definido em `None`
- `ALLOWED_METRIC_OPERATIONS` — frozenset; definido em `None`
- `Mapping(*args, **kwargs)` — _SpecialGenericAlias; definido em `typing`
- `MappingProxyType` — type; definido em `builtins`
- `TelegramConversationMetricRecord(operation: 'str', component: 'str', outcome: 'str', duration_ms: 'float', error_category: 'str | None' = None, conflict_recovered: 'bool | None' = None) -> None` — type; definido em `src.services.telegram_observability.contracts`
- `TelegramConversationMetrics(*args, **kwargs)` — _ProtocolMeta; definido em `src.services.telegram_observability.contracts`

## `src.services.telegram_observability.operational_http`

- `Mapping(*args, **kwargs)` — _SpecialGenericAlias; definido em `typing`
- `MappingProxyType` — type; definido em `builtins`
- `_internal_runtime_payload(result: 'TelegramReadinessRuntimeResult', *, probe: 'TelegramOperationalProbeKind') -> 'dict[str, object]'` — function; definido em `src.services.telegram_observability.operational_http`

## `src.services.telegram_observability.prometheus_exporter`

- `Mapping(*args, **kwargs)` — _SpecialGenericAlias; definido em `typing`
- `OPENMETRICS_CONTENT_TYPE` — str; definido em `None`
- `SafeTelegramPrometheusMetricsExporter(delegate: 'TelegramPrometheusMetricsExporter') -> 'None'` — type; definido em `src.services.telegram_observability.prometheus_exporter`
- `TelegramMetricsExport(body: 'str', content_type: 'str', format: 'TelegramMetricsExportFormat') -> None` — type; definido em `src.services.telegram_observability.prometheus_exporter`
- `TelegramMetricsExportFormat(*values)` — EnumType; definido em `src.services.telegram_observability.prometheus_exporter`
- `TelegramPrometheusMetricsExporter()` — type; definido em `src.services.telegram_observability.prometheus_exporter`
- `_METRIC_NAME_PATTERN` — Pattern; definido em `re`
- `_validate_metric_name(name: 'object') -> 'str'` — function; definido em `src.services.telegram_observability.prometheus_exporter`

## `src.services.telegram_observability.readiness_runtime`


## `src.services.telegram_update_jobs.execution`

- `Mapping()` — ABCMeta; definido em `collections.abc`
- `MappingProxyType` — type; definido em `builtins`
- `decrypt_authenticated_telegram_worker_lease(lease: 'worker_module.TelegramUpdateWorkerLease', *, keyring: 'crypto_service.TelegramUpdateEncryptionKeyring | None' = None) -> 'TelegramUpdateWorkerPayload'` — function; definido em `src.services.telegram_update_jobs.execution`

## `src.services.telegram_update_jobs.ingress`

- `Mapping()` — ABCMeta; definido em `collections.abc`
- `_generate_claim_token() -> 'str'` — function; definido em `src.services.telegram_update_jobs.ingress`
- `enqueue_authenticated_telegram_update_atomic(update: 'Mapping[str, Any]', *, receipt_lease_seconds: 'int' = 120, max_attempts: 'int' = 5, keyring: 'crypto_service.TelegramUpdateEncryptionKeyring | None' = None) -> 'TelegramUpdateIngressOutcome'` — function; definido em `src.services.telegram_update_jobs.ingress`

## `src.services.telegram_update_jobs.repository`


## `src.services.telegram_update_jobs.runner`


## `src.services.telegram_update_jobs.service`

- `LOCK_TOKEN_PATTERN` — Pattern; definido em `re`
- `Mapping(*args, **kwargs)` — _SpecialGenericAlias; definido em `typing`
- `MappingProxyType` — type; definido em `builtins`
- `_build_authenticated_data(*, update_id: 'int', payload_key_id: 'str', payload_version: 'int') -> 'bytes'` — function; definido em `src.services.telegram_update_jobs.service`
- `decrypt_authenticated_telegram_update(*, update_id: 'int', payload_ciphertext: 'bytes', payload_nonce: 'bytes', payload_key_id: 'str', payload_version: 'int', keyring: 'TelegramUpdateEncryptionKeyring | None' = None) -> 'dict[str, Any]'` — function; definido em `src.services.telegram_update_jobs.service`
- `encrypt_authenticated_telegram_update(update: 'Any', *, keyring: 'TelegramUpdateEncryptionKeyring | None' = None) -> 'EncryptedTelegramUpdatePayload'` — function; definido em `src.services.telegram_update_jobs.service`
- `generate_telegram_update_job_lock_token() -> 'str'` — function; definido em `src.services.telegram_update_jobs.service`

## `src.services.telegram_update_jobs.worker`

- `SQL_RECOVER_EXPIRED_AUTHENTICATED_JOBS` — str; definido em `None`
- `claim_next_authenticated_telegram_update_job_atomic(*, lease_seconds: 'int' = 120) -> 'TelegramUpdateWorkerLease | None'` — function; definido em `src.services.telegram_update_jobs.worker`
- `complete_authenticated_telegram_update_job_atomic(lease: 'TelegramUpdateWorkerLease') -> 'TelegramUpdateWorkerCompletionOutcome'` — function; definido em `src.services.telegram_update_jobs.worker`
- `recover_expired_authenticated_telegram_update_jobs_atomic(*, limit: 'int' = 100) -> 'TelegramUpdateWorkerRecoveryBatch'` — function; definido em `src.services.telegram_update_jobs.worker`
- `retry_or_dead_letter_authenticated_telegram_update_job_atomic(lease: 'TelegramUpdateWorkerLease', *, error_code: 'str', retry_delay_seconds: 'int', force_dead_letter: 'bool' = False) -> 'TelegramUpdateWorkerFailureOutcome'` — function; definido em `src.services.telegram_update_jobs.worker`

## `src.services.telegram_update_receipts.service`

- `Mapping()` — ABCMeta; definido em `collections.abc`
- `_generate_claim_token() -> 'str'` — function; definido em `src.services.telegram_update_receipts.service`
- `claim_authenticated_telegram_update(update: 'Mapping[str, Any]', *, lease_seconds: 'int' = 120) -> 'TelegramUpdateClaimDecision'` — function; definido em `src.services.telegram_update_receipts.service`
- `complete_authenticated_telegram_update(lease: 'TelegramUpdateProcessingLease') -> 'TelegramUpdateTransitionOutcome'` — function; definido em `src.services.telegram_update_receipts.service`
- `fail_authenticated_telegram_update(lease: 'TelegramUpdateProcessingLease', *, error_code: 'str' = 'telegram.processing_failed') -> 'TelegramUpdateTransitionOutcome'` — function; definido em `src.services.telegram_update_receipts.service`

## Falhas de importação

- Nenhuma.
