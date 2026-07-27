from src.observability.phoenix_privacy import (
    hash_identifier,
    sanitize_attributes,
)


def test_removes_sensitive_attributes():
    result = sanitize_attributes(
        {
            "agent.name": "financial_agent",
            "prompt": "conteúdo privado",
            "response": "resposta privada",
            "PHOENIX_API_KEY": "segredo",
            "authorization": "Bearer segredo",
            "DATABASE_URL": "postgresql://segredo",
            "operation.success": True,
        }
    )

    assert result["agent.name"] == "financial_agent"
    assert result["operation.success"] is True
    assert result["privacy.content_exported"] is False

    assert "prompt" not in result
    assert "response" not in result
    assert "PHOENIX_API_KEY" not in result
    assert "authorization" not in result
    assert "DATABASE_URL" not in result


def test_hash_identifier_is_deterministic_and_irreversible():
    first = hash_identifier("usuario-123")
    second = hash_identifier("usuario-123")

    assert first == second
    assert first != "usuario-123"
    assert len(first) == 16


def test_converts_complex_objects_to_type_name():
    result = sanitize_attributes(
        {
            "operation.metadata": {
                "private": "value",
            }
        }
    )

    assert result["operation.metadata"] == "<dict>"
