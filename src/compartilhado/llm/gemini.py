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


from src.observability.resilience_tracing import (
    get_shared_resilience_runtime,
    traced_resilience_operation,
)
from src.compartilhado.resilience.deadline import DeadlineBudget
from src.compartilhado.resilience.policies import (
    GEMINI_TEXT_GENERATION_POLICY,
)
from src.compartilhado.llm.model_registry import (
    DEFAULT_TEXT_MODEL,
    LLMRole,
    get_model_for_role,
)

MODELO_TEXTO_PADRAO = DEFAULT_TEXT_MODEL

DEFAULT_TEXT_GENERATION_TIMEOUT_MS = 15000
DEFAULT_TEXT_GENERATION_TOTAL_DEADLINE_MS = 25000
TEXT_GENERATION_DEADLINE_RESERVE_SECONDS = 0.25


def _ler_inteiro_ambiente(
    name: str,
    default: int,
    *,
    minimum: int,
    maximum: int,
) -> int:
    carregar_variaveis_ambiente()

    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    try:
        value = int(
            str(raw_value).strip()
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise GeminiTextConfigurationError(
            f"{name} possui valor inválido."
        ) from exc

    if (
        value < minimum
        or value > maximum
    ):
        raise GeminiTextConfigurationError(
            f"{name} deve estar entre "
            f"{minimum} e {maximum}."
        )

    return value


def _obter_timeout_geracao_ms() -> int:
    return _ler_inteiro_ambiente(
        "INNA_TEXT_GENERATION_TIMEOUT_MS",
        DEFAULT_TEXT_GENERATION_TIMEOUT_MS,
        minimum=1000,
        maximum=120000,
    )


def _obter_deadline_total_geracao_ms() -> int:
    return _ler_inteiro_ambiente(
        "INNA_TEXT_GENERATION_TOTAL_DEADLINE_MS",
        DEFAULT_TEXT_GENERATION_TOTAL_DEADLINE_MS,
        minimum=1000,
        maximum=180000,
    )


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


def criar_cliente_gemini(
    *,
    timeout_ms: int | None = None,
):
    """
    Cria cliente google-genai com timeout explícito.

    O SDK não recebe política própria de retry:
    a INNA é a autoridade de retentativa.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise GeminiTextConfigurationError(
            "Pacote google-genai não instalado. "
            "Execute: pip install -U google-genai"
        ) from exc

    resolved_timeout_ms = int(
        timeout_ms
        if timeout_ms is not None
        else _obter_timeout_geracao_ms()
    )

    if resolved_timeout_ms <= 0:
        raise GeminiTextConfigurationError(
            "Timeout Gemini deve ser positivo."
        )

    http_options = types.HttpOptions(
        timeout=resolved_timeout_ms,
        retry_options=None,
    )

    return genai.Client(
        api_key=obter_api_key_gemini(),
        http_options=http_options,
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
    usage_out: dict[str, int] | None = None,
) -> str:
    """
    Gera texto Gemini com resiliência controlada pela INNA.

    O serviço possui:
    - timeout HTTP por tentativa;
    - deadline total;
    - retry controlado;
    - circuit breaker dedicado;
    - observabilidade segura;
    - propagação opcional de usage/tokens.
    """
    if usage_out is not None:
        usage_out.clear()

    prompt_normalizado = _normalizar_prompt(
        prompt
    )

    temperatura = max(
        0.0,
        min(
            float(temperatura),
            2.0,
        ),
    )

    max_tokens = max(
        128,
        min(
            int(max_tokens),
            8192,
        ),
    )

    timeout_ms = (
        _obter_timeout_geracao_ms()
    )

    total_deadline_ms = (
        _obter_deadline_total_geracao_ms()
    )

    deadline_budget = DeadlineBudget(
        total_deadline_ms / 1000.0,
        reserve_seconds=(
            TEXT_GENERATION_DEADLINE_RESERVE_SECONDS
        ),
    )

    try:
        from google.genai import types

        modelo_resolvido = (
            str(
                modelo
                or ""
            ).strip()
            or get_model_for_role(role)
        )

        # Gemini 3.x possui contrato de geração diferente.
        #
        # Não enviamos parâmetros de amostragem legados
        # (temperature/top_p/top_k) nem thinking_budget.
        # O modelo usa seu thinking_level padrão.
        #
        # Para Gemini 2.5 e anteriores preservamos o
        # contrato histórico da INNA.
        modelo_normalizado = (
            modelo_resolvido
            .strip()
            .lower()
        )

        if modelo_normalizado.startswith(
            "gemini-3"
        ):
            config = types.GenerateContentConfig(
                max_output_tokens=max_tokens,
            )
        else:
            config = types.GenerateContentConfig(
                temperature=temperatura,
                max_output_tokens=max_tokens,
                thinking_config=(
                    types.ThinkingConfig(
                        thinking_budget=0
                    )
                ),
            )

        resilience_runtime = (
            get_shared_resilience_runtime()
        )

        def generate_attempt():
            attempt_timeout_seconds = (
                deadline_budget.clamp_timeout(
                    timeout_ms / 1000.0
                )
            )

            attempt_timeout_ms = max(
                1,
                int(
                    attempt_timeout_seconds
                    * 1000
                ),
            )

            client = criar_cliente_gemini(
                timeout_ms=attempt_timeout_ms
            )

            return (
                executar_generate_content_observado(
                    client,
                    modelo=modelo_resolvido,
                    contents=prompt_normalizado,
                    config=config,
                    operacao=(
                        "llm_service_generate"
                    ),
                    origem=(
                        "services.llm.gemini"
                    ),
                    metadados={
                        "temperatura": temperatura,
                        "max_output_tokens": (
                            max_tokens
                        ),
                        "thinking_budget": 0,
                    },
                )
            )

        with traced_resilience_operation(
            GEMINI_TEXT_GENERATION_POLICY
        ):
            response = (
                resilience_runtime.execute(
                    policy=(
                        GEMINI_TEXT_GENERATION_POLICY
                    ),
                    operation=generate_attempt,
                    deadline_budget=(
                        deadline_budget
                    ),
                    minimum_retry_attempt_seconds=(
                        0.50
                    ),
                )
            )

        if usage_out is not None:
            try:
                from src.observability.llm_costs import (
                    extrair_tokens_resposta,
                )

                extracted_usage = (
                    extrair_tokens_resposta(
                        response
                    )
                )

                usage_out.update(
                    {
                        "tokens_entrada": int(
                            extracted_usage.get(
                                "tokens_entrada",
                                0,
                            )
                            or 0
                        ),
                        "tokens_saida": int(
                            extracted_usage.get(
                                "tokens_saida",
                                0,
                            )
                            or 0
                        ),
                        "tokens_totais": int(
                            extracted_usage.get(
                                "tokens_totais",
                                0,
                            )
                            or 0
                        ),
                    }
                )

            except Exception:
                # Telemetria de custo nunca pode
                # afetar a resposta funcional.
                usage_out.clear()

        resposta = _extrair_texto_resposta(
            response
        )

        # Resposta inválida não é falha transitória.
        if not resposta:
            raise GeminiTextGenerationError(
                "O Gemini não retornou "
                "uma resposta textual."
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
            "Não foi possível gerar a "
            "resposta Gemini "
            f"({type(exc).__name__})."
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
            "message": (
                "Falha no serviço textual Gemini "
                f"({type(exc).__name__})."
            ),
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
