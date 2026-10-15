from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./dev.db"
    jwt_secret: str  # required: no default, so the app refuses to start without it
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30


settings = Settings()
