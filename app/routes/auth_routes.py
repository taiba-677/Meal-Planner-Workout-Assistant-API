from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User
from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    UpdatePasswordRequest,
    TokenResponse,
    RegisterResponse,
    LoginResponse,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password and create user
    hashed_pwd = hash_password(data.password)
    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hashed_pwd,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(new_user.user_id)})
    return RegisterResponse(
        status="success",
        message="User registered successfully",
        user_id=new_user.user_id,
        access_token=access_token,
        token_type="bearer",
    )


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # Find user by email
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # Specific 401 message for email vs password
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Also block deactivated users from logging in
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account has been deactivated. Please contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.user_id)})
    return LoginResponse(
        status="success",
        message="Logged in successfully",
        user_id=user.user_id,
        access_token=access_token,
        token_type="bearer",
    )



@router.patch("/update-password")
async def update_password(
    data: UpdatePasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update the user's password using their email.
    No old_password required — email acts as identity verification.
    """
    # Find user by email
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated",
        )

    # Hash and update password
    user.password_hash = hash_password(data.new_password)
    db.add(user)
    await db.commit()

    return {"status": "success", "message": "Password updated successfully"}


@router.delete("/delete-account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete — sets is_active=False.
    The user's data remains in the database but they cannot log in.
    """
    # Re-fetch user in this session to avoid detached instance issues
    stmt = select(User).where(User.user_id == current_user.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.add(user)
    await db.commit()

    return {"status": "success", "message": "Account deactivated successfully"}


@router.post("/signout")
async def signout():
    # Stateless logout. Client is expected to discard the token.
    return {
        "status": "success",
        "message": "Signed out. Please discard your token client-side.",
    }
