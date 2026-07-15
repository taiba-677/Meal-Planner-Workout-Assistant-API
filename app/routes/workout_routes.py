from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import MealPlan, WorkoutPlan, User, HistoryLog, ActionType
from app.schemas.workout_schema import WorkoutRequest
from app.services.gemini_service import generate_meal
from app.services.workout_prompt_service import build_workout_prompt
from app.services.workout_validation_service import validate_workout_input
from app.services.plan_math_service import validate_workout_plan_math
from app.core.security import get_current_user
from app.utils.json_parser import safe_parse_json

router = APIRouter(tags=["Workout Assistant"])


def _validate_workout_structure(parsed_workout: dict, days_available: int) -> tuple[bool, str]:
    """
    Returns (is_valid, reason). Validates structural integrity of the
    generated workout plan before accepting it.
    """
    schedule = parsed_workout.get("weekly_schedule", [])
    rest_days = parsed_workout.get("rest_days", [])

    if not isinstance(schedule, list) or len(schedule) != days_available:
        return False, f"Expected {days_available} training days, got {len(schedule)}"

    training_day_names = [d.get("day") for d in schedule if d.get("day")]
    rest_day_names = [d.get("day") for d in rest_days if d.get("day")]

    if len(set(rest_day_names)) != len(rest_day_names):
        return False, "Duplicate day names found in rest_days"

    if len(set(training_day_names)) != len(training_day_names):
        return False, "Duplicate day names found in weekly_schedule"

    overlap = set(training_day_names) & set(rest_day_names)
    if overlap:
        return False, f"Day(s) {overlap} appear in both training and rest schedules"

    if len(training_day_names) + len(rest_day_names) != 7:
        return False, "Training + rest days do not sum to 7"

    return True, "ok"


@router.post("/generate-workout-plan")
async def generate_workout_plan(
    data: WorkoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    User-triggered endpoint.
    Fetches the saved meal plan summary from DB by meal_plan_id,
    then generates and saves a personalised workout plan.
    """

   
    result = validate_workout_input(data.model_dump())
    if "errors" in result:
        raise HTTPException(status_code=422, detail=result["errors"])

    stmt = select(MealPlan).where(
        MealPlan.meal_plan_id == data.meal_plan_id,
        MealPlan.user_id == current_user.user_id
    )
    db_result = await db.execute(stmt)
    meal_plan_record: MealPlan | None = db_result.scalar_one_or_none()

    if meal_plan_record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Meal plan with id={data.meal_plan_id} not found. "
                   "Please generate a meal plan first.",
        )

    prompt = build_workout_prompt(
        summary=meal_plan_record.full_meal_plan.get("summary", {}),
        data=result,
    )

   
    try:
        MAX_WORKOUT_ATTEMPTS = 3
        parsed_workout = None
        last_failure_reason = None

        for attempt in range(MAX_WORKOUT_ATTEMPTS):
            output = generate_meal(prompt)   
            clean_output = output.strip()

            if clean_output.startswith("```json"):
                clean_output = clean_output[7:]
            elif clean_output.startswith("```"):
                clean_output = clean_output[3:]
            if clean_output.endswith("```"):
                clean_output = clean_output[:-3]

            candidate = safe_parse_json(clean_output)

            if not isinstance(candidate, dict) or "weekly_schedule" not in candidate:
                last_failure_reason = "Missing weekly_schedule key"
                continue

            is_valid, reason = _validate_workout_structure(candidate, result["days_available"])
            if is_valid:
                parsed_workout = candidate
                break
            last_failure_reason = reason

        if parsed_workout is None:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate a structurally valid workout plan after {MAX_WORKOUT_ATTEMPTS} attempts. Last issue: {last_failure_reason}",
            )
      
        desired_order = [
            "workout_summary",
            "weekly_schedule",
            "rest_days",
            "weekly_targets",
            "progression_plan",
            "nutrition_timing_tips",
            "safety_notes"
        ]
        
        ordered_workout = {}
        for key in desired_order:
            if key in parsed_workout:
                ordered_workout[key] = parsed_workout[key]
  
        for key in parsed_workout:
            if key not in ordered_workout:
                ordered_workout[key] = parsed_workout[key]
                
        parsed_workout = ordered_workout

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

   
    workout_math = validate_workout_plan_math(parsed_workout, result["equipment"])

    
    workout_record = WorkoutPlan(
        user_id=current_user.user_id,
        meal_plan_id=result["meal_plan_id"],
        fitness_level=result["fitness_level"],
        days_available=result["days_available"],
        equipment=result["equipment"],
        training_style=result["training_style"],
        injuries_or_limitations=result["injuries_or_limitations"],
        full_workout_plan=parsed_workout,
    )
    db.add(workout_record)
    await db.flush()   

  
    history_log = HistoryLog(
        user_id=current_user.user_id,
        action_type=ActionType.WORKOUT_PLAN_GENERATED,
        meal_plan_id=result["meal_plan_id"],
        workout_plan_id=workout_record.workout_plan_id,
    )
    db.add(history_log)
    await db.flush()

    return {
        "status": "success",
        "workout_plan_id": workout_record.workout_plan_id,
        "meal_plan_id": result["meal_plan_id"],
        "workout_plan": parsed_workout,
    }
