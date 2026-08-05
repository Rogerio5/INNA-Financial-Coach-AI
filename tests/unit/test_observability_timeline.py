from unittest.mock import patch

from src.observability.timeline import (
    ETAPAS_TIMELINE,
    LABELS_ETAPAS,
    executar_etapa_timeline,
    gerar_trace_id,
    registrar_evento_timeline,
)


def test_gerar_trace_id_valido():
    trace_1 = gerar_trace_id()
    trace_2 = gerar_trace_id()

    assert trace_1
    assert trace_2
    assert trace_1 != trace_2
    assert len(trace_1) == 36


def test_ordem_das_etapas():
    assert (
        ETAPAS_TIMELINE["pergunta_recebida"]
        < ETAPAS_TIMELINE["memoria_consultada"]
        < ETAPAS_TIMELINE["router_executado"]
        < ETAPAS_TIMELINE["tool_executada"]
        < ETAPAS_TIMELINE["rag_consultado"]
        < ETAPAS_TIMELINE["prompt_montado"]
        < ETAPAS_TIMELINE["gemini_executado"]
        < ETAPAS_TIMELINE["resposta_formatada"]
        < ETAPAS_TIMELINE["resposta_entregue"]
    )


def test_todas_etapas_possuem_label():
    assert set(ETAPAS_TIMELINE) == set(LABELS_ETAPAS)


@patch("src.observability.timeline._conectar_postgres")
def test_etapa_invalida_nao_acessa_banco(
    mock_conectar,
):
    resultado = registrar_evento_timeline(
        trace_id=gerar_trace_id(),
        etapa="etapa_inexistente",
    )

    assert resultado["ok"] is False
    assert "Etapa desconhecida" in resultado["message"]

    mock_conectar.assert_not_called()


@patch("src.observability.timeline.registrar_evento_timeline")
def test_executar_etapa_com_sucesso(
    mock_registrar,
):
    mock_registrar.return_value = {
        "ok": True,
        "evento_id": 1,
    }

    resultado = executar_etapa_timeline(
        trace_id=gerar_trace_id(),
        etapa="router_executado",
        funcao=lambda valor: valor * 2,
        argumentos={
            "valor": 5,
        },
    )

    assert resultado["ok"] is True
    assert resultado["resultado"] == 10
    assert resultado["duracao_ms"] >= 0

    mock_registrar.assert_called_once()


@patch("src.observability.timeline.registrar_evento_timeline")
def test_executar_etapa_com_falha_sem_propagar(
    mock_registrar,
):
    mock_registrar.return_value = {
        "ok": True,
        "evento_id": 2,
    }

    def funcao_com_erro():
        raise ValueError("Erro simulado")

    resultado = executar_etapa_timeline(
        trace_id=gerar_trace_id(),
        etapa="gemini_executado",
        funcao=funcao_com_erro,
        propagar_erro=False,
    )

    assert resultado["ok"] is False
    assert resultado["resultado"] is None
    assert resultado["erro"] == "Erro simulado"

    argumentos_registro = mock_registrar.call_args.kwargs

    assert argumentos_registro["status"] == "falha"
    assert argumentos_registro["erro"] == "Erro simulado"


@patch("src.observability.timeline.registrar_evento_timeline")
def test_falha_no_registro_nao_apaga_resultado(
    mock_registrar,
):
    mock_registrar.return_value = {
        "ok": False,
        "message": "Banco indisponível",
    }

    resultado = executar_etapa_timeline(
        trace_id=gerar_trace_id(),
        etapa="tool_executada",
        funcao=lambda: {
            "saldo": 3000,
        },
    )

    assert resultado["ok"] is True
    assert resultado["resultado"]["saldo"] == 3000
    assert resultado["timeline"]["ok"] is False
