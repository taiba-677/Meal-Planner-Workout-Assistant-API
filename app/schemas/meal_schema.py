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


from enum import Enum
from pydantic import BaseModel,Field
import re
class MealRequest(BaseModel):
    # goal: str
    # body_metrics: str
    # activity_level: str
    # diet_type: str
    goal: str = Field(..., description="Lose weight / Gain muscle / Maintain / Eat healthy")
    body_metrics: str = Field(..., description="Format: 170cm 70kg OR 5'9 65kg")
    activity_level: str = Field(..., description="Low / Moderate / Active")
    diet_type: str = Field(..., description="None / Halal / Vegetarian / Vegan / Keto")
    allergies: str = Field(..., description="Yes or No", example="Yes")
    allergy_items: str = Field("", description="Comma-separated foods if Yes", example="peanuts, dairy")