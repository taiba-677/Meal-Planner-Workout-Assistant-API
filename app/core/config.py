from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "AI Meal Planner API"


settings = Settings()