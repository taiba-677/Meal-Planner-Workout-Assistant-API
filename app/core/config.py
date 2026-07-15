import os
from pathlib import Path
from dotenv import load_dotenv

# ✅ Load .env from the app directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    def __init__(self):
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/meal_planner_api",
        )
        self.jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "temporary_default_secret_key_for_dev_mode_change_me")
        self._validate()

    def _validate(self):
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env file")
        if not self.database_url:
            raise ValueError("DATABASE_URL is not set in .env file")
        if not self.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY is not set in .env file")


settings = Settings()