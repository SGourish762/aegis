import os

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "groq" or "gemini"
DB_URL = os.getenv("DB_URL", "sqlite:///./aegis.db")

BLOCK_THRESHOLD = float(os.getenv("AEGIS_BLOCK_THRESHOLD", "0.7"))
FLAG_THRESHOLD = float(os.getenv("AEGIS_FLAG_THRESHOLD", "0.4"))
