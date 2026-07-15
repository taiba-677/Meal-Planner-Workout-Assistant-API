"""
history_routes.py
─────────────────
Read-only endpoints to retrieve saved meal plans and workout plans by ID.
These are useful for the frontend to re-display previously generated data.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import MealPlan, WorkoutPlan, User, HistoryLog
from app.core.security import get_current_user

router = APIRouter(tags=["History"])



# ── GET Meal Plan ─────────────────────────────────────────────────────────────
@router.get("/meal-plans/{meal_plan_id}")
async def get_meal_plan(
    meal_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a previously generated meal plan by its ID, scoped to the current user."""
    stmt = select(MealPlan).where(
        MealPlan.meal_plan_id == meal_plan_id,
        MealPlan.user_id == current_user.user_id
    )
    result = await db.execute(stmt)
    record: MealPlan | None = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Meal plan with id={meal_plan_id} not found.",
        )

    return {
        "status": "success",
        "meal_plan_id": record.meal_plan_id,
        "created_at": record.created_at,
        "inputs": {
            "goal": record.goal,
            "diet_type": record.diet_type,
            "activity_level": record.activity_level,
            "gender": record.gender,
            "age": record.age,
            "body_metrics": record.body_metrics,
            "meals_per_day": record.meals_per_day,
            "medical_conditions": record.medical_conditions,
            "allergies": record.allergies,
            "allergy_items": record.allergy_items,
        },
        "targets": {
            "target_calories": record.target_calories,
            "target_protein_g": record.target_protein_g,
            "target_carbs_g": record.target_carbs_g,
            "target_fat_g": record.target_fat_g,
        },
        "meal_plan": record.full_meal_plan,
    }


# ── GET Workout Plan ──────────────────────────────────────────────────────────
@router.get("/workout-plans/{workout_plan_id}")
async def get_workout_plan(
    workout_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a previously generated workout plan by its ID, verifying user ownership via user_id."""
    stmt = (
        select(WorkoutPlan)
        .where(
            WorkoutPlan.workout_plan_id == workout_plan_id,
            WorkoutPlan.user_id == current_user.user_id,
        )
    )
    result = await db.execute(stmt)
    record: WorkoutPlan | None = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Workout plan with id={workout_plan_id} not found.",
        )

    return {
        "status": "success",
        "workout_plan_id": record.workout_plan_id,
        "meal_plan_id": record.meal_plan_id,
        "created_at": record.created_at,
        "inputs": {
            "fitness_level": record.fitness_level,
            "days_available": record.days_available,
            "equipment": record.equipment,
            "training_style": record.training_style,
            "injuries_or_limitations": record.injuries_or_limitations,
        },
        "workout_plan": record.full_workout_plan,
    }


# ── GET All Workout Plans for a Meal Plan ─────────────────────────────────────
@router.get("/meal-plans/{meal_plan_id}/workouts")
async def get_workouts_for_meal_plan(
    meal_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all workout plans generated for a specific meal plan, verifying owner first."""
    
    meal_stmt = select(MealPlan).where(
        MealPlan.meal_plan_id == meal_plan_id,
        MealPlan.user_id == current_user.user_id
    )
    meal_result = await db.execute(meal_stmt)
    if meal_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=404,
            detail=f"Meal plan with id={meal_plan_id} not found.",
        )

    stmt = (
        select(WorkoutPlan)
        .where(
            WorkoutPlan.meal_plan_id == meal_plan_id,
            WorkoutPlan.user_id == current_user.user_id,
        )
        .order_by(WorkoutPlan.created_at.desc())
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    return {
        "status": "success",
        "meal_plan_id": meal_plan_id,
        "total": len(records),
        "workout_plans": [
            {
                "workout_plan_id": r.workout_plan_id,
                "fitness_level": r.fitness_level,
                "training_style": r.training_style,
                "days_available": r.days_available,
                "created_at": r.created_at,
            }
            for r in records
        ],
    }



# ── GET /users/{user_id}/activity-log ─────────────────────────────────────────
@router.get("/users/{user_id}/activity-log")
async def get_activity_log(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch chronological history log of all plan generations for a given user,
    including summarized details of each generated plan."""
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorised to access another user's activity log.",
        )

    stmt = (
        select(HistoryLog)
        .where(HistoryLog.user_id == current_user.user_id)
        .options(
            selectinload(HistoryLog.meal_plan),
            selectinload(HistoryLog.workout_plan),
        )
        .order_by(HistoryLog.created_at.desc())
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    activity_log = []
    for r in records:
        entry = {
            "log_id": r.log_id,
            "action_type": r.action_type.name,
            "created_at": r.created_at,
        }

        if r.action_type.name == "MEAL_PLAN_GENERATED" and r.meal_plan:
            mp = r.meal_plan
            entry["meal_plan"] = {
                "meal_plan_id": mp.meal_plan_id,
                "inputs": {
                    "goal": mp.goal,
                    "diet_type": mp.diet_type,
                    "activity_level": mp.activity_level,
                    "gender": mp.gender,
                    "age": mp.age,
                    "body_metrics": mp.body_metrics,
                    "meals_per_day": mp.meals_per_day,
                    "medical_conditions": mp.medical_conditions,
                    "allergies": mp.allergies,
                    "allergy_items": mp.allergy_items,
                },
                "targets": {
                    "target_calories": mp.target_calories,
                    "target_protein_g": mp.target_protein_g,
                    "target_carbs_g": mp.target_carbs_g,
                    "target_fat_g": mp.target_fat_g,
                },
                "summary": mp.full_meal_plan.get("summary", {}),
            }

        elif r.action_type.name == "WORKOUT_PLAN_GENERATED" and r.workout_plan:
            wp = r.workout_plan
            entry["workout_plan"] = {
                "workout_plan_id": wp.workout_plan_id,
                "inputs": {
                    "fitness_level": wp.fitness_level,
                    "days_available": wp.days_available,
                    "equipment": wp.equipment,
                    "training_style": wp.training_style,
                    "injuries_or_limitations": wp.injuries_or_limitations,
                },
                "workout_summary": wp.full_workout_plan.get("workout_summary", {}),
            }
            # Also include the linked meal plan summary
            if r.meal_plan:
                mp = r.meal_plan
                entry["linked_meal_plan"] = {
                    "meal_plan_id": mp.meal_plan_id,
                    "goal": mp.goal,
                    "diet_type": mp.diet_type,
                    "target_calories": mp.target_calories,
                }

        activity_log.append(entry)

    return {
        "status": "success",
        "user_id": user_id,
        "total": len(activity_log),
        "activity_log": activity_log,
    }
