from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    DEBUG: bool = False
    BOT_TOKEN_DEV: str | None = None
    BOT_TOKEN_PROD: str | None = None
    widgets_dir: Path = Field(default=PROJECT_ROOT / "widgets", alias="WIDGETS_DIR")
    root_telegram_id: int = Field(default=596169119, alias="ROOT_TELEGRAM_ID")

    bot_token: str = ""

    @model_validator(mode="after")
    def resolve_bot_token(self) -> "Settings":
        token = self.BOT_TOKEN_DEV if self.DEBUG else self.BOT_TOKEN_PROD
        if not token:
            mode = "DEV" if self.DEBUG else "PROD"
            raise ValueError(f"BOT_TOKEN_{mode} не задан в .env, а DEBUG={self.DEBUG}")
        self.bot_token = token
        return self


settings = Settings()
