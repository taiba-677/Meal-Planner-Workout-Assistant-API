import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import MealPlan, User, HistoryLog, ActionType
from app.schemas.meal_schema import MealRequest
from app.services.gemini_service import generate_meal
from app.services.prompt_service import build_prompt
from app.services.validation_service import validate_all
from app.services.nutrition_calc_service import calculate_nutrition_targets
from app.services.plan_math_service import validate_meal_plan_math, overwrite_nutrition_breakdown
from app.core.security import get_current_user
from app.utils.json_parser import safe_parse_json

router = APIRouter(tags=["Meal Planner"])

# ── Validation Step ───────────────────────────────────────────────────────────
@router.post("/step-2-body")
async def step_2_body(data: MealRequest):
    result = validate_all(data.model_dump())
    if "errors" in result:
        raise HTTPException(status_code=422, detail=result["errors"])
    return {"status": "success", "data": result}


# ── Generate + Save Meal Plan ─────────────────────────────────────────────────
@router.post("/generate-meal-plan")
async def generate_meal_plan(
    data: MealRequest,
    current_user: User = Depends(get_current_user),  
    db: AsyncSession = Depends(get_db)
):
   
    result = validate_all(data.model_dump())
    if "errors" in result:
        raise HTTPException(status_code=422, detail=result["errors"])

   
    targets = calculate_nutrition_targets(result)

   
    prompt = build_prompt(result, targets)

    try:
        MAX_MEAL_ATTEMPTS = 3
        parsed_meals = None

        for attempt in range(MAX_MEAL_ATTEMPTS):
            output = generate_meal(prompt)
            clean_output = output.strip()

            if clean_output.startswith("```json"):
                clean_output = clean_output[7:]
            elif clean_output.startswith("```"):
                clean_output = clean_output[3:]
            if clean_output.endswith("```"):
                clean_output = clean_output[:-3]

            candidate = safe_parse_json(clean_output)

            if not isinstance(candidate, dict) or "meals" not in candidate:
                continue

            parsed_meals = candidate
            break  

        if parsed_meals is None:
            raise HTTPException(status_code=500, detail="Failed to generate a valid meal plan.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

    
    math_result = validate_meal_plan_math(parsed_meals, targets)
    parsed_meals = overwrite_nutrition_breakdown(parsed_meals, math_result)
    
   
    if "summary" in parsed_meals:
        summary_data = parsed_meals.pop("summary")
        parsed_meals["summary"] = summary_data

   
    meal_plan_record = MealPlan(
        user_id=current_user.user_id,
        goal=data.goal,
        diet_type=data.diet_type,
        activity_level=data.activity_level,
        gender=data.gender,
        age=data.age,
        body_metrics=data.body_metrics,
        meals_per_day=data.meals_per_day,
        medical_conditions=data.medical_conditions,
        allergies=data.allergies,
        allergy_items=data.allergy_items,
        target_calories=targets.get("target_calories", 0),
        target_protein_g=targets.get("target_protein_g", 0),
        target_carbs_g=targets.get("target_carbs_g", 0),
        target_fat_g=targets.get("target_fat_g", 0),
        full_meal_plan=parsed_meals,
    )
    db.add(meal_plan_record)
    await db.flush() 

   
    history_log = HistoryLog(
        user_id=current_user.user_id,
        action_type=ActionType.MEAL_PLAN_GENERATED,
        meal_plan_id=meal_plan_record.meal_plan_id,
    )
    db.add(history_log)
    await db.flush()

    return {
        "status": "success",
        "meal_plan_id": meal_plan_record.meal_plan_id,
        "meal_plan": parsed_meals,
    }