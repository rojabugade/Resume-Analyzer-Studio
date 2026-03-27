from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Agent System"
    environment: str = "dev"
    log_level: str = "INFO"
    model_name: str = "gpt-4o-mini"
    openai_api_key: str = ""
    enable_trace: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
