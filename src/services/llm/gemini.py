"""
Serviço de geração textual Gemini da INNA Financial Coach AI.

Utiliza o SDK atual google-genai.

Responsabilidades:
- carregar a chave da API;
- criar o cliente Gemini;
- gerar respostas textuais;
- validar o retorno do modelo;
- centralizar configurações;
- evitar dependência direta do Gemini no dashboard.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
try:
    from observability.llm_tracking import (
        executar_generate_content_observado,
    )
except ImportError:
    from src.observability.llm_tracking import (
        executar_generate_content_observado,
    )


from src.services.llm.model_registry import (
    DEFAULT_TEXT_MODEL,
    LLMRole,
    get_model_for_role,
)

MODELO_TEXTO_PADRAO = DEFAULT_TEXT_MODEL


class GeminiTextConfigurationError(RuntimeError):
    """Erro de configuração do serviço Gemini."""


class GeminiTextGenerationError(RuntimeError):
    """Erro durante a geração da resposta Gemini."""


def carregar_variaveis_ambiente() -> None:
    """
    Carrega o arquivo .env local quando disponível.
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
    Obtém a chave Gemini sem expor seu conteúdo.
    """
    carregar_variaveis_ambiente()

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not api_key:
        raise GeminiTextConfigurationError(
            "GEMINI_API_KEY ou GOOGLE_API_KEY não encontrada."
        )

    return api_key.strip()


def criar_cliente_gemini():
    """
    Cria um cliente utilizando google-genai.
    """
    try:
        from google import genai
    except ImportError as exc:
        raise GeminiTextConfigurationError(
            "Pacote google-genai não instalado. "
            "Execute: pip install -U google-genai"
        ) from exc

    return genai.Client(
        api_key=obter_api_key_gemini()
    )


def _normalizar_prompt(prompt: Any) -> str:
    """
    Valida e normaliza o prompt antes do envio.
    """
    prompt_normalizado = str(prompt or "").strip()

    if not prompt_normalizado:
        raise ValueError(
            "Não é possível gerar resposta com prompt vazio."
        )

    return prompt_normalizado


def _extrair_texto_resposta(response: Any) -> str:
    """
    Extrai o texto do retorno do SDK.
    """
    texto = getattr(response, "text", None)

    if texto:
        return str(texto).strip()

    candidatos = getattr(response, "candidates", None) or []

    for candidato in candidatos:
        content = getattr(candidato, "content", None)
        parts = getattr(content, "parts", None) or []

        trechos = []

        for part in parts:
            texto_part = getattr(part, "text", None)

            if texto_part:
                trechos.append(str(texto_part))

        if trechos:
            return "\n".join(trechos).strip()

    return ""


def gerar_texto_gemini(
    prompt: Any,
    *,
    modelo: str | None = None,
    role: LLMRole | str = LLMRole.DEFAULT,
    temperatura: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """
    Gera uma resposta textual utilizando Gemini.

    Args:
        prompt:
            Prompt final construído pela INNA.

        modelo:
            Modelo Gemini utilizado.

        temperatura:
            Controla variação da resposta.

        max_tokens:
            Limite aproximado da saída.
    """
    prompt_normalizado = _normalizar_prompt(prompt)

    temperatura = max(
        0.0,
        min(float(temperatura), 2.0),
    )

    max_tokens = max(
        128,
        min(int(max_tokens), 8192),
    )

    try:
        from google.genai import types

        modelo_resolvido = (
            str(modelo or "").strip()
            or get_model_for_role(role)
        )

        client = criar_cliente_gemini()

        config = types.GenerateContentConfig(
            temperature=temperatura,
            max_output_tokens=max_tokens,
            thinking_config=types.ThinkingConfig(
                thinking_budget=0
            ),
        )

        response = executar_generate_content_observado(
            client,
            modelo=modelo_resolvido,
            contents=prompt_normalizado,
            config=config,
            operacao="llm_service_generate",
            origem="services.llm.gemini",
            metadados={
                "temperatura": temperatura,
                "max_output_tokens": max_tokens,
                "thinking_budget": 0,
            },
        )

        resposta = _extrair_texto_resposta(response)

        if not resposta:
            raise GeminiTextGenerationError(
                "O Gemini não retornou uma resposta textual."
            )

        return resposta

    except (
        GeminiTextConfigurationError,
        GeminiTextGenerationError,
        ValueError,
    ):
        raise

    except Exception as exc:
        raise GeminiTextGenerationError(
            "Não foi possível gerar a resposta Gemini: "
            f"{type(exc).__name__}: {exc}"
        ) from exc


def testar_servico_gemini() -> dict:
    """
    Executa um teste simples sem expor informações sensíveis.
    """
    try:
        resposta = gerar_texto_gemini(
            "Responda apenas com: INNA funcionando.",
            temperatura=0.0,
            max_tokens=50,
        )

        return {
            "ok": True,
            "message": "Serviço textual Gemini validado.",
            "response": resposta,
            "model": get_model_for_role(
                LLMRole.DEFAULT
            ),
            "sdk": "google-genai",
        }

    except Exception as exc:
        return {
            "ok": False,
            "message": str(exc),
            "response": "",
            "model": get_model_for_role(
                LLMRole.DEFAULT
            ),
            "sdk": "google-genai",
        }


__all__ = [
    "MODELO_TEXTO_PADRAO",
    "gerar_texto_gemini",
    "testar_servico_gemini",
]
