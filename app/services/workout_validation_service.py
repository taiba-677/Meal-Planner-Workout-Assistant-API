ALLOWED_FITNESS_LEVELS = {"beginner", "intermediate", "advanced"}
ALLOWED_EQUIPMENT = {"none", "dumbbells", "barbell", "resistance bands", "gym", "bodyweight"}
ALLOWED_TRAINING_STYLES = {"strength", "cardio", "mixed", "hiit", "yoga", "calisthenics"}


def validate_workout_input(data: dict) -> dict:
    errors = {}

    fitness_level = str(data.get("fitness_level", "")).strip().lower()
    if fitness_level not in ALLOWED_FITNESS_LEVELS:
        errors["fitness_level"] = "Please select: Beginner, Intermediate, or Advanced."

    days = data.get("days_available")
    if not isinstance(days, int) or not (1 <= days <= 7):
        errors["days_available"] = "Please enter a number of training days between 1 and 7."

    raw_equipment = str(data.get("equipment", "")).strip()
    equipment_list = [e.strip().lower() for e in raw_equipment.split(",") if e.strip()]
    invalid_equipment = [e for e in equipment_list if e not in ALLOWED_EQUIPMENT]
    if not equipment_list or invalid_equipment:
        errors["equipment"] = "Please select valid equipment options (None, Dumbbells, Barbell, Resistance Bands, Gym, Bodyweight). You can combine multiple: e.g. 'Dumbbells, Resistance Bands'."
    else:
        equipment = ", ".join(equipment_list)

    training_style = str(data.get("training_style", "")).strip().lower()
    if training_style not in ALLOWED_TRAINING_STYLES:
        errors["training_style"] = "Please select a valid training style (Strength, Cardio, Mixed, HIIT, Yoga, Calisthenics)."

    if errors:
        return {"errors": errors}

    return {
        "fitness_level": fitness_level,
        "days_available": days,
        "equipment": equipment,
        "training_style": training_style,
        "injuries_or_limitations": data.get("injuries_or_limitations", "none"),
        "meal_plan_id": data.get("meal_plan_id"),
    }
