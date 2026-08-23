from unittest.mock import patch

from src.observability.llm_notifications import (
    avaliar_persistir_e_notificar_alertas,
)


def criar_alerta():
    return {
        "codigo": "teste_automatico",
        "titulo": "Teste automático",
        "descricao": "Alerta controlado.",
        "categoria": "observabilidade",
        "severidade": "alta",
        "ordem_severidade": 4,
        "valor_atual": 1,
        "valor_limite": 0,
        "unidade": "teste",
        "modelo": None,
        "operacao": None,
        "trace_id": None,
        "dedupe_key": "teste_automatico",
        "recomendacao": "Validar o fluxo.",
        "metadados": {},
    }


@patch(
    "src.observability.llm_notifications."
    "notificar_alerta_email"
)
@patch(
    "src.observability.llm_alerts."
    "avaliar_e_persistir_alertas"
)
def test_notifica_alerta_novo(
    mock_avaliar,
    mock_notificar,
):
    alerta = criar_alerta()

    mock_avaliar.return_value = {
        "ok": True,
        "alertas_detectados": [alerta],
        "resultados_persistencia": [
            {
                "ok": True,
                "salvo": True,
                "duplicado": False,
                "id": 15,
                "criado_em": "2026-07-15",
            }
        ],
        "total_detectados": 1,
        "total_salvos": 1,
        "total_duplicados": 0,
    }

    mock_notificar.return_value = {
        "ok": True,
        "enviado": True,
        "duplicado": False,
    }

    resultado = (
        avaliar_persistir_e_notificar_alertas(
            None,
            {},
        )
    )

    assert (
        resultado[
            "total_notificacoes_enviadas"
        ]
        == 1
    )

    alerta_enviado = (
        mock_notificar.call_args.args[0]
    )

    assert alerta_enviado["id"] == 15
    assert alerta_enviado["status"] == "aberto"


@patch(
    "src.observability.llm_notifications."
    "notificar_alerta_email"
)
@patch(
    "src.observability.llm_alerts."
    "avaliar_e_persistir_alertas"
)
def test_nao_notifica_alerta_duplicado(
    mock_avaliar,
    mock_notificar,
):
    alerta = criar_alerta()

    mock_avaliar.return_value = {
        "ok": True,
        "alertas_detectados": [alerta],
        "resultados_persistencia": [
            {
                "ok": True,
                "salvo": False,
                "duplicado": True,
            }
        ],
        "total_detectados": 1,
        "total_salvos": 0,
        "total_duplicados": 1,
    }

    resultado = (
        avaliar_persistir_e_notificar_alertas(
            None,
            {},
        )
    )

    mock_notificar.assert_not_called()

    assert (
        resultado[
            "total_notificacoes_enviadas"
        ]
        == 0
    )

    assert (
        resultado[
            "total_notificacoes_ignoradas"
        ]
        == 1
    )
