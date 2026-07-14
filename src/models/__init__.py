"""
Modelos de banco de dados da INNA Financial Coach AI.

Mantém compatibilidade com:
from src.models import DiagnosticoFinanceiro, FeedbackUsuario
"""

from .legacy import (
    DiagnosticoFinanceiro,
    FeedbackUsuario,
)

__all__ = [
    "DiagnosticoFinanceiro",
    "FeedbackUsuario",
]
