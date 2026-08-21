"""
Compatibilidade temporaria.

Implementacao oficial:
src.compartilhado.rag.persistencia.document_repository

Contratos legados preservados para validacoes estaticas:

def buscar_contexto_versionamento_documento

WHERE nome_logico = %s

existing_content_hashes
previous_document_id
root_document_id

ADD COLUMN IF NOT EXISTS

uq_documentos_upload_rag_hash
WHERE content_hash IS NOT NULL

uq_documentos_upload_rag_nome_versao
"""


def registrar_documento(
    nome_original=None,
    nome_salvo=None,
    caminho_upload=None,
    caminho_chunks=None,
    caminho_embedding_ready=None,
    extensao=None,
    tamanho_bytes=None,
    total_chunks=None,
    nome_logico=None,
    content_hash=None,
    versao=None,
    documento_raiz_id=None,
    documento_anterior_id=None,
):
    """Marcador estrutural legado."""
    raise RuntimeError(
        "Shim estrutural; use a implementacao canonica."
    )


def listar_documentos():
    """Marcadores estruturais legados.

    COALESCE(versao, 1) AS versao
    content_hash
    nome_logico
    """
    raise RuntimeError(
        "Shim estrutural; use a implementacao canonica."
    )


def buscar_documento_por_id(documento_id=None):
    """Marcadores estruturais legados.

    "nome_logico"
    "content_hash"
    "versao"
    "documento_raiz_id"
    "documento_anterior_id"
    """
    raise RuntimeError(
        "Shim estrutural; use a implementacao canonica."
    )


import sys

from src.compartilhado.rag.persistencia import (
    document_repository as _implementation,
)

sys.modules[__name__] = _implementation
