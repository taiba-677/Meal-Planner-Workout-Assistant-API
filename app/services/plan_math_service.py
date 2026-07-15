"""
plan_math_service.py
────────────────────
Server-side math validation for meal plans and workout plans.

ALL tolerance thresholds live here — change them in ONE place only.

MEAL PLAN TOLERANCES:
  DAILY_MACRO_TOLERANCE_PCT  = 0.03  (3% on total daily macros vs. target)
  ITEM_CALORIE_TOLERANCE_PCT = 0.05  (5% on per-item calorie vs. 4/4/9 rule)

WORKOUT PLAN:
  No numeric tolerances — totals are hard-recomputed, not approximated.
"""


DAILY_MACRO_TOLERANCE_PCT:  float = 0.03  
ITEM_CALORIE_TOLERANCE_PCT: float = 0.05   


# ─────────────────────────────────────────────────────────────────────────────
# MEAL PLAN VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def validate_meal_plan_math(meal_plan: dict, targets: dict) -> dict:
    """
    Independently recompute all sums and verify them against targets.
    Returns a dict that REPLACES whatever accuracy_check the LLM produced.

    Parameters
    ----------
    meal_plan : dict
        The raw parsed output from Gemini (contains "meals" list).
    targets : dict
        Server-computed targets: target_calories, target_protein_g,
        target_carbs_g, target_fat_g.

    Returns
    -------
    dict with keys:
        status          : "Verified" | "Discrepancy Found"
        computed_totals : the independently recomputed macro sums
        differences     : per-macro deviation from target
        failed_checks   : list of check names that failed
    """
    meals = meal_plan.get("meals", [])
    target_cal     = targets.get("target_calories",  0)
    target_protein = targets.get("target_protein_g", 0)
    target_carbs   = targets.get("target_carbs_g",   0)
    target_fat     = targets.get("target_fat_g",     0)

    # ── Recompute daily totals from meal_totals ───────────────────────────────
    computed_calories = sum(m.get("meal_totals", {}).get("calories",  0) for m in meals)
    computed_protein  = sum(m.get("meal_totals", {}).get("protein_g", 0) for m in meals)
    computed_carbs    = sum(m.get("meal_totals", {}).get("carbs_g",   0) for m in meals)
    computed_fat      = sum(m.get("meal_totals", {}).get("fat_g",     0) for m in meals)

    failed_checks: list[str] = []

    
    def _macro_ok(computed: float, target: float, label: str) -> bool:
        if target == 0:
            return True
        ok = abs(computed - target) <= target * DAILY_MACRO_TOLERANCE_PCT
        if not ok:
            failed_checks.append(f"daily_{label}_off_by_{abs(computed - target):.1f}")
        return ok

    _macro_ok(computed_calories, target_cal,     "calories")
    _macro_ok(computed_protein,  target_protein, "protein_g")
    _macro_ok(computed_carbs,    target_carbs,   "carbs_g")
    _macro_ok(computed_fat,      target_fat,     "fat_g")   # <-- the original bug

   
    for meal in meals:
        for item in meal.get("items", []):
            p = item.get("protein_g", 0)
            c = item.get("carbs_g",   0)
            f = item.get("fat_g",     0)
            stated_cal   = item.get("calories", 0)
            expected_cal = p * 4 + c * 4 + f * 9

            if expected_cal == 0:
                continue

            if abs(stated_cal - expected_cal) > expected_cal * ITEM_CALORIE_TOLERANCE_PCT:
                food_label = item.get("food", "unknown_item").replace(" ", "_")[:40]
                failed_checks.append(f"item_4_4_9_mismatch_{food_label}_stated={stated_cal}_expected={round(expected_cal)}")

    return {
        "status": "Verified" if not failed_checks else "Discrepancy Found",
        "computed_totals": {
            "total_calories":  computed_calories,
            "total_protein_g": computed_protein,
            "total_carbs_g":   computed_carbs,
            "total_fat_g":     computed_fat,
        },
        "differences": {
            "calorie_difference": round(computed_calories - target_cal, 1),
            "protein_difference": round(computed_protein  - target_protein, 1),
            "carbs_difference":   round(computed_carbs    - target_carbs,   1),
            "fat_difference":     round(computed_fat      - target_fat,     1),
        },
        "failed_checks": failed_checks,
    }


def overwrite_nutrition_breakdown(meal_plan: dict, math_result: dict) -> dict:
    """
    Injects the server-computed accuracy_check into the meal_plan dict,
    overwriting whatever the LLM placed there.
    Returns the mutated meal_plan dict.
    """
    if "nutrition_breakdown" not in meal_plan:
        meal_plan["nutrition_breakdown"] = {}

    nb = meal_plan["nutrition_breakdown"]
    totals = math_result["computed_totals"]

    # Overwrite totals with server-computed values
    nb["total_calories"]  = totals["total_calories"]
    nb["total_protein_g"] = totals["total_protein_g"]
    nb["total_carbs_g"]   = totals["total_carbs_g"]
    nb["total_fat_g"]     = totals["total_fat_g"]

    return meal_plan


# ─────────────────────────────────────────────────────────────────────────────
# WORKOUT PLAN VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def validate_workout_plan_math(workout_plan: dict, equipment_input: str) -> dict:
    """
    Recomputes weekly totals and validates equipment usage.
    Overwrites the LLM's self-reported numbers in the plan dict in-place.

    Parameters
    ----------
    workout_plan    : the raw Gemini output dict
    equipment_input : the user's stated equipment string (e.g. "dumbbells")

    Returns
    -------
    dict with keys:
        total_sessions                : int
        total_estimated_calories_burned : int  (true sum)
        total_estimated_duration_minutes: int  (true sum)
        total_training_days           : int  (counted from schedule)
        equipment_violations          : list of exercise names that violate the equipment rule
    """
    schedule = workout_plan.get("weekly_schedule", [])

    training_sessions    = [s for s in schedule if s.get("session_type") == "Training"]
    total_training_days  = len(training_sessions)
    total_calories       = sum(s.get("estimated_calories_burned", 0) for s in training_sessions)
    total_duration       = sum(s.get("estimated_duration_minutes", 0) for s in training_sessions)

    
    if "weekly_targets" not in workout_plan:
        workout_plan["weekly_targets"] = {}

    workout_plan["weekly_targets"]["total_sessions"]                  = total_training_days
    workout_plan["weekly_targets"]["total_estimated_calories_burned"] = total_calories
    workout_plan["weekly_targets"]["total_estimated_duration_minutes"]= total_duration

    
    if "workout_summary" in workout_plan:
        workout_plan["workout_summary"]["total_training_days"] = total_training_days

    # ── Equipment check ───────────────────────────────────────────────────────
    allowed_keywords = [kw.strip().lower() for kw in equipment_input.replace(",", " ").split() if kw.strip()]
    violations: list[str] = []

    for session in schedule:
        for exercise in session.get("exercises", []):
            name = exercise.get("name", "")
            name_lower = name.lower()
           
            KNOWN_EQUIPMENT_KEYWORDS = [
                "barbell", "cable", "machine", "kettlebell", "resistance band",
                "pull-up bar", "pull up bar", "pullup bar", "smith machine",
                "trx", "bench", "rack", "plate", "rope"
            ]
            for kw in KNOWN_EQUIPMENT_KEYWORDS:
                if kw in name_lower:
                    if not any(allowed in kw or kw in allowed for allowed in allowed_keywords):
                        violations.append(f"{name} (requires: {kw})")
                        break

    return {
        "total_sessions": total_training_days,
        "total_estimated_calories_burned": total_calories,
        "total_estimated_duration_minutes": total_duration,
        "total_training_days": total_training_days,
        "equipment_violations": violations,
    }
