from __future__ import annotations

import ast
from pathlib import Path

RAG_ENGINE_PATH = Path(
    "src/rag_engine.py"
)


def _source() -> str:
    return RAG_ENGINE_PATH.read_text(
        encoding="utf-8-sig",
    )


def _answer_function():
    source = _source()
    tree = ast.parse(source)

    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "answer_with_rag"
    )

    return source, function


def _answer_section() -> str:
    source, function = _answer_function()

    lines = source.splitlines(
        keepends=True
    )

    return "".join(
        lines[
            function.lineno - 1:
            function.end_lineno
        ]
    )


def test_trace_starts_before_hybrid_retrieval():
    section = _answer_section()

    trace_position = section.index(
        "start_retrieval_trace("
    )

    retrieval_position = section.index(
        "search_knowledge_base_hybrid("
    )

    assert trace_position < retrieval_position


def test_trace_finishes_after_search_mode_resolution():
    section = _answer_section()

    mode_position = section.index(
        "modo_busca ="
    )

    finish_position = section.index(
        "retrieval_trace.finish("
    )

    assert mode_position < finish_position


def test_finalizer_preserves_existing_payload():
    section = _answer_section()

    assert (
        "payload = dict(resultado or {})"
        in section
    )

    assert (
        'payload["trace_id"]'
        in section
    )

    assert (
        'payload["retrieval_trace"]'
        in section
    )


def test_security_response_remains_before_trace_start():
    section = _answer_section()

    security_position = section.index(
        "return resposta_seguranca"
    )

    trace_position = section.index(
        "start_retrieval_trace("
    )

    assert security_position < trace_position


def test_no_direct_dict_returns_remain():
    _, function = _answer_function()

    direct_dict_returns = [
        node.lineno
        for node in ast.walk(function)
        if (
            isinstance(node, ast.Return)
            and isinstance(node.value, ast.Dict)
        )
    ]

    assert direct_dict_returns == []


def test_fifteen_post_retrieval_returns_are_finalized():
    _, function = _answer_function()

    finalized_returns = [
        node.lineno
        for node in ast.walk(function)
        if (
            isinstance(node, ast.Return)
            and isinstance(node.value, ast.Call)
            and isinstance(
                node.value.func,
                ast.Name,
            )
            and node.value.func.id
            == "finalizar_resposta_rag"
        )
    ]

    assert len(finalized_returns) == 15


def test_retrieval_trace_fields_are_exposed():
    section = _answer_section()

    assert '"trace_id"' in section
    assert '"retrieval_trace"' in section

    assert (
        "retrieval_trace.to_dict()"
        in section
    )


def test_trace_is_finished_with_retrieval_results():
    section = _answer_section()

    assert (
        "retrieval_trace.finish("
        in section
    )

    assert (
        "results,"
        in section
    )

    assert (
        "search_mode=modo_busca"
        in section
    )


def test_finalizer_can_override_response_mode():
    section = _answer_section()

    assert (
        'trace_payload["search_mode"] = modo'
        in section
    )


def test_security_path_does_not_require_retrieval_trace():
    section = _answer_section()

    security_block = section[
        section.index(
            "resposta_seguranca ="
        ):
        section.index(
            "try:",
            section.index(
                "resposta_seguranca ="
            ),
        )
    ]

    assert (
        "return resposta_seguranca"
        in security_block
    )

    assert (
        "retrieval_trace"
        not in security_block
    )
