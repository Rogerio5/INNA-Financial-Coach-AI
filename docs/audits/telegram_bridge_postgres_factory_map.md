# F2H5-D5B — Factory PostgreSQL da bridge

Factory: `create_postgres_telegram_webhook_conversation_bridge`

Ocorrências: 1

## Ocorrência 1

- Arquivo: `src/services/telegram_conversation_state/webhook_bridge.py`
- Linhas: 965–1004
- Assinatura: `def create_postgres_telegram_webhook_conversation_bridge(*, default_ttl_seconds: int=DEFAULT_STATE_TTL_SECONDS, default_language: str='pt-BR') -> TelegramWebhookConversationBridge`
- Retorno: `TelegramWebhookConversationBridge`

### Argumentos

| Nome | Tipo | Kind | Default |
|---|---|---|---|
| `default_ttl_seconds` | `int` | keyword_only | `DEFAULT_STATE_TTL_SECONDS` |
| `default_language` | `str` | keyword_only | `'pt-BR'` |

### Implementação

```python
def create_postgres_telegram_webhook_conversation_bridge(
    *,
    default_ttl_seconds: int = (
        DEFAULT_STATE_TTL_SECONDS
    ),
    default_language: str = "pt-BR",
) -> TelegramWebhookConversationBridge:
    normalized_ttl = (
        validate_state_ttl_seconds(
            default_ttl_seconds
        )
    )

    normalized_language = (
        normalize_telegram_language(
            default_language
        )
    )

    if normalized_language is None:
        raise TelegramConversationStateValidationError(
            "default_language é obrigatório."
        )

    def runtime_factory(
    ) -> TelegramConversationStateRuntimePort:
        return (
            create_postgres_telegram_conversation_state_runtime(
                default_ttl_seconds=(
                    normalized_ttl
                )
            )
        )

    return TelegramWebhookConversationBridge(
        runtime_factory=runtime_factory,
        default_language=(
            normalized_language
        ),
    )
```

### Chamadas internas

- Linha 973: `validate_state_ttl_seconds` — keywords=``
- Linha 979: `normalize_telegram_language` — keywords=``
- Linha 999: `TelegramWebhookConversationBridge` — keywords=`runtime_factory, default_language`
- Linha 985: `TelegramConversationStateValidationError` — keywords=``
- Linha 992: `create_postgres_telegram_conversation_state_runtime` — keywords=`default_ttl_seconds`
