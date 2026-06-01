from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Resale Radar API"
    database_url: str = "postgresql+psycopg://resale:resale@localhost:5432/resale"
    bot_token: str | None = None
    telegram_webhook_secret: str = "change-me"
    mini_app_url: str | None = None
    render_external_url: str | None = None
    support_username: str = "support"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    seed_demo_data: bool = True
    dev_default_telegram_id: int = Field(default=1001)

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        for origin in (self.public_app_url, self.render_external_url):
            if origin and origin not in origins:
                origins.append(origin)
        return origins

    @property
    def public_app_url(self) -> str:
        return self.mini_app_url or self.render_external_url or "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
