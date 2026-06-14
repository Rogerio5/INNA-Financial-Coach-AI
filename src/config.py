import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "inna-financial-coach-ai")
INNA_MOCK_MODE = os.getenv("INNA_MOCK_MODE", "true").lower() == "true"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
