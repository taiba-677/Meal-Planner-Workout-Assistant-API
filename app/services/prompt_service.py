import time
from typing import Any


def build_prompt(data: dict, targets: dict) -> str:
    age            = data["age"]
    h              = data["height_cm"]
    w              = data["weight_kg"]
    goal           = data["goal"]
    activity_level = data["activity_level"]
    diet_type      = data["diet_type"]
    meals_per_day  = data["meals_per_day"]

    target_cal      = targets["target_calories"]
    protein_target  = targets["target_protein_g"]
    carbs_target    = targets["target_carbs_g"]
    fat_target      = targets["target_fat_g"]
    hydration       = targets["hydration_l"]
    cal_per_meal    = targets["cal_per_meal"]
    protein_per_meal= targets["protein_per_meal"]

    allergy_items = data.get("allergy_items", [])
    allergy_str   = ", ".join(allergy_items) if allergy_items else "none"

    conditions    = data.get("medical_conditions", [])
    condition_str = ", ".join(conditions) if conditions else "none"

    
    entropy = int(time.time())

    return f"""
[request_id:{entropy}]
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
- Medical Conditions: {condition_str}

=====================
NUTRITIONAL TARGETS (STRICT — ALL FOUR MACROS)
=====================
- TOTAL DAILY CALORIES : {target_cal} kcal  (tolerance ±{round(target_cal * 0.03)} kcal, i.e. 3%)
- TOTAL DAILY PROTEIN  : {protein_target}g  (tolerance ±{round(protein_target * 0.03)}g,   i.e. 3%)
- TOTAL DAILY CARBS    : {carbs_target}g    (tolerance ±{round(carbs_target * 0.03)}g,   i.e. 3%)
- TOTAL DAILY FAT      : {fat_target}g      (tolerance ±{round(fat_target * 0.03)}g,   i.e. 3%)
- MEALS PER DAY        : {meals_per_day} (generate EXACTLY {meals_per_day} meals)
- TARGET PER MEAL      : ~{cal_per_meal} kcal and ~{protein_per_meal}g protein

=====================
DIETARY CONSTRAINTS
=====================
- DIET TYPE : Follow {diet_type} rules strictly.
- ALLERGIES : ABSOLUTELY NO {allergy_str}.
  IMPORTANT — Cross-check EVERY ingredient, including non-obvious hidden sources
  (e.g. nutritional yeast, tahini, coconut milk, soy sauce, ghee) against the
  allergy list above before including any food item. If an ingredient appears on
  the allergy list, remove the entire dish and replace it.
- REAL FOOD ONLY : No powders, supplements, or shakes. Whole foods only.
- VARIETY : Ensure a mix of vegetables, complex carbs, and healthy fats.

=====================
CALORIE COMPUTATION RULE (MANDATORY)
=====================
For EVERY food item, you MUST compute calories DIRECTLY from its macros using
the standard 4/4/9 rule:

  calories = (protein_g × 4) + (carbs_g × 4) + (fat_g × 9)

Do NOT invent calorie values independently. Always derive calories FROM the
stated macros. Round to the nearest whole number. Do not let per-item calorie values drift from macro-derived calories.

=====================
EXECUTION STEPS
=====================
1. SELECT foods appropriate for the diet type and patient profile.
   For each `allergy_items` entry, exclude the ingredient and any common derivatives/cross-contaminants (e.g., dairy -> whey, casein, ghee; gluten -> wheat, barley, malt; peanuts -> peanut oil, peanut flour). State compliance explicitly in `notes` only when relevant, don't rely on assumption.
2. FOR EACH ITEM: state protein_g, carbs_g, fat_g, then compute calories
   using the 4/4/9 rule above. Never state calories first.
3. SUM each meal's items to get meal_totals (calories, protein, carbs, fat).
4. SUM all meal_totals to get the daily grand total.
5. VERIFY: check that EACH of the four daily totals is within 3% of its target.
   After assigning macros to each food item, sum all protein_g, carbs_g, fat_g, and calories across all meals. The sum MUST exactly equal target_protein_g, target_carbs_g, target_fat_g, and target_calories. If it does not, adjust portion sizes of one or more items and recompute before returning the final JSON.
6. SELF-CHECK: Before finalizing output, verify:
   (a) sum of meal_totals.calories == nutrition_breakdown.total_calories == target_calories, and same for protein/carbs/fat.
   (b) No allergy item or its derivatives appear in any food/portion/notes field.
   (c) All foods are compliant with the specified diet type.
   If any check fails, silently correct the plan and re-verify before responding.
7. OUTPUT the final JSON exactly as specified below. No markdown, no preamble.

=====================
CRITICAL: DO NOT SELF-GRADE
=====================
Do NOT include any "accuracy_check", "verified", or "status" field in your
output. The backend independently recomputes all sums and attaches its own
accuracy report. Any self-reported verification from you will be discarded.
`nutrition_breakdown` must be calculated by summing the `meal_totals` array — do not generate it independently. It must match `target_*` fields exactly (within 1 unit rounding tolerance).

=====================
OUTPUT FORMAT (JSON ONLY)
=====================
- Output ONLY the JSON object.
- NO markdown code blocks.
- NO preamble or postscript.
- The "meals" array MUST contain EXACTLY {meals_per_day} meal objects.

{{
  "meals": [
    {{
      "meal_number": 1,
      "meal_name": "Breakfast",
      "suggested_time": "08:00 AM",
      "items": [
        {{
          "food": "Exact food name",
          "portion": "Weight/size (e.g. 150g)",
          "notes": "Why chosen",
          "protein_g": 35,
          "carbs_g": 0,
          "fat_g": 12,
          "calories": 188
        }}
      ],
      "meal_totals": {{
        "calories": 188,
        "protein_g": 35,
        "carbs_g": 0,
        "fat_g": 12
      }}
    }},
    "... (Repeat for exactly {meals_per_day} meals total)"
  ],
  "hydration": "Drink {hydration} liters of water throughout the day.",
  "nutrition_breakdown": {{
    "total_calories": 0,
    "total_protein_g": 0,
    "total_carbs_g": 0,
    "total_fat_g": 0
  }},
  "summary": {{
    "target_calories": {target_cal},
    "target_protein_g": {protein_target},
    "target_carbs_g": {carbs_target},
    "target_fat_g": {fat_target},
    "notes": "Provide 2-3 sentences of professional dietary advice specific to this goal."
  }}
}}

(Note: Fill nutrition_breakdown with the ACTUAL sums of ALL {meals_per_day} meal_totals.
Do NOT add any accuracy_check block — the backend handles that.)
"""
