"""
Central configuration for the support bot.

All values are read from environment variables so the same code can run
locally, in Docker, or in CI without changes. See .env.example for the
full list of variables.
"""
from dotenv import load_dotenv
load_dotenv()
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # Which LLM provider powers the Support and Escalation agents.
    # "openai"  -> requires OPENAI_API_KEY
    # "gemini"  -> requires GEMINI_API_KEY
    # "mock"    -> no API key needed, returns canned responses (used in CI/tests)
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    # How many knowledge-base chunks the retrieval agent returns per query.
    top_k: int = int(os.getenv("RAG_TOP_K", "3"))

    # Below this similarity score, the retrieval agent reports "no match",
    # which the orchestrator uses to decide whether to escalate.
    similarity_threshold: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.08"))

    knowledge_base_dir: str = os.getenv(
        "KB_DIR", os.path.join(os.path.dirname(__file__), "data")
    )


settings = Settings()
