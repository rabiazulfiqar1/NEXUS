from crewai import LLM
from app.core.config import (
    GROQ_API_KEY,
    GROQ_MODEL_LARGE,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)

def get_crew_llm() -> LLM:
    if GROQ_API_KEY:
        return LLM(
            model=GROQ_MODEL_LARGE,
            api_key=GROQ_API_KEY,
            temperature=0.3,
            max_tokens=2048,
            timeout=120,        
            max_retries=3,    
        )
    return LLM(
        model=OPENROUTER_MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
        temperature=0.3,
        max_tokens=2048,
        timeout=120,     
        max_retries=3,     
    )