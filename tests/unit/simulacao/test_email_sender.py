from unittest.mock import Mock, patch

from src.email_sender import (
    send_diagnostico_email,
    send_text_email,
)


@patch.dict(
    "os.environ",
    {
        "RESEND_API_KEY": "chave-teste",
        "EMAIL_FROM": "INNA <onboarding@resend.dev>",
    },
)
@patch("src.email_sender.requests.post")
def test_send_text_email(mock_post):
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "id": "email_teste_123"
    }
    mock_post.return_value = response

    resultado = send_text_email(
        to_email="teste@example.com",
        subject="Alerta da INNA",
        body="Conteúdo técnico",
        html_body="<p>Conteúdo técnico</p>",
    )

    assert resultado["ok"] is True
    assert resultado["message_id"] == "email_teste_123"

    payload = mock_post.call_args.kwargs["json"]

    assert payload["to"] == ["teste@example.com"]
    assert payload["subject"] == "Alerta da INNA"
    assert payload["text"] == "Conteúdo técnico"
    assert payload["html"] == "<p>Conteúdo técnico</p>"
    assert "attachments" not in payload


@patch.dict(
    "os.environ",
    {
        "RESEND_API_KEY": "chave-teste",
        "EMAIL_FROM": "INNA <onboarding@resend.dev>",
    },
)
@patch("src.email_sender.requests.post")
def test_send_diagnostico_email_preserva_anexo(mock_post):
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "id": "diagnostico_123"
    }
    mock_post.return_value = response

    resultado = send_diagnostico_email(
        to_email="teste@example.com",
        subject="Diagnóstico",
        body="Relatório anexado",
        pdf_bytes=b"PDF TESTE",
    )

    assert resultado["ok"] is True

    payload = mock_post.call_args.kwargs["json"]

    assert len(payload["attachments"]) == 1
    assert (
        payload["attachments"][0]["filename"]
        == "relatorio-inna.pdf"
    )


@patch.dict(
    "os.environ",
    {
        "RESEND_API_KEY": "chave-teste",
    },
)
@patch("src.email_sender.requests.post")
def test_resend_rejeitado_gera_erro(mock_post):
    response = Mock()
    response.status_code = 422
    response.text = "invalid recipient"
    mock_post.return_value = response

    try:
        send_text_email(
            to_email="invalido",
            subject="Teste",
            body="Teste",
        )
    except RuntimeError as exc:
        assert "Erro Resend: 422" in str(exc)
    else:
        raise AssertionError(
            "Era esperado um RuntimeError."
        )
