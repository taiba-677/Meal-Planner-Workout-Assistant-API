from typing import Optional
from pydantic import BaseModel,Field,field_validator,ConfigDict
import re
class MealRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "goal": "lose weight",
                "body_metrics": "170cm 70kg",
                "activity_level": "moderate",
                "diet_type": "vegetarian",
                "allergies": "yes",
                "allergy_items": "peanuts, dairy",
                "meals_per_day": 3,
                "medical_conditions": "none",
                "age": 25,
                "gender": "female"
            }
        }
    )

    goal: str = Field(..., description="Lose weight / Gain muscle / Maintain / Eat healthy")
    body_metrics: str = Field(..., description="Format: 170cm 70kg OR 5'9 65kg")
    activity_level: str = Field(..., description="Low / Moderate / Active")
    diet_type: str = Field(..., description="None / Halal / Vegetarian / Vegan / Keto")
    allergies: str = Field(..., description="Yes or No", example="Yes")
    allergy_items: str = Field("", description="Comma-separated foods if Yes", example="peanuts, dairy")
    meals_per_day: int = Field(...,ge=1, le=6, example=3, description="Number of meals per day (e.g., 1 to 6)")

    medical_conditions: str = Field(
    ...,
    description="e.g. diabetes, high cholesterol, or 'none'"
)
    
    age: int = Field(..., description="Age in years (e.g. 25)" , ge=18, le=100, example=25)
    gender: str = Field(..., description="Male / Female / Prefer not to say")
    

    
    @field_validator("allergies")
    def validate_allergies(cls, v):
        if v.lower() not in ["yes", "no"]:
            raise ValueError("Allergies must be 'Yes' or 'No'")
        return v.lower()



