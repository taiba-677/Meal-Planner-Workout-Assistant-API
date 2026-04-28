# from enum import Enum
# from pydantic import BaseModel
# import re

# class GoalEnum(str, Enum):
#     lose_weight = "Lose weight"
#     gain_muscle = "Gain muscle"
#     maintain = "Maintain"
#     eat_healthy = "Eat healthy"


# class GoalRequest(BaseModel):
#     goal: GoalEnum
#     body_metrics: str

from typing import Optional
from pydantic import BaseModel,Field,field_validator
import re
class MealRequest(BaseModel):
    goal: str = Field(..., description="Lose weight / Gain muscle / Maintain / Eat healthy")
    body_metrics: str = Field(..., description="Format: 170cm 70kg OR 5'9 65kg")
    activity_level: str = Field(..., description="Low / Moderate / Active")
    diet_type: str = Field(..., description="None / Halal / Vegetarian / Vegan / Keto")
    allergies: str = Field(..., description="Yes or No", example="Yes")
    allergy_items: str = Field("", description="Comma-separated foods if Yes", example="peanuts, dairy")
    meals_per_day: int = Field(..., description="Number of meals per day (e.g., 1 to 6)")

    medical_conditions: str = Field(
    ...,
    description="e.g. diabetes, high cholesterol, or 'none'"
)
    
    age: int = Field(..., description="Age in years (e.g. 25)")
    gender: str = Field(..., description="Male / Female / Prefer not to say")



    # optional you may delete this 
#     cuisine: Optional[str] = Field(..., description="Pakistani / Indian / Western / Middle Eastern / Mixed")
#     food_preference: Optional[str]  = Field(
#     ...,
#     description="Spicy / Mild / Sweet / Balanced / High Protein / Low Carb"
# )
#     budget: Optional[str] = Field(..., description="Low / Medium / High")