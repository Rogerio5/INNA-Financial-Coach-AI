from __future__ import annotations

from pathlib import Path
import ast


RAG_TOOLS_PATH = Path("src/agent_tools/rag_tools.py")

API_PATH = Path("api/main.py")


def _function_source(
    path: Path,
    function_name: str,
) -> str:
    source = path.read_text(
        encoding="utf-8-sig",
    )

    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)

    function = next(
        node
        for node in ast.walk(tree)
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name == function_name
        )
    )

    return "".join(lines[function.lineno - 1 : function.end_lineno])


def test_rag_tools_calls_answer_with_rag():
    section = _function_source(
        RAG_TOOLS_PATH,
        "consultar_rag_inna",
    )

    assert "resultado = answer_with_rag(" in section


def test_rag_tools_keeps_complete_raw_result():
    section = _function_source(
        RAG_TOOLS_PATH,
        "consultar_rag_inna",
    )

    assert "raw_result=resultado" in section


def test_rag_tools_preserves_raw_result_on_success():
    section = _function_source(
        RAG_TOOLS_PATH,
        "consultar_rag_inna",
    )

    success_position = section.index("return RagToolResult(\n            ok=True,")

    success_block = section[success_position : success_position + 700]

    assert "raw_result=resultado" in success_block


def test_rag_tools_preserves_raw_result_on_empty_answer():
    section = _function_source(
        RAG_TOOLS_PATH,
        "consultar_rag_inna",
    )

    empty_position = section.index('error_type="EmptyRagAnswer"')

    block_start = section.rfind(
        "return RagToolResult(",
        0,
        empty_position,
    )

    empty_block = section[block_start : empty_position + 300]

    assert "raw_result=resultado" in empty_block


def test_rag_tools_trace_is_implicitly_compatible():
    section = _function_source(
        RAG_TOOLS_PATH,
        "consultar_rag_inna",
    )

    assert "raw_result=resultado" in section

    assert "if not isinstance(resultado, dict):" in section


def test_api_calls_answer_with_rag():
    section = _function_source(
        API_PATH,
        "rag_ask",
    )

    assert "result = answer_with_rag(" in section


def test_api_returns_complete_rag_result():
    section = _function_source(
        API_PATH,
        "rag_ask",
    )

    assert "return result" in section


def test_api_logs_trace_id():
    section = _function_source(
        API_PATH,
        "rag_ask",
    )

    assert '"trace_id": result.get("trace_id")' in section


def test_api_logs_retrieval_trace():
    section = _function_source(
        API_PATH,
        "rag_ask",
    )

    assert '"retrieval_trace": result.get(' in section

    assert '"retrieval_trace"' in section


def test_api_preserves_legacy_result_implicitly():
    section = _function_source(
        API_PATH,
        "rag_ask",
    )

    assert "resposta=result.get(" in section

    assert '"modo": result.get("modo")' in section

    assert '"fontes": result.get("fontes", [])' in section

    assert "return result" in section


def test_api_trace_reads_are_optional():
    source = API_PATH.read_text(
        encoding="utf-8-sig",
    )

    tree = ast.parse(source)

    function = next(
        node
        for node in ast.walk(tree)
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name == "rag_ask"
        )
    )

    optional_fields = set()

    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue

        if not isinstance(
            node.func,
            ast.Attribute,
        ):
            continue

        if node.func.attr != "get":
            continue

        if not isinstance(
            node.func.value,
            ast.Name,
        ):
            continue

        if node.func.value.id != "result":
            continue

        if not node.args:
            continue

        field = node.args[0]

        if isinstance(field, ast.Constant) and isinstance(
            field.value,
            str,
        ):
            optional_fields.add(field.value)

    assert "trace_id" in optional_fields
    assert "retrieval_trace" in optional_fields
