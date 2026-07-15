from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSON
import json
import enum
from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

class FormattedJSON(TypeDecorator):
    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, indent=4)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ── User ─────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    meal_plans: Mapped[list["MealPlan"]] = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")


# ── MealPlan ─────────────────────────────────────────────────────────────────
class MealPlan(Base):
    __tablename__ = "meal_plans"
    __table_args__ = (
        Index("idx_meal_plans_user", "user_id"),
    )

    meal_plan_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # ── User inputs (snapshot) ───────────────────────────────────────────────
    goal: Mapped[str] = mapped_column(String(100))
    diet_type: Mapped[str] = mapped_column(String(100))
    activity_level: Mapped[str] = mapped_column(String(50))
    gender: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)
    body_metrics: Mapped[str] = mapped_column(String(100))
    meals_per_day: Mapped[int] = mapped_column(Integer)
    medical_conditions: Mapped[str] = mapped_column(Text, default="none")
    allergies: Mapped[str] = mapped_column(String(10), default="no")
    allergy_items: Mapped[str] = mapped_column(Text, default="")

    # ── Computed nutritional targets ─────────────────────────────────────────
    target_calories: Mapped[int] = mapped_column(Integer)
    target_protein_g: Mapped[int] = mapped_column(Integer)
    target_carbs_g: Mapped[int] = mapped_column(Integer)
    target_fat_g: Mapped[int] = mapped_column(Integer)

    # ── Generated output ─────────────────────────────────────────────────────
    # FormattedJSON ensures it physically saves with indentation, bypassing asyncpg compression
    full_meal_plan: Mapped[dict] = mapped_column(FormattedJSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationship ─────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="meal_plans")
    workout_plans: Mapped[list["WorkoutPlan"]] = relationship(
        "WorkoutPlan", back_populates="meal_plan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MealPlan meal_plan_id={self.meal_plan_id} goal={self.goal!r} cal={self.target_calories}>"


# ── WorkoutPlan ───────────────────────────────────────────────────────────────
class WorkoutPlan(Base):
    __tablename__ = "workout_plans"
    __table_args__ = (
        Index("idx_workout_plans_user",      "user_id"),
        Index("idx_workout_plans_meal_plan",  "meal_plan_id"),
    )

    workout_plan_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── FK to owning user (always required, cascades on user delete) ─────────
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )

    # ── FK to MealPlan (optional context — SET NULL when meal plan deleted) ──
    meal_plan_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("meal_plans.meal_plan_id", ondelete="SET NULL"), nullable=True
    )

    # ── User workout inputs (snapshot) ───────────────────────────────────────
    fitness_level: Mapped[str] = mapped_column(String(50))
    days_available: Mapped[int] = mapped_column(Integer)
    equipment: Mapped[str] = mapped_column(String(100))
    training_style: Mapped[str] = mapped_column(String(50))
    injuries_or_limitations: Mapped[str] = mapped_column(Text, default="none")

    # ── Generated output ─────────────────────────────────────────────────────
    full_workout_plan: Mapped[dict] = mapped_column(FormattedJSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User")
    meal_plan: Mapped["MealPlan | None"] = relationship("MealPlan", back_populates="workout_plans")

    def __repr__(self) -> str:
        return f"<WorkoutPlan workout_plan_id={self.workout_plan_id} user_id={self.user_id} meal_plan_id={self.meal_plan_id} level={self.fitness_level!r}>"


# ── ActionType Enum ──────────────────────────────────────────────────────────
class ActionType(enum.Enum):
    MEAL_PLAN_GENERATED = "MEAL_PLAN_GENERATED"
    WORKOUT_PLAN_GENERATED = "WORKOUT_PLAN_GENERATED"


# ── HistoryLog ───────────────────────────────────────────────────────────────
class HistoryLog(Base):
    __tablename__ = "history_logs"
    __table_args__ = (
        Index("idx_history_logs_user_created", "user_id", "created_at"),
    )

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    
    action_type: Mapped[ActionType] = mapped_column(SQLEnum(ActionType), nullable=False)
    
    meal_plan_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("meal_plans.meal_plan_id", ondelete="SET NULL"), nullable=True
    )
    
    workout_plan_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("workout_plans.workout_plan_id", ondelete="SET NULL"), nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    meal_plan: Mapped["MealPlan | None"] = relationship(
        "MealPlan",
        foreign_keys=[meal_plan_id],
        lazy="select"
    )
    workout_plan: Mapped["WorkoutPlan | None"] = relationship(
        "WorkoutPlan",
        foreign_keys=[workout_plan_id],
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<HistoryLog log_id={self.log_id} user_id={self.user_id} action={self.action_type.name}>"
