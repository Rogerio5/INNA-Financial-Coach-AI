from src.observability.llm_notifications import (
    alerta_deve_ser_enviado,
    mascarar_email,
    montar_email_alerta,
)


def criar_alerta(
    severidade="alta",
    status="aberto",
):
    return {
        "id": 10,
        "titulo": (
            "Chamadas de LLM com alta latência"
        ),
        "descricao": (
            "Foi detectada uma chamada lenta."
        ),
        "categoria": "performance",
        "severidade": severidade,
        "status": status,
        "valor_atual": 173000,
        "valor_limite": 30000,
        "unidade": "ms",
        "recomendacao": (
            "Verificar cold start."
        ),
    }


def test_mascarar_email():
    resultado = mascarar_email(
        "rogeriosabino661@gmail.com"
    )

    assert resultado.startswith("ro***")
    assert resultado.endswith("@gmail.com")


def test_alerta_alto_aberto_deve_ser_enviado():
    assert alerta_deve_ser_enviado(
        criar_alerta(),
        severidade_minima="alta",
    ) is True


def test_alerta_medio_nao_deve_ser_enviado():
    assert alerta_deve_ser_enviado(
        criar_alerta(
            severidade="media"
        ),
        severidade_minima="alta",
    ) is False


def test_alerta_resolvido_nao_deve_ser_enviado():
    assert alerta_deve_ser_enviado(
        criar_alerta(
            status="resolvido"
        ),
        severidade_minima="alta",
    ) is False


def test_montar_email_alerta():
    email = montar_email_alerta(
        criar_alerta()
    )

    assert (
        "Chamadas de LLM com alta latência"
        in email["assunto"]
    )

    assert "173000" in email["texto"]
    assert "30000" in email["texto"]
    assert "<h2>" in email["html"]
