import os

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "groq" or "gemini"
DB_URL = os.getenv("DB_URL", "sqlite:///./aegis.db")

BLOCK_THRESHOLD = float(os.getenv("AEGIS_BLOCK_THRESHOLD", "0.7"))
FLAG_THRESHOLD = float(os.getenv("AEGIS_FLAG_THRESHOLD", "0.4"))

# Comma-separated list of allowed frontend origins for CORS. Defaults to the
# local Vite dev server; set to the deployed frontend's origin(s) in prod.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
