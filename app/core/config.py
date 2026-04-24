import os
from dotenv import load_dotenv

load_dotenv()

def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

JOB_SEARCH_API = os.getenv("JOB_SEARCH_API")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
LLM_USE_MOCK = _to_bool(os.getenv("LLM_USE_MOCK"), default=True)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").strip().lower()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b").strip()

CRON_QUERIES = [
    "software engineering Jobs in Pakistan",
    # "data science Jobs in Pakistan",
    # "machine learning Jobs in Pakistan",
    # "backend developer Jobs in Pakistan",
    # "frontend developer Jobs in Pakistan",
    # "cybersecurity Jobs in Pakistan",
]
COUNTRY="pk"
EMPLOYMENT_TYPES="PARTTIME,INTERN"

ALLOWED_FILE_TYPES = ['application/pdf']

MATCH_THRESHOLD = 0.4
MATCH_COUNT=5

