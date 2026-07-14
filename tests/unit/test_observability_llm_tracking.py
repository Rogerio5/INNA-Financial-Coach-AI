from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.observability.llm_tracking import (
    executar_generate_content_observado,
    executar_llm_observado,
)


def criar_resposta():
    return SimpleNamespace(
        text="resposta simulada",
        usage_metadata=SimpleNamespace(
            prompt_token_count=120,
            candidates_token_count=30,
            total_token_count=150,
        ),
    )


@patch(
    "src.observability.llm_tracking."
    "registrar_consumo_llm"
)
def test_executar_llm_observado_sucesso(
    registrar,
):
    resposta = criar_resposta()

    resultado = executar_llm_observado(
        lambda: resposta,
        modelo="gemini-teste",
        operacao="teste",
        origem="unitario",
    )

    assert resultado is resposta

    registrar.assert_called_once()

    argumentos = registrar.call_args.kwargs

    assert argumentos["sucesso"] is True
    assert argumentos["tokens_entrada"] == 120
    assert argumentos["tokens_saida"] == 30
    assert argumentos["tokens_totais"] == 150
    assert argumentos["duracao_ms"] >= 0


@patch(
    "src.observability.llm_tracking."
    "registrar_consumo_llm"
)
def test_executar_llm_observado_falha(
    registrar,
):
    def chamada():
        raise RuntimeError(
            "falha simulada"
        )

    with pytest.raises(
        RuntimeError,
        match="falha simulada",
    ):
        executar_llm_observado(
            chamada,
            modelo="gemini-teste",
            operacao="teste_falha",
        )

    argumentos = registrar.call_args.kwargs

    assert argumentos["sucesso"] is False
    assert (
        argumentos["erro_tipo"]
        == "RuntimeError"
    )
    assert (
        argumentos["erro_mensagem"]
        == "falha simulada"
    )


@patch(
    "src.observability.llm_tracking."
    "registrar_consumo_llm"
)
def test_wrapper_generate_content(
    registrar,
):
    resposta = criar_resposta()

    client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **kwargs: (
                resposta
            )
        )
    )

    resultado = (
        executar_generate_content_observado(
            client,
            modelo="gemini-teste",
            contents="conteúdo simulado",
            operacao="rag_answer",
        )
    )

    assert resultado is resposta
    registrar.assert_called_once()


@patch(
    "src.observability.llm_tracking."
    "registrar_consumo_llm"
)
def test_nao_registra_prompt_ou_resposta(
    registrar,
):
    executar_llm_observado(
        criar_resposta,
        modelo="gemini-teste",
        operacao="privacidade",
        metadados={
            "modo": "rag",
        },
    )

    argumentos = registrar.call_args.kwargs

    assert "prompt" not in argumentos
    assert "contents" not in argumentos
    assert "resposta" not in argumentos

    assert argumentos["metadados"][
        "conteudo_registrado"
    ] is False
