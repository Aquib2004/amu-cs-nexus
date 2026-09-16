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

    # Secrets are optional at this stage. Never commit real values.
    database_url: str | None = None
    llm_provider: str | None = None
    llm_api_key: str | None = None
    embedding_provider: str | None = None
    embedding_api_key: str | None = None
    redis_url: str | None = None


# A single, shared settings instance used across the application.
settings = Settings()
