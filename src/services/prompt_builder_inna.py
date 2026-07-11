"""
Adaptador de compatibilidade do Prompt Builder da INNA.

A implementação real está em:

src/services/prompts/builder.py
"""

try:
    from services.prompts.builder import montar_prompt_inna
except ImportError:
    from src.services.prompts.builder import montar_prompt_inna


__all__ = [
    "montar_prompt_inna",
]
