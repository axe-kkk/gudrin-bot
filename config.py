# config.py

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../gudrin/.env", env_file_encoding="utf-8")
    bot_token: str = Field(alias="BOT_TOKEN")
    db_url: str = Field(alias="DB_URL")
    admin_ids: list[str] = Field(alias="ADMIN_IDS")
    bot_username: str = Field(alias="BOT_USERNAME")


settings = Settings()
