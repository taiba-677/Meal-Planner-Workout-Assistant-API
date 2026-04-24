# from fastapi import APIRouter
# from app.schemas.meal_schema import MealRequest
# from app.services.validation_service import validate_all
# from fastapi import APIRouter, HTTPException

# router = APIRouter()



# @router.post("/step-2-body")
# def step_2_body(data: MealRequest):
#     result = validate_all(data.dict())

#     if "errors" in result:
#         return {
#             "status": "error",
#             "errors": result["errors"]
#         }

#     return {
#         "status": "success",
#         "data": result
#     }



import json
from fastapi import APIRouter, HTTPException
from app.schemas.meal_schema import MealRequest
from app.services.validation_service import validate_all
from app.services.prompt_service import build_prompt
from app.services.gemini_service import generate_meal

router = APIRouter()


@router.post("/step-2-body")
def step_2_body(data: MealRequest):
    result = validate_all(data.dict())

    if "errors" in result:
        raise HTTPException(
            status_code=422,
            detail=result["errors"]
        )

    return {
        "status": "success",
        "data": result
    }



@router.post("/generate-meal-plan")
def generate_meal_plan(data: MealRequest):
    result = validate_all(data.dict())

    # ❌ validation error
    if "errors" in result:
        raise HTTPException(status_code=422, detail=result["errors"])

    # ✅ build prompt from CLEAN data
    prompt = build_prompt(result)

    # 🤖 generate from Gemini
    output = generate_meal(prompt)
    
    try:
        clean_output = output.strip()
        # Clean markdown
        if clean_output.startswith("```json"):
            clean_output = clean_output[7:]
        elif clean_output.startswith("```"):
            clean_output = clean_output[3:]
        if clean_output.endswith("```"):
            clean_output = clean_output[:-3]
            
        # Parse EXPECTED root-level JSON
        parsed_meals = json.loads(clean_output.strip())
        
        # Verify structure
        if not isinstance(parsed_meals, dict) or "meals" not in parsed_meals:
            raise ValueError("Invalid meal plan structure")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse meal plan: {str(e)}")
    
    return {
        "status": "success",
        "meal_plan": parsed_meals  # Now correctly structured
    }

