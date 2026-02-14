import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    database_url: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_required: bool
    api_rate_limit_per_minute: int


def get_settings() -> Settings:
    environment = os.getenv("ENVIRONMENT", "development")
    if environment not in {"development", "staging", "production"}:
        raise ValueError("ENVIRONMENT must be development|staging|production")

    rate_limit = int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "60"))
    if rate_limit <= 0:
        raise ValueError("API_RATE_LIMIT_PER_MINUTE must be > 0")

    return Settings(
        app_name=os.getenv("APP_NAME", "Forge Framework API"),
        environment=environment,
        database_url=os.getenv(
            "DATABASE_URL", "postgresql+psycopg2://forge:forge@localhost:5432/forge"
        ),
        jwt_secret=os.getenv("JWT_SECRET", "dev-secret-change-me"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        jwt_required=os.getenv("JWT_REQUIRED", "false").lower() == "true",
        api_rate_limit_per_minute=rate_limit,
    )
