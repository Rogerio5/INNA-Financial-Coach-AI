from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver

from src.agents.graph import (
    _criar_estado_inicial,
    criar_grafo_inna,
)
from src.agents.state import (
    merge_conversation_history,
)


def test_estado_inicial_registra_usuario():
    estado = _criar_estado_inicial(
        "Como criar uma reserva?",
        thread_id="thread-teste",
        usuario_id="usuario-1",
        idioma="pt",
        moeda="BRL",
    )

    assert estado["thread_id"] == "thread-teste"

    assert estado["conversation_history"] == [
        {
            "role": "user",
            "content": "Como criar uma reserva?",
        }
    ]


def test_grafo_acumula_historico_com_checkpointer():
    checkpointer = InMemorySaver()

    graph = criar_grafo_inna(
        checkpointer=checkpointer,
    )

    config = {
        "configurable": {
            "thread_id": "thread-memoria",
        }
    }

    primeiro_estado = _criar_estado_inicial(
        "Olá, tudo bem?",
        thread_id="thread-memoria",
        usuario_id="usuario-1",
        idioma="pt",
        moeda="BRL",
    )

    primeiro_resultado = graph.invoke(
        primeiro_estado,
        config=config,
    )

    assert len(
        primeiro_resultado["conversation_history"]
    ) == 2

    segundo_estado = _criar_estado_inicial(
        "Quero gerar um relatório em PDF.",
        thread_id="thread-memoria",
        usuario_id="usuario-1",
        idioma="pt",
        moeda="BRL",
    )

    segundo_resultado = graph.invoke(
        segundo_estado,
        config=config,
    )

    historico = segundo_resultado[
        "conversation_history"
    ]

    assert len(historico) == 4

    assert historico[0]["role"] == "user"
    assert historico[1]["role"] == "assistant"
    assert historico[2]["role"] == "user"
    assert historico[3]["role"] == "assistant"


def test_threads_diferentes_nao_compartilham_historico():
    checkpointer = InMemorySaver()

    graph = criar_grafo_inna(
        checkpointer=checkpointer,
    )

    estado_a = _criar_estado_inicial(
        "Olá",
        thread_id="thread-a",
        usuario_id="usuario-1",
        idioma="pt",
        moeda="BRL",
    )

    estado_b = _criar_estado_inicial(
        "Quero um relatório em PDF.",
        thread_id="thread-b",
        usuario_id="usuario-1",
        idioma="pt",
        moeda="BRL",
    )

    resultado_a = graph.invoke(
        estado_a,
        config={
            "configurable": {
                "thread_id": "thread-a",
            }
        },
    )

    resultado_b = graph.invoke(
        estado_b,
        config={
            "configurable": {
                "thread_id": "thread-b",
            }
        },
    )

    assert len(
        resultado_a["conversation_history"]
    ) == 2

    assert len(
        resultado_b["conversation_history"]
    ) == 2


def test_reducer_nao_duplica_historico_completo():
    atual = [
        {
            "role": "user",
            "content": "Olá",
        }
    ]

    update = [
        {
            "role": "user",
            "content": "Olá",
        },
        {
            "role": "assistant",
            "content": "Olá! Como posso ajudar?",
        },
    ]

    resultado = merge_conversation_history(
        atual,
        update,
    )

    assert resultado == update
    assert len(resultado) == 2


def test_reducer_adiciona_mensagem_incremental():
    atual = [
        {
            "role": "user",
            "content": "Olá",
        }
    ]

    update = [
        {
            "role": "assistant",
            "content": "Olá! Como posso ajudar?",
        }
    ]

    resultado = merge_conversation_history(
        atual,
        update,
    )

    assert len(resultado) == 2
    assert resultado[-1]["role"] == "assistant"


def test_reducer_remove_duplicacao_consecutiva():
    mensagem = {
        "role": "user",
        "content": "Como criar uma reserva?",
    }

    resultado = merge_conversation_history(
        [mensagem],
        [mensagem],
    )

    assert resultado == [mensagem]
