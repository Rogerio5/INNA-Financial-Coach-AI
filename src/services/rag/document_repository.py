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
"""

import sys

from src.compartilhado.rag.persistencia import (
    document_repository as _implementation,
)

sys.modules[__name__] = _implementation
