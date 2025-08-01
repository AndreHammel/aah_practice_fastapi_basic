from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )
    DATABASE: str
    SECRET_KEY: str
    ALGORITHMS: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str
