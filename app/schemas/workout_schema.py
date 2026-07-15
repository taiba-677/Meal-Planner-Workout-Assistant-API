from pydantic import BaseModel, ConfigDict, Field


class WorkoutRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "meal_plan_id": 1,
                "fitness_level": "Intermediate",
                "days_available": 4,
                "equipment": "Dumbbells",
                "training_style": "Mixed",
                "injuries_or_limitations": "none",
            }
        }
    )

    meal_plan_id: int = Field(
        ...,
        description="ID returned by /generate-meal-plan — links this workout to that meal plan.",
        gt=0,
    )
    fitness_level: str = Field(
        ...,
        description="Beginner / Intermediate / Advanced",
    )
    days_available: int = Field(
        ...,
        ge=1,
        le=7,
        description="Number of training days per week (1–7).",
    )
    equipment: str = Field(
        ...,
        description="None / Dumbbells / Barbell / Resistance Bands / Gym / Bodyweight",
    )
    training_style: str = Field(
        ...,
        description="Strength / Cardio / Mixed / HIIT / Yoga / Calisthenics",
    )
    injuries_or_limitations: str = Field(
        default="none",
        description="e.g. 'bad knee, lower back pain' or 'none'",
    )
