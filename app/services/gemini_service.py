from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

def generate_meal(prompt: str):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return str(e)