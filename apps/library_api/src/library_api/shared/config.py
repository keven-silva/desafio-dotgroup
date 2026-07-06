from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://dotgroup:dotgroup@localhost:5432/library"
    log_level: str = "INFO"
    log_json: bool = True
    default_loan_period_days: int = 14

    # lista separada por vírgula (ex: "https://app.com,https://admin.app.com"); "*" libera geral
    cors_allowed_origins: str = "*"

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        if self.cors_allowed_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
