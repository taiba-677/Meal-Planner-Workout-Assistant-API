# import google.generativeai as genai
# from app.core.config import settings

# genai.configure(api_key=settings.gemini_api_key)

# model = genai.GenerativeModel(
#     "gemini-2.5-flash-lite",
#     generation_config={
#         "temperature": 0.2  # 🔥 important for consistency
#     }
# )

# def generate_meal(prompt: str):
#     response = model.generate_content(prompt)
#     return response.text




from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

def generate_meal(prompt: str):
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )
    return response.text