# Application configuration, loaded from environment variables.
#
# pydantic-settings reads values from the environment and from a local
# `.env` file (which is git-ignored). Fields map to variable names by
# default; e.g. `database_url` reads DATABASE_URL.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    project_name: str = "AMUCS Nexus"
    version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    # Secrets are optional; never commit real values.
    database_url: str | None = None
    # yourobo LLM: set LLM_PROVIDER=gemini and a key (LLM_API_KEY or the
    # GEMINI_API_KEY alias below) to enable the real Gemini-backed assistant.
    # Without a key the chatbot uses the offline, no-fabrication extractive
    # fallback, so the app still works on a fresh clone.
    llm_provider: str | None = None
    llm_api_key: str | None = None
    # Alias used by the older AMU.ai chatbot and by Google's docs. We accept it
    # so an existing GEMINI_API_KEY works without renaming anything.
    gemini_api_key: str | None = None
    llm_model: str = "gemini-3.6-flash"
    # How long a single provider call may take, and how many EXTRA attempts we
    # make after it fails. Both are bounded on purpose: an unbounded retry loop
    # would hold the request open and amplify load on a struggling provider.
    llm_timeout_seconds: float = 20.0
    llm_max_retries: int = 2
    embedding_provider: str | None = None
    embedding_api_key: str | None = None
    redis_url: str | None = None

    # Comma-separated list of allowed browser origins for CORS.
    cors_origins: str = "http://localhost:3000"


# A single, shared settings instance used across the application.
settings = Settings()