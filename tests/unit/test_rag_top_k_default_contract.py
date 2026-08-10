from __future__ import annotations

import inspect

import src.agent_tools.rag_tools as rag_tools
import src.rag_engine as rag_engine


def test_answer_with_rag_default_top_k_is_two() -> None:
    signature = inspect.signature(
        rag_engine.answer_with_rag
    )

    assert signature.parameters["top_k"].default == 2


def test_consultar_rag_inna_default_top_k_is_two() -> None:
    signature = inspect.signature(
        rag_tools.consultar_rag_inna
    )

    assert signature.parameters["top_k"].default == 2


def test_formal_rag_input_default_top_k_is_two() -> None:
    payload = rag_tools.BuscarConhecimentoRagInput(
        pergunta="Como organizar meu orcamento?"
    )

    assert payload.top_k == 2


def test_invalid_direct_top_k_falls_back_to_two(
    monkeypatch,
) -> None:
    captured: dict[str, int] = {}

    def fake_answer_with_rag(
        pergunta: str,
        idioma: str = "pt",
        top_k: int = 2,
    ) -> dict:
        del pergunta, idioma
        captured["top_k"] = top_k

        return {
            "resposta": "Resposta de teste.",
            "fontes": ["fonte-teste"],
            "contexto_usado": "Contexto de teste.",
            "modo": "rag_teste",
        }

    monkeypatch.setattr(
        rag_engine,
        "answer_with_rag",
        fake_answer_with_rag,
    )
    def fake_save_rag_log(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(
        rag_engine,
        "save_rag_log",
        fake_save_rag_log,
    )

    result = rag_tools.consultar_rag_inna(
        "Como organizar meu orcamento?",
        top_k=None,
    )

    assert result.ok is True
    assert captured["top_k"] == 2
