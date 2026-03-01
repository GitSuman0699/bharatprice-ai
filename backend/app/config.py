from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AWS
    aws_region: str = "ap-south-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # Amazon Bedrock
    bedrock_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"

    # DynamoDB
    dynamodb_users_table: str = "bharatprice-users"
    dynamodb_prices_table: str = "bharatprice-prices"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # data.gov.in API (AGMARKNET real mandi prices) — key must be in .env
    data_gov_api_key: str = ""

    # Feature flags
    use_local_data: bool = True  # Use seed data instead of DynamoDB (for dev)
    use_real_prices: bool = True  # Use real data.gov.in API for prices

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
