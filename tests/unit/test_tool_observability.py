from unittest.mock import patch

from src.tools.orchestrator import (
    processar_pergunta_com_tools,
)


def memoria_teste():
    return {
        "usuario_id": "demo_user",
        "renda_mensal": 6300,
        "gastos_mensais": 3300,
        "valor_reserva": 1200,
    }


def test_orquestrador_retorna_duracao():
    resultado = processar_pergunta_com_tools(
        pergunta=(
            "Com minha renda e gastos, "
            "quanto sobra?"
        ),
        memoria=memoria_teste(),
    )

    assert "duracao_ms" in resultado
    assert resultado["duracao_ms"] >= 0


def test_observabilidade_desativada_por_padrao():
    resultado = processar_pergunta_com_tools(
        pergunta="Quanto posso guardar por semana?",
        memoria=memoria_teste(),
    )

    assert (
        resultado["observabilidade"]["ok"]
        is False
    )

    assert (
        resultado["observabilidade"]["message"]
        == "Registro não solicitado."
    )


@patch(
    "src.tools.observability.registrar_evento_tool"
)
def test_registro_de_observabilidade(
    mock_registrar,
):
    mock_registrar.return_value = {
        "ok": True,
        "evento_id": 123,
        "message": "Evento registrado.",
    }

    resultado = processar_pergunta_com_tools(
        pergunta="Quanto posso guardar por semana?",
        memoria=memoria_teste(),
        usuario_id="demo_user",
        origem="teste",
        registrar_observabilidade=True,
    )

    assert resultado["observabilidade"]["ok"] is True
    assert (
        resultado["observabilidade"]["evento_id"]
        == 123
    )

    mock_registrar.assert_called_once()


@patch(
    "src.tools.observability.registrar_evento_tool"
)
def test_falha_de_observabilidade_nao_quebra_tool(
    mock_registrar,
):
    mock_registrar.side_effect = RuntimeError(
        "Banco indisponível"
    )

    resultado = processar_pergunta_com_tools(
        pergunta="Quanto posso guardar por semana?",
        memoria=memoria_teste(),
        registrar_observabilidade=True,
    )

    assert resultado["ok"] is True
    assert resultado["resultado"][
        "valor_semanal_estimado"
    ] == 300.0

    assert (
        resultado["observabilidade"]["ok"]
        is False
    )
