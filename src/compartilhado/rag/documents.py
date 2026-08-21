"""
Gerenciamento local de documentos RAG da INNA.

Responsabilidades:
- criar diretórios da base;
- validar extensões;
- gerar nomes seguros;
- salvar arquivos enviados;
- listar arquivos processados.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path("data/knowledge_base")
UPLOADS_DIR = BASE_DIR / "uploads"
CHUNKS_DIR = BASE_DIR / "chunks"
EMBEDDING_READY_DIR = BASE_DIR / "embedding_ready"

EXTENSOES_PERMITIDAS = {".md", ".txt"}


def garantir_diretorios_rag() -> dict[str, Path]:
    """
    Garante que as pastas locais da base RAG existam.
    """
    diretorios = {
        "base": BASE_DIR,
        "uploads": UPLOADS_DIR,
        "chunks": CHUNKS_DIR,
        "embedding_ready": EMBEDDING_READY_DIR,
    }

    for diretorio in diretorios.values():
        diretorio.mkdir(
            parents=True,
            exist_ok=True,
        )

    return diretorios


def validar_extensao_documento(
    nome_arquivo: str,
) -> str:
    """
    Valida a extensão do documento enviado.
    """
    suffix = Path(str(nome_arquivo or "")).suffix.lower()

    if suffix not in EXTENSOES_PERMITIDAS:
        permitidas = ", ".join(
            sorted(EXTENSOES_PERMITIDAS)
        )

        raise ValueError(
            f"Extensão não permitida: {suffix or 'sem extensão'}. "
            f"Permitidas: {permitidas}."
        )

    return suffix


def normalizar_nome_arquivo(
    nome_arquivo: str,
) -> str:
    """
    Remove caminhos, acentos e caracteres problemáticos.
    """
    nome = Path(str(nome_arquivo or "")).name

    if not nome:
        raise ValueError(
            "Nome do arquivo não informado."
        )

    suffix = validar_extensao_documento(nome)
    stem = Path(nome).stem

    stem = unicodedata.normalize(
        "NFKD",
        stem,
    ).encode(
        "ascii",
        "ignore",
    ).decode("ascii")

    stem = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        stem,
    )

    stem = re.sub(
        r"_+",
        "_",
        stem,
    ).strip("_")

    if not stem:
        stem = "documento"

    return f"{stem}{suffix}"


def gerar_nome_arquivo_salvo(
    nome_original: str,
    *,
    usar_timestamp: bool = True,
) -> str:
    """
    Gera um nome seguro para o arquivo salvo localmente.
    """
    nome_normalizado = normalizar_nome_arquivo(
        nome_original
    )

    if not usar_timestamp:
        return nome_normalizado

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return f"{timestamp}_{nome_normalizado}"


def salvar_documento_upload(
    nome_original: str,
    conteudo: bytes | bytearray | str,
    *,
    usar_timestamp: bool = True,
) -> dict:
    """
    Salva um documento enviado na pasta uploads.

    Retorna informações úteis para o dashboard e o banco.
    """
    diretorios = garantir_diretorios_rag()

    nome_salvo = gerar_nome_arquivo_salvo(
        nome_original,
        usar_timestamp=usar_timestamp,
    )

    caminho = diretorios["uploads"] / nome_salvo

    if isinstance(conteudo, str):
        conteudo_bytes = conteudo.encode("utf-8")
    elif isinstance(conteudo, bytearray):
        conteudo_bytes = bytes(conteudo)
    elif isinstance(conteudo, bytes):
        conteudo_bytes = conteudo
    else:
        raise TypeError(
            "O conteúdo deve ser bytes, bytearray ou str."
        )

    caminho.write_bytes(conteudo_bytes)

    return {
        "ok": True,
        "nome_original": Path(nome_original).name,
        "nome_salvo": nome_salvo,
        "caminho": caminho,
        "extensao": caminho.suffix.lower(),
        "tamanho_bytes": len(conteudo_bytes),
    }


def ler_documento_texto(
    caminho: str | Path,
) -> str:
    """
    Lê um documento de texto em UTF-8 com tolerância a erros.
    """
    caminho = Path(caminho)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Documento não encontrado: {caminho}"
        )

    return caminho.read_text(
        encoding="utf-8",
        errors="ignore",
    )


def listar_arquivos_rag(
    pasta: str | Path,
    *,
    padrao: str = "*",
    limite: int | None = None,
) -> list[Path]:
    """
    Lista arquivos locais por data de modificação decrescente.
    """
    pasta = Path(pasta)

    if not pasta.exists():
        return []

    arquivos = [
        arquivo
        for arquivo in pasta.glob(padrao)
        if arquivo.is_file()
        and arquivo.name != ".gitkeep"
    ]

    arquivos.sort(
        key=lambda arquivo: arquivo.stat().st_mtime,
        reverse=True,
    )

    if limite is not None:
        limite = max(0, int(limite))
        arquivos = arquivos[:limite]

    return arquivos


def listar_documentos_upload(
    *,
    limite: int | None = None,
) -> list[Path]:
    garantir_diretorios_rag()

    return listar_arquivos_rag(
        UPLOADS_DIR,
        limite=limite,
    )


def listar_arquivos_chunks(
    *,
    limite: int | None = None,
) -> list[Path]:
    garantir_diretorios_rag()

    return listar_arquivos_rag(
        CHUNKS_DIR,
        padrao="*.json",
        limite=limite,
    )


def listar_arquivos_embedding_ready(
    *,
    limite: int | None = None,
) -> list[Path]:
    garantir_diretorios_rag()

    return listar_arquivos_rag(
        EMBEDDING_READY_DIR,
        padrao="*.jsonl",
        limite=limite,
    )


def obter_resumo_arquivos_rag() -> dict[str, Any]:
    """
    Retorna contagens e arquivos recentes da base local.
    """
    uploads = listar_documentos_upload()
    chunks = listar_arquivos_chunks()
    embeddings = listar_arquivos_embedding_ready()

    return {
        "uploads_total": len(uploads),
        "chunks_total": len(chunks),
        "embedding_ready_total": len(embeddings),
        "uploads_recentes": uploads[:5],
        "chunks_recentes": chunks[:5],
        "embedding_ready_recentes": embeddings[:5],
    }


__all__ = [
    "BASE_DIR",
    "UPLOADS_DIR",
    "CHUNKS_DIR",
    "EMBEDDING_READY_DIR",
    "EXTENSOES_PERMITIDAS",
    "garantir_diretorios_rag",
    "validar_extensao_documento",
    "normalizar_nome_arquivo",
    "gerar_nome_arquivo_salvo",
    "salvar_documento_upload",
    "ler_documento_texto",
    "listar_arquivos_rag",
    "listar_documentos_upload",
    "listar_arquivos_chunks",
    "listar_arquivos_embedding_ready",
    "obter_resumo_arquivos_rag",
]
