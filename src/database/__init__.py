"""
Camada de banco de dados da INNA Financial Coach AI.

Mantém compatibilidade com os imports antigos:
from src.database import get_db_session, init_db
"""

from .legacy import (
    Base,
    DATABASE_URL,
    SessionLocal,
    engine,
    get_db_session,
    init_db,
)

__all__ = [
    "DATABASE_URL",
    "engine",
    "SessionLocal",
    "Base",
    "init_db",
    "get_db_session",
]
