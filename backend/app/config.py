from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Groq API
    groq_api_key: str = ""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Security
    api_secret_key: str = ""  # Static API key for /api/* routes (leave blank to disable)
    allowed_hosts: str = "localhost"  # Comma-separated trusted hostnames

    # data.gov.in API (AGMARKNET real mandi prices) — key must be in .env
    data_gov_api_key: str = ""

    # Feature flags
    use_local_data: bool = True  # Use seed data instead of DynamoDB (for dev)
    use_real_prices: bool = True  # Use real data.gov.in API for prices

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Allow extra env vars (e.g. BENCHMARK_API_URL) without crashing


@lru_cache()
def get_settings() -> Settings:
    return Settings()
