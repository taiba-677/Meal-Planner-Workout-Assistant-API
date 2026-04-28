import os
from pathlib import Path
from dotenv import load_dotenv

# ✅ Load .env from the app directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self._validate()

    def _validate(self):
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env file")

settings = Settings()