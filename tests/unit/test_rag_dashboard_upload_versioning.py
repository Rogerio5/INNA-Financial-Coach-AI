from __future__ import annotations

from pathlib import Path


DASHBOARD_PATH = Path(
    "src/dashboard.py"
)


def _upload_flow() -> str:
    source = DASHBOARD_PATH.read_text(
        encoding="utf-8-sig",
    )

    start = source.index(
        "def render_upload_documentos_rag"
    )

    try:
        end = source.index(
            "\ndef ",
            start + len(
                "def render_upload_documentos_rag"
            ),
        )
    except ValueError:
        end = len(source)

    return source[start:end]


def test_versioning_happens_before_file_write():
    flow = _upload_flow()

    version_position = flow.index(
        "create_document_version_from_context"
    )

    write_position = flow.index(
        "final_path.write_bytes(content_bytes)"
    )

    assert version_position < write_position


def test_dashboard_queries_existing_versions():
    flow = _upload_flow()

    assert (
        "buscar_contexto_versionamento_rag"
        in flow
    )

    assert (
        "versioning_lookup.get("
        in flow
    )

    assert (
        '"contexto"'
        in flow
    )


def test_dashboard_rejects_duplicate_document():
    flow = _upload_flow()

    assert (
        "except RagDuplicateDocumentError as exc:"
        in flow
    )

    duplicate_start = flow.index(
        "except RagDuplicateDocumentError as exc:"
    )

    block = flow[
        duplicate_start:
        duplicate_start + 300
    ]

    assert "return" in block


def test_dashboard_sends_version_metadata():
    flow = _upload_flow()

    for field in (
        "document_version.logical_name",
        "document_version.content_hash",
        "document_version.version",
        "document_version.root_document_id",
        "document_version.previous_document_id",
    ):
        assert field in flow


def test_dashboard_displays_version():
    flow = _upload_flow()

    assert (
        "Versão: {document_version.version}"
        in flow
    )
