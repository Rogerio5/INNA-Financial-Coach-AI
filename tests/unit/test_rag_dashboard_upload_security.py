from __future__ import annotations

from pathlib import Path


DASHBOARD_PATH = Path(
    "src/dashboard.py"
)


def _load_dashboard_source() -> str:
    return DASHBOARD_PATH.read_text(
        encoding="utf-8-sig",
    )


def _load_upload_flow() -> str:
    source = _load_dashboard_source()

    start = source.index(
        "def render_upload_documentos_rag"
    )

    return source[
        start:
        start + 9000
    ]


def test_dashboard_requires_safe_document_before_write():
    upload_flow = _load_upload_flow()

    security_position = upload_flow.index(
        "security_result = require_safe_rag_document"
    )

    write_position = upload_flow.index(
        "final_path.write_bytes(content_bytes)"
    )

    assert security_position < write_position


def test_dashboard_handles_document_security_error():
    upload_flow = _load_upload_flow()

    assert (
        "except RagDocumentSecurityError as exc:"
        in upload_flow
    )

    assert (
        "upload_rag_t('security_rejection')"
        in upload_flow
    )


def test_dashboard_stops_after_security_rejection():
    upload_flow = _load_upload_flow()

    rejection_start = upload_flow.index(
        "except RagDocumentSecurityError as exc:"
    )

    rejection_block = upload_flow[
        rejection_start:
        rejection_start + 500
    ]

    assert "return" in rejection_block


def test_dashboard_does_not_ignore_utf8_errors():
    upload_flow = _load_upload_flow()

    assert (
        'content_bytes.decode("utf-8")'
        in upload_flow
    )

    assert (
        'content_bytes.decode('
        '"utf-8", errors="ignore")'
        not in upload_flow
    )


def test_dashboard_exposes_security_metadata():
    upload_flow = _load_upload_flow()

    assert (
        "security_result.size_bytes"
        in upload_flow
    )

    assert (
        "security_result.content_hash"
        in upload_flow
    )


def test_dashboard_imports_security_contract():
    upload_flow = _load_upload_flow()

    assert (
        "require_safe_rag_document"
        in upload_flow
    )

    assert (
        "RagDocumentSecurityError"
        in upload_flow
    )
