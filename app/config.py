from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./sessionbook.db"
    PORT: int = 8000
    ENV: str = "development"
    PUBLIC_API_BASE_URL: str = ""
    ASSEMBLYAI_API_KEY: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}

    @model_validator(mode="after")
    def use_local_database_for_development(self) -> "Settings":
        if (
            self.ENV == "development"
            and self.DATABASE_URL.startswith("postgresql")
            and ("@localhost:" in self.DATABASE_URL or "@127.0.0.1:" in self.DATABASE_URL)
        ):
            self.DATABASE_URL = "sqlite+aiosqlite:///./sessionbook.db"
        return self


settings = Settings()
