# F2H5-D5B — Factory observável da bridge

Factory: `create_postgres_telegram_webhook_conversation_bridge`

## Definição

- Arquivo: `src/services/telegram_conversation_state/webhook_bridge.py`
- Linhas: 965–1004
- Assinatura: `def create_postgres_telegram_webhook_conversation_bridge(*, default_ttl_seconds: int=DEFAULT_STATE_TTL_SECONDS, default_language: str='pt-BR') -> TelegramWebhookConversationBridge`

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

## Compatibilidade de observabilidade

- Aceita `metrics`: False
- Aceita `event_sink`: False
- Aceita `clock`: False

## Exportação

- Exportada por `src/services/telegram_conversation_state/__init__.py`

## Chamadores localizados

- Nenhum chamador localizado dentro do pacote.
