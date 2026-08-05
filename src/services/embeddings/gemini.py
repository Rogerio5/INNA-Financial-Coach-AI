"""
Serviço de embeddings Gemini da INNA Financial Coach AI.

Utiliza o SDK atual google-genai.

Responsabilidades:
- carregar a chave da API com segurança;
- gerar embeddings de documentos;
- gerar embeddings de consultas;
- preservar o modelo gemini-embedding-001;
- preservar vetores com 3072 dimensões;
- validar o retorno antes de enviar ao pgvector.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


MODELO_EMBEDDING = "gemini-embedding-001"
MODELO_EMBEDDING_BANCO = "models/gemini-embedding-001"
DIMENSOES_EMBEDDING = 3072

TASK_RETRIEVAL_DOCUMENT = "RETRIEVAL_DOCUMENT"
TASK_RETRIEVAL_QUERY = "RETRIEVAL_QUERY"


class GeminiEmbeddingConfigurationError(RuntimeError):
    """Erro de configuração do serviço de embeddings."""


class GeminiEmbeddingGenerationError(RuntimeError):
    """Erro ocorrido durante a geração do embedding."""


def carregar_variaveis_ambiente() -> None:
    """
    Carrega o arquivo .env quando ele existir.

    Em produção, Render, Docker ou Cloud podem fornecer
    as variáveis diretamente no ambiente.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    env_path = Path(".env")

    if env_path.exists():
        load_dotenv(
            dotenv_path=env_path,
            override=False,
        )


def obter_api_key_gemini() -> str:
    """
    Retorna a chave Gemini configurada.

    Aceita:
    - GEMINI_API_KEY
    - GOOGLE_API_KEY
    """
    carregar_variaveis_ambiente()

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise GeminiEmbeddingConfigurationError(
            "GEMINI_API_KEY ou GOOGLE_API_KEY não encontrada."
        )

    return api_key.strip()


def criar_cliente_gemini():
    """
    Cria um cliente utilizando o SDK google-genai.
    """
    try:
        from google import genai
    except ImportError as exc:
        raise GeminiEmbeddingConfigurationError(
            "Pacote google-genai não instalado. Execute: pip install -U google-genai"
        ) from exc

    return genai.Client(api_key=obter_api_key_gemini())


def _normalizar_texto(texto: Any) -> str:
    """
    Normaliza e valida o texto recebido.
    """
    texto_normalizado = str(texto or "").strip()

    if not texto_normalizado:
        raise ValueError("Não é possível gerar embedding de um texto vazio.")

    return texto_normalizado


def _validar_task_type(task_type: str) -> str:
    """
    Restringe o serviço aos tipos utilizados pelo RAG da INNA.
    """
    task_type = str(task_type or "").upper().strip()

    permitidos = {
        TASK_RETRIEVAL_DOCUMENT,
        TASK_RETRIEVAL_QUERY,
    }

    if task_type not in permitidos:
        raise ValueError(
            f"task_type inválido: {task_type}. Permitidos: {sorted(permitidos)}"
        )

    return task_type


def gerar_embedding_gemini(
    texto: Any,
    *,
    task_type: str = TASK_RETRIEVAL_DOCUMENT,
    modelo: str = MODELO_EMBEDDING,
    dimensoes: int = DIMENSOES_EMBEDDING,
) -> list[float]:
    """
    Gera um embedding com Gemini.

    Para documentos:
        task_type="RETRIEVAL_DOCUMENT"

    Para perguntas de busca:
        task_type="RETRIEVAL_QUERY"
    """
    texto_normalizado = _normalizar_texto(texto)
    task_type = _validar_task_type(task_type)

    dimensoes = int(dimensoes)

    if dimensoes != DIMENSOES_EMBEDDING:
        raise ValueError(
            "A INNA está configurada para 3072 dimensões. "
            "Alterar esse valor exige migração do pgvector."
        )

    try:
        from google.genai import types

        client = criar_cliente_gemini()

        resultado = client.models.embed_content(
            model=modelo,
            contents=texto_normalizado,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=dimensoes,
            ),
        )

        embeddings = getattr(
            resultado,
            "embeddings",
            None,
        )

        if not embeddings:
            raise GeminiEmbeddingGenerationError(
                "A API Gemini não retornou embeddings."
            )

        valores = getattr(
            embeddings[0],
            "values",
            None,
        )

        if not valores:
            raise GeminiEmbeddingGenerationError(
                "O embedding retornado não possui valores."
            )

        vetor = [float(valor) for valor in valores]

        if len(vetor) != dimensoes:
            raise GeminiEmbeddingGenerationError(
                "Dimensão inesperada no embedding: "
                f"esperado={dimensoes}, recebido={len(vetor)}."
            )

        return vetor

    except (
        GeminiEmbeddingConfigurationError,
        GeminiEmbeddingGenerationError,
        ValueError,
    ):
        raise

    except Exception as exc:
        raise GeminiEmbeddingGenerationError(
            f"Não foi possível gerar o embedding Gemini: {type(exc).__name__}: {exc}"
        ) from exc


def gerar_embedding_documento(
    texto: Any,
) -> list[float]:
    """
    Gera embedding para chunks armazenados no pgvector.
    """
    return gerar_embedding_gemini(
        texto,
        task_type=TASK_RETRIEVAL_DOCUMENT,
    )


def gerar_embedding_consulta(
    texto: Any,
) -> list[float]:
    """
    Gera embedding para perguntas utilizadas na busca semântica.
    """
    return gerar_embedding_gemini(
        texto,
        task_type=TASK_RETRIEVAL_QUERY,
    )


def obter_configuracao_embedding() -> dict:
    """
    Retorna configuração pública e não sensível do serviço.
    """
    return {
        "modelo": MODELO_EMBEDDING,
        "modelo_banco": MODELO_EMBEDDING_BANCO,
        "dimensoes": DIMENSOES_EMBEDDING,
        "sdk": "google-genai",
    }


__all__ = [
    "MODELO_EMBEDDING",
    "MODELO_EMBEDDING_BANCO",
    "DIMENSOES_EMBEDDING",
    "TASK_RETRIEVAL_DOCUMENT",
    "TASK_RETRIEVAL_QUERY",
    "gerar_embedding_gemini",
    "gerar_embedding_documento",
    "gerar_embedding_consulta",
    "obter_configuracao_embedding",
]
