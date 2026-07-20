# Mapa de instrumentação da observabilidade Telegram

## Princípios

- Instrumentar primeiro através de contratos internos.
- Não importar Prometheus no domínio.
- Medir duração com relógio monotônico.
- Telemetria não deve alterar retorno ou exceção da operação.
- Labels devem possuir baixa cardinalidade.

## Pontos de instrumentação

| Componente | Função/operação | Situação | Evento | Métrica | Medir duração |
|---|---|---|---|---|---|
| webhook | send_telegram_message | configuração ausente | telegram_configuration_missing | contador | não |
| webhook | _process_telegram_update_core | update inválido | telegram_update_invalid_discarded | contador | não |
| webhook | _process_telegram_update_core | falha de processamento | telegram_update_processing_failed | contador + duração | não |
| bridge | load_or_open_session | carregar/abrir sessão | telegram_session_load_completed | contador + histograma | sim |
| bridge | save_session | salvar sessão | telegram_session_save_completed | contador + histograma | sim |
| bridge | save_session | conflito otimista | telegram_session_save_conflict | contador | sim |
| bridge | reload_session | recarregar sessão | telegram_session_reload_completed | contador + histograma | sim |
| bridge | delete_session | excluir sessão | telegram_session_delete_completed | contador + histograma | sim |
| bridge | resolve_language | resolver idioma | telegram_language_resolution_completed | contador + histograma | sim |
| worker | main | início | telegram_worker_started | contador | não |
| worker | claim | fila vazia | telegram_worker_claim_empty | contador | não |
| worker | process | update claimed | telegram_worker_update_claimed | contador | sim |
| worker | process | update concluído | telegram_worker_update_completed | contador + histograma | sim |
| worker | process | update falhou | telegram_worker_update_failed | contador + histograma | sim |
| receipt | complete_authenticated_telegram_update | conclusão | telegram_receipt_completed | contador | não |
| receipt | fail_authenticated_telegram_update | falha | telegram_receipt_failed | contador | não |
| repository | _safe_rollback | rollback falhou | telegram_repository_rollback_failed | contador | não |

## Operações obrigatórias da bridge

- `delete_session`
- `load_or_open_session`
- `reload_session`
- `resolve_language`
- `save_session`

## Operações de receipts localizadas

- `complete_authenticated_telegram_update`
- `fail_authenticated_telegram_update`

## Supressões revisadas

### `SystemExit` no worker

Classificação: comportamento controlado de CLI.

Decisão: não registrar como erro operacional quando representar encerramento esperado.

### `_safe_rollback` no repository

Classificação: supressão defensiva intencional.

Decisão: manter o rollback sem propagar uma segunda exceção, mas emitir `telegram_repository_rollback_failed` de maneira sanitizada.

## Próxima implementação

Criar os contratos:

- `TelegramConversationMetrics`
- `TelegramOperationalEventSink`
- `NoOpTelegramConversationMetrics`
- `InMemoryTelegramConversationMetrics`
- `NoOpTelegramOperationalEventSink`
- `InMemoryTelegramOperationalEventSink`
