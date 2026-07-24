import os
from dataclasses import dataclass
from dotenv import load_dotenv

from src.services.llm.model_registry import DEFAULT_TEXT_MODEL


load_dotenv()


def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in ("true", "1", "yes", "sim")


@dataclass
class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "inna-financial-coach-ai")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    INNA_APP_NAME: str = os.getenv("INNA_APP_NAME", "INNA Financial Coach AI")
    INNA_NOME: str = os.getenv("INNA_NOME", "INNA")
    INNA_TITULO: str = os.getenv("INNA_TITULO", "Educadora Financeira com IA Generativa")
    INNA_MOCK_MODE: bool = get_bool_env("INNA_MOCK_MODE", True)

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", DEFAULT_TEXT_MODEL)

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:Engenharia10@localhost:5432/inna_db",
    )

    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    INTERACTIONS_LOG_FILE: str = os.getenv("INTERACTIONS_LOG_FILE", "data/interacoes.csv")
    FEEDBACK_FILE: str = os.getenv("FEEDBACK_FILE", "data/feedbacks.csv")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

# Compatibilidade com arquivos antigos do projeto
INNA_MOCK_MODE = settings.INNA_MOCK_MODE
GEMINI_API_KEY = settings.GEMINI_API_KEY
GEMINI_MODEL = settings.GEMINI_MODEL
DATABASE_URL = settings.DATABASE_URL
