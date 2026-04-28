from typing import Any

def build_prompt(data: dict) -> str:
    age = data["age"]
    h = data["height_cm"]
    w = data["weight_kg"]
    goal = data["goal"]
    activity_level = data["activity_level"]
    diet_type = data["diet_type"]
    meals_per_day = int(data['meals_per_day'])

    # 1. BMR Calculation (Mifflin-St Jeor Equation)
    gender_lower = data["gender"].lower()
    if gender_lower == "male":
        bmr = (10 * w) + (6.25 * h) - (5 * age) + 5
    elif gender_lower == "female":
        bmr = (10 * w) + (6.25 * h) - (5 * age) - 161
    else:
        # For 'prefer not to say', use the average of male and female BMR
        bmr = (10 * w) + (6.25 * h) - (5 * age) - 78

    # 2. TDEE Calculation (Conservative Multipliers)
    activity_factors = {
        "low": 1.15,
        "moderate": 1.35,
        "active": 1.55
    }
    tdee = round(bmr * activity_factors.get(activity_level, 1.35))

    # 3. Goal Adjustment (Percentage-based for safety)
    if goal == "lose_weight":
        target_cal = int(tdee * 0.80)  # 20% deficit is the "sweet spot"
    elif goal == "gain_muscle":
        target_cal = int(tdee * 1.10)  # 10% surplus for lean gain
    else:
        target_cal = tdee

    # 4. Dynamic Safety Floor
    min_cal = max(1500 if gender_lower == "male" else 1200, int(22 * w))
    if target_cal < min_cal:
        target_cal = min_cal

    # 5. Protein & Macro Balancing
    protein_multiplier = 1.8 if goal in ["lose_weight", "gain_muscle"] else 1.2
    protein_target = round(w * protein_multiplier)

    # 6. Comprehensive Macro Logic for All Diet Types
    carbs_target = 0
    fat_target = 0
    
    diet_lower = diet_type.lower()
    
    if diet_lower == "keto":
        carbs_target = 30  # Strict Keto
        fat_cal = target_cal - (protein_target * 4) - (carbs_target * 4)
        fat_target = round(max(fat_cal / 9, 30))
        
    elif diet_lower == "low carb":
        carbs_target = 100
        fat_cal = target_cal - (protein_target * 4) - (carbs_target * 4)
        fat_target = round(max(fat_cal / 9, 30))
        
    elif diet_lower in ["vegan", "vegetarian"]:
        # Standard balance but with a reminder for plant protein
        fat_target = round((target_cal * 0.25) / 9) # Slightly lower fat
        carbs_target = round((target_cal - (protein_target * 4) - (fat_target * 9)) / 4)
        
    else:
        # Default (None, Halal, etc.): Balanced 30% Fat
        fat_target = round((target_cal * 0.30) / 9)
        carbs_target = round((target_cal - (protein_target * 4) - (fat_target * 9)) / 4)

    # 7. Hydration (35ml per kg)
    hydration = round(w * 35 / 1000, 1)

    # 8. Per-meal targets for the LLM to follow
    protein_per_meal = round(protein_target / meals_per_day, 1)
    cal_per_meal = round(target_cal / meals_per_day, 1)

    # 9. Formatting constraints
    allergy_str = ", ".join(data.get("allergy_items", [])) or "none"
    conditions = data.get("medical_conditions", "none")
    if isinstance(conditions, list):
        conditions = ", ".join(conditions)

    return f"""
You are a WORLD-CLASS NUTRITIONIST and DIETITIAN. 

Your task is to create a scientifically accurate, highly realistic daily meal plan for a patient with the following profile:

=====================
PATIENT PROFILE
=====================
- Gender: {data['gender']}
- Age: {age}
- Height: {h} cm
- Weight: {w} kg
- Goal: {goal}
- Activity: {activity_level}
- Diet Type: {diet_type}
- Allergies: {allergy_str}
- Medical Conditions: {conditions}

=====================
NUTRITIONAL TARGETS (STRICT)
=====================
- TOTAL DAILY CALORIES: {target_cal} kcal (Tolerance: ±50 kcal)
- TOTAL DAILY PROTEIN: {protein_target}g (Tolerance: ±5g)
- TOTAL DAILY CARBS: {carbs_target}g (Tolerance: ±10g)
- TOTAL DAILY FAT: {fat_target}g (Tolerance: ±10g)
- MEALS PER DAY: {meals_per_day}
- TARGET PER MEAL: ~{cal_per_meal} kcal and ~{protein_per_meal}g protein.

=====================
DIETARY CONSTRAINTS
=====================
- DIET TYPE: Follow {diet_type} rules strictly.
- ALLERGIES: ABSOLUTELY NO {allergy_str}.
- REAL FOOD ONLY: No powders, supplements, or shakes. Use whole foods only.
- VARIETY: Ensure a mix of vegetables, complex carbs, and healthy fats.

=====================
EXECUTION STEPS
=====================
1. NUTRITION AUDIT: For every food item you select, calculate its calories and protein based on the portion size.
2. SUMMATION: Sum the calories and protein for all items in a meal to get 'meal_totals'.
3. FINAL VALIDATION: Sum all 'meal_totals'. If they do not match the Daily Targets ({target_cal} kcal, {protein_target}g protein, {carbs_target}g carbs, {fat_target}g fat), adjust the portions until they do.
4. JSON GENERATION: Output the final plan in the exact JSON format below.

=====================
OUTPUT FORMAT (JSON ONLY)
=====================
- Output ONLY the JSON object. 
- NO markdown code blocks. 
- NO preamble or postscript.
- Ensure all numbers are integers or floats as shown.

{{
  "summary": {{
    "target_calories": {target_cal},
    "target_protein_g": {protein_target},
    "target_carbs_g": {carbs_target},
    "target_fat_g": {fat_target},
    "notes": "Provide 2-3 sentences of professional dietary advice specific to this goal."
  }},
  "meals": [
    {{
      "meal_number": 1,
      "meal_name": "Breakfast",
      "suggested_time": "08:00 AM",
      "items": [
        {{
          "food": "Exact food name (e.g. Grilled Chicken Breast)",
          "portion": "Exact weight/size (e.g. 150g or 2 large eggs)",
          "notes": "Why this food was chosen",
          "calories": 250,
          "protein_g": 35,
          "carbs_g": 0,
          "fat_g": 12
        }}
      ],
      "meal_totals": {{
        "calories": 250,
        "protein_g": 35,
        "carbs_g": 0,
        "fat_g": 12
      }}
    }}
  ],
  "hydration": "Drink {hydration} liters of water throughout the day.",
  "nutrition_breakdown": {{
    "total_calories": 0,
    "total_protein_g": 0,
    "total_carbs_g": 0,
    "total_fat_g": 0,
    "accuracy_check": {{
      "calorie_difference": 0,
      "protein_difference": 0,
      "status": "Verified"
    }}
  }}
}}

(Note: In the 'nutrition_breakdown', you MUST sum the calories and protein from all meals you generated and provide those ACTUAL totals. Then, calculate the difference from the targets provided above.)
"""