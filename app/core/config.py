import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

class Settings:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self._validate()

    def _validate(self):
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env file")

settings = Settings()