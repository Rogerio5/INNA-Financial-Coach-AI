import json

from src.services.rag.chunking import (
    criar_payload_chunks,
    dividir_texto_em_chunks,
    limpar_texto_documento,
    salvar_chunks_documento,
)


def classificar_teste(texto):
    texto = texto.lower()

    if "pix" in texto:
        return "pix"

    if "reserva" in texto:
        return "reserva_financeira"

    return "geral"


def test_limpar_texto_documento():
    texto = "Linha 1\tcom espaço\r\n\r\n\r\nLinha 2"

    resultado = limpar_texto_documento(texto)

    assert "\t" not in resultado
    assert "\r" not in resultado
    assert "\n\n\n" not in resultado


def test_dividir_por_secoes_markdown():
    texto = """
# Guia

## Pix

Confira o aplicativo oficial.

## Reserva

Guarde um valor compatível com o orçamento.
"""

    chunks = dividir_texto_em_chunks(
        texto,
        tamanho_chunk=650,
    )

    assert len(chunks) == 2
    assert "# Guia" in chunks[0]
    assert "## Pix" in chunks[0]
    assert "## Reserva" in chunks[1]


def test_criar_payload_com_categoria():
    chunks = [
        "# Guia\n\n## Pix\nConfira o aplicativo.",
        "# Guia\n\n## Reserva\nCrie o hábito.",
    ]

    payload = criar_payload_chunks(
        nome_arquivo="guia.md",
        chunks=chunks,
        classificar_chunk=classificar_teste,
    )

    assert payload["total_chunks"] == 2
    assert payload["chunks"][0]["metadata"]["categoria"] == "pix"
    assert payload["chunks"][1]["metadata"]["categoria"] == "reserva_financeira"


def test_salvar_json_e_jsonl(tmp_path):
    chunks_dir = tmp_path / "chunks"
    embedding_dir = tmp_path / "embedding_ready"

    texto = """
# Guia

## Pix

Confira o aplicativo oficial.

## Reserva

Crie uma pequena reserva.
"""

    json_path, chunks, jsonl_path = salvar_chunks_documento(
        nome_arquivo="guia.md",
        texto=texto,
        classificar_chunk=classificar_teste,
        chunks_dir=chunks_dir,
        embedding_ready_dir=embedding_dir,
    )

    assert json_path.exists()
    assert jsonl_path.exists()
    assert len(chunks) == 2

    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert payload["total_chunks"] == 2

    linhas = jsonl_path.read_text(encoding="utf-8").strip().splitlines()

    assert len(linhas) == 2

    primeira_linha = json.loads(linhas[0])

    assert "chunk_id" in primeira_linha
    assert "texto" in primeira_linha
    assert "metadata" in primeira_linha
