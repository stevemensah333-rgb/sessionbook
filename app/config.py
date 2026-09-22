from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./sessionbook.db"
    PORT: int = 8000
    ENV: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
