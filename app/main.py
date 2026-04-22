from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from app.routes.meal_routes import router as meal_router

app = FastAPI()

# ✅ FIX CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc: RequestValidationError):
#     errors = {}

#     for err in exc.errors():
#         field = err["loc"][-1]

#         if field == "goal":
#             errors["goal"] = "Please select one goal so I can plan your meals properly."

#         elif field == "body_metrics":
#             errors["body_metrics"] = "Please enter both height and weight (e.g., 170cm 70kg OR 5'9 65kg)."
#         elif field == "diet_type":
#             errors["diet_type"] = "Please select one diet type (or choose 'None')."
#         else:
#             errors[field] = err["msg"]

#     return JSONResponse(
#         status_code=422,
#         content={
#             "status": "error",
#             "errors": errors
#         },
#     )



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = {}

    for err in exc.errors():
        field = err["loc"][-1]
        errors[field] = "Invalid or missing input."

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "errors": errors
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        },
    )
app.include_router(meal_router, prefix="/api")