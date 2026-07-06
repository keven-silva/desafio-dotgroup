from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Desafio Dotgroup"
    database_url: str = "postgresql+psycopg://postgres@localhost:5432/desafio_dotgroup"
    auto_create_schema: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()
