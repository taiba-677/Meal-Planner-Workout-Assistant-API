def calculate_nutrition_targets(data: dict) -> dict:
    """
    data must already be the normalized dict from validate_all():
    goal, height_cm, weight_kg, activity_level, diet_type, age, gender, meals_per_day
    """
    h, w, age = data["height_cm"], data["weight_kg"], data["age"]
    goal, activity_level, diet_type = data["goal"], data["activity_level"], data["diet_type"]
    gender_lower = data["gender"].lower()

    # BMR
    if gender_lower == "male":
        bmr = (10 * w) + (6.25 * h) - (5 * age) + 5
    elif gender_lower == "female":
        bmr = (10 * w) + (6.25 * h) - (5 * age) - 161
    else:
        bmr = (10 * w) + (6.25 * h) - (5 * age) - 78

    activity_factors = {"low": 1.15, "moderate": 1.35, "active": 1.55}
    tdee = round(bmr * activity_factors.get(activity_level, 1.35))

    if goal == "lose_weight":
        target_cal = int(tdee * 0.80)
    elif goal == "gain_muscle":
        target_cal = int(tdee * 1.10)
    else:
        target_cal = tdee

    min_cal = max(1500 if gender_lower == "male" else 1200, int(22 * w))
    target_cal = max(target_cal, min_cal)

    protein_multiplier = 1.8 if goal in ["lose_weight", "gain_muscle"] else 1.2
    protein_target = round(w * protein_multiplier)

    if diet_type == "keto":
        carbs_target = 30
        fat_cal = target_cal - (protein_target * 4) - (carbs_target * 4)
        fat_target = round(max(fat_cal / 9, 30))
    elif diet_type in ["vegan", "vegetarian"]:
        fat_target = round((target_cal * 0.25) / 9)
        carbs_target = round((target_cal - (protein_target * 4) - (fat_target * 9)) / 4)
    else:
        fat_target = round((target_cal * 0.30) / 9)
        carbs_target = round((target_cal - (protein_target * 4) - (fat_target * 9)) / 4)

    hydration = round(w * 35 / 1000, 1)
    meals_per_day = data["meals_per_day"]
    protein_per_meal = round(protein_target / meals_per_day, 1)
    cal_per_meal = round(target_cal / meals_per_day, 1)

    return {
        "target_calories": target_cal,
        "target_protein_g": protein_target,
        "target_carbs_g": carbs_target,
        "target_fat_g": fat_target,
        "hydration_l": hydration,
        "cal_per_meal": cal_per_meal,
        "protein_per_meal": protein_per_meal,
    }
