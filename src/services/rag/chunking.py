"""
Processamento de textos e chunks da base RAG da INNA.

Responsabilidades:
- limpar o texto dos documentos;
- preservar títulos e seções Markdown;
- dividir textos longos em chunks;
- criar metadados;
- gerar JSON de chunks;
- gerar JSONL pronto para embeddings.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Callable


ChunkClassifier = Callable[[str], str]

CHUNKS_DIR_PADRAO = Path("data/knowledge_base/chunks")
EMBEDDING_READY_DIR_PADRAO = Path("data/knowledge_base/embedding_ready")
UPLOADS_DIR_PADRAO = Path("data/knowledge_base/uploads")


def limpar_texto_documento(
    texto: str | None,
) -> str:
    """
    Normaliza espaços, tabulações e quebras de linha.
    """
    if not texto:
        return ""

    texto = str(texto)
    texto = texto.replace("\r\n", "\n")
    texto = texto.replace("\r", "\n")
    texto = texto.replace("\t", " ")

    linhas = []

    for linha in texto.split("\n"):
        linha = linha.strip()

        if not linha:
            linhas.append("")
            continue

        linha = re.sub(r"\s+", " ", linha)
        linhas.append(linha)

    texto_limpo = "\n".join(linhas)
    texto_limpo = re.sub(r"\n{3,}", "\n\n", texto_limpo)

    return texto_limpo.strip()


def dividir_texto_em_chunks(
    texto: str | None,
    tamanho_chunk: int = 650,
    sobreposicao: int = 0,
) -> list[str]:
    """
    Divide um documento preservando títulos Markdown.

    A sobreposição é opcional e permanece desativada por padrão,
    mantendo o comportamento atual da INNA.
    """
    texto = limpar_texto_documento(texto)

    if not texto:
        return []

    tamanho_chunk = max(100, int(tamanho_chunk))
    sobreposicao = max(0, int(sobreposicao))

    linhas = texto.split("\n")
    titulo_documento = ""
    secoes = []
    secao_atual = []

    for linha in linhas:
        linha_limpa = linha.strip()

        if linha_limpa.startswith("# ") and not titulo_documento:
            titulo_documento = linha_limpa
            continue

        if linha_limpa.startswith("## "):
            if secao_atual:
                secoes.append("\n".join(secao_atual).strip())

            secao_atual = [linha_limpa]

        elif linha_limpa:
            secao_atual.append(linha_limpa)

    if secao_atual:
        secoes.append("\n".join(secao_atual).strip())

    if not secoes:
        secoes = [texto]

    chunks = []

    for secao in secoes:
        chunk_completo = (
            f"{titulo_documento}\n\n{secao}" if titulo_documento else secao
        ).strip()

        if len(chunk_completo) <= tamanho_chunk:
            chunks.append(chunk_completo)
            continue

        palavras = chunk_completo.split()
        parte = ""

        for palavra in palavras:
            candidato = f"{parte} {palavra}".strip()

            if len(candidato) <= tamanho_chunk:
                parte = candidato
                continue

            if parte:
                chunks.append(parte.strip())

            if sobreposicao > 0 and parte:
                trecho_overlap = parte[-sobreposicao:]
                parte = f"{trecho_overlap} {palavra}".strip()
            else:
                parte = palavra

        if parte:
            chunks.append(parte.strip())

    return [chunk for chunk in chunks if chunk.strip()]


def criar_payload_chunks(
    nome_arquivo: str,
    chunks: list[str],
    *,
    classificar_chunk: ChunkClassifier,
    idioma: str = "pt",
    origem: str = "upload_usuario",
) -> dict:
    """
    Cria o payload estruturado dos chunks.
    """
    if not callable(classificar_chunk):
        raise ValueError("A função classificar_chunk é obrigatória.")

    base_name = Path(nome_arquivo).stem

    itens = []

    for indice, chunk in enumerate(chunks, start=1):
        categoria = classificar_chunk(chunk) or "geral"

        itens.append(
            {
                "chunk_id": f"{base_name}_chunk_{indice}",
                "chunk_index": indice,
                "texto": chunk,
                "metadata": {
                    "documento_origem": nome_arquivo,
                    "fonte": str(UPLOADS_DIR_PADRAO / nome_arquivo),
                    "categoria": categoria,
                    "origem": origem,
                    "idioma": idioma,
                    "tipo": "documento_upload",
                    "fase": "7.10_chunking_modular",
                },
            }
        )

    return {
        "documento_origem": nome_arquivo,
        "total_chunks": len(itens),
        "status": "chunks_gerados",
        "preparado_para_embeddings": True,
        "chunks": itens,
    }


def salvar_chunks_documento(
    nome_arquivo: str,
    texto: str,
    *,
    classificar_chunk: ChunkClassifier,
    tamanho_chunk: int = 650,
    sobreposicao: int = 0,
    idioma: str = "pt",
    chunks_dir: Path | str = CHUNKS_DIR_PADRAO,
    embedding_ready_dir: Path | str = (EMBEDDING_READY_DIR_PADRAO),
) -> tuple[Path, list[str], Path]:
    """
    Processa o texto e salva:

    - JSON completo de chunks;
    - JSONL pronto para embeddings.
    """
    nome_arquivo = Path(nome_arquivo).name

    if not nome_arquivo:
        raise ValueError("Nome do arquivo não informado.")

    chunks_dir = Path(chunks_dir)
    embedding_ready_dir = Path(embedding_ready_dir)

    chunks_dir.mkdir(parents=True, exist_ok=True)
    embedding_ready_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    chunks = dividir_texto_em_chunks(
        texto,
        tamanho_chunk=tamanho_chunk,
        sobreposicao=sobreposicao,
    )

    if not chunks:
        raise ValueError("O documento não gerou chunks válidos.")

    base_name = Path(nome_arquivo).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_path = chunks_dir / f"{timestamp}_{base_name}_chunks.json"

    embedding_ready_path = (
        embedding_ready_dir / f"{timestamp}_{base_name}_embedding_ready.jsonl"
    )

    payload = criar_payload_chunks(
        nome_arquivo=nome_arquivo,
        chunks=chunks,
        classificar_chunk=classificar_chunk,
        idioma=idioma,
    )

    output_path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    with embedding_ready_path.open(
        "w",
        encoding="utf-8",
    ) as arquivo_jsonl:
        for item in payload["chunks"]:
            linha = {
                "chunk_id": item["chunk_id"],
                "documento_origem": nome_arquivo,
                "chunk_index": item["chunk_index"],
                "texto": item["texto"],
                "metadata": item["metadata"],
            }

            arquivo_jsonl.write(
                json.dumps(
                    linha,
                    ensure_ascii=False,
                )
                + "\n"
            )

    return (
        output_path,
        chunks,
        embedding_ready_path,
    )


__all__ = [
    "limpar_texto_documento",
    "dividir_texto_em_chunks",
    "criar_payload_chunks",
    "salvar_chunks_documento",
]
