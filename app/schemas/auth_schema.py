from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, example="John Doe")
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., min_length=8, example="StrongPass123@")

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., example="StrongPass123@")

class UpdatePasswordRequest(BaseModel):
    email: EmailStr = Field(..., example="john.doe@example.com")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        example="NewStrongPass123@"
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must include at least 1 uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must include at least 1 lowercase letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must include at least 1 number.")
        if not re.search(r"[^\w\s]", v):
            raise ValueError("Password must include at least 1 special character (e.g. @, #, !).")
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RegisterResponse(BaseModel):
    status: str = "success"
    message: str = "User registered successfully"
    user_id: int
    access_token: str
    token_type: str = "bearer"

class LoginResponse(BaseModel):
    status: str = "success"
    message: str = "Logged in successfully"
    user_id: int
    access_token: str
    token_type: str = "bearer"
