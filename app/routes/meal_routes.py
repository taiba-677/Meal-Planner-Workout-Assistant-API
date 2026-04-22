from fastapi import APIRouter
from app.schemas.meal_schema import MealRequest
from app.services.validation_service import validate_all
from fastapi import APIRouter, HTTPException

router = APIRouter()



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



from fastapi import APIRouter, HTTPException
from app.schemas.meal_schema import MealRequest
from app.services.validation_service import validate_all

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