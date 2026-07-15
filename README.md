# 🥗 Meal Planner & Workout Assistant API

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-asyncpg-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini_AI-Powered-4285F4?style=for-the-badge&logo=google&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT_Bearer-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

**A production-ready REST API that generates personalised meal plans and workout schedules powered by Google Gemini AI. Built with FastAPI, async PostgreSQL, and JWT authentication.**

</div>

---

## ✨ Features

- 🤖 **AI-Powered Generation** — Meal plans and workout schedules via Google Gemini
- 🔐 **JWT Authentication** — Secure register/login, token-based access
- 🧮 **Server-Side Nutrition Math** — Calories, protein, carbs & fat targets computed independently; AI output is *always* validated and overwritten
- 🏋️ **Workout Plans** — Linked to meal plans, validated weekly schedule structure
- 📜 **Activity History** — Full chronological log of all generated plans per user
- ⚡ **Async throughout** — FastAPI + SQLAlchemy async + asyncpg
- 🛡️ **Validation** — Pydantic v2 schema + custom business-rule validators

---

## 📋 Table of Contents

1. [Tech Stack](#-tech-stack)
2. [Architecture Diagram](#-architecture-diagram)
3. [Folder Structure](#-folder-structure)
4. [Database Schema](#-database-schema)
5. [Setup & Installation](#-setup--installation)
6. [Environment Variables](#-environment-variables)
7. [Running the Server](#-running-the-server)
8. [API Reference](#-api-reference)
9. [Testing with Postman](#-testing-with-postman)
10. [Error Responses](#-error-responses)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | FastAPI 0.136 (async) |
| **Language** | Python 3.11+ |
| **Database** | PostgreSQL (async via asyncpg) |
| **ORM** | SQLAlchemy 2.0 (async) |
| **AI Model** | Google Gemini (google-genai) |
| **Auth** | JWT (HS256) via python-jose |
| **Password Hashing** | bcrypt via passlib |
| **Schema Validation** | Pydantic v2 |
| **Server** | Uvicorn (ASGI) |

---

## 🏗️ Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                     CLIENT (Postman / Frontend)                       │
└──────────────────────────────────┬────────────────────────────────────┘
                                   │  HTTP Requests
                                   ▼
┌───────────────────────────────────────────────────────────────────────┐
│                     FastAPI Application (main.py)                     │
│                                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  ┌──────────┐  │
│  │ auth_routes │  │ meal_routes  │  │workout_routes │  │ history  │  │
│  │  /api/auth  │  │    /api/     │  │    /api/      │  │  routes  │  │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘  └────┬─────┘  │
│         └────────────────┴──────────────────┴───────────────┘         │
│                                   │                                   │
│                    ┌──────────────▼──────────────┐                    │
│                    │  core/security.py            │                    │
│                    │  JWT Auth + get_current_user │                    │
│                    └──────────────┬──────────────┘                    │
│         ┌─────────────────────────┼────────────────────┐              │
│         ▼                         ▼                    ▼              │
│  ┌─────────────┐        ┌──────────────────┐  ┌──────────────────┐   │
│  │  services/  │        │    db/models.py  │  │   schemas/       │   │
│  │             │        │  User            │  │  MealRequest     │   │
│  │ gemini_svc  │        │  MealPlan        │  │  WorkoutRequest  │   │
│  │ prompt_svc  │        │  WorkoutPlan     │  │  AuthSchemas     │   │
│  │ validation  │        │  HistoryLog      │  └──────────────────┘   │
│  │ plan_math   │        └────────┬─────────┘                         │
│  └──────┬──────┘                 │                                   │
│         │                        ▼                                   │
│         │              ┌──────────────────┐                          │
│         │              │  db/database.py  │                          │
│         │              │  AsyncSession    │                          │
│         │              └────────┬─────────┘                         │
└─────────┼───────────────────────┼──────────────────────────────────-┘
          │                       │
          ▼                       ▼
┌─────────────────┐    ┌──────────────────────┐
│  Google Gemini  │    │   PostgreSQL Database │
│  AI (gemini-2)  │    │                      │
│                 │    │  users               │
│  Generates:     │    │  meal_plans          │
│  - Meal Plans   │    │  workout_plans       │
│  - Workout Sched│    │  history_logs        │
└─────────────────┘    └──────────────────────┘
```

---

## 📁 Folder Structure

```
meal_planner_api/
├── app/
│   ├── .env                            # Environment variables (not committed)
│   ├── main.py                         # FastAPI app, routers, CORS, error handlers
│   │
│   ├── core/
│   │   ├── config.py                   # Loads .env, exposes Settings object
│   │   └── security.py                 # JWT creation/decoding, bcrypt, get_current_user
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py                 # Async SQLAlchemy engine + session factory
│   │   ├── init_db.py                  # Creates all tables on startup
│   │   └── models.py                   # ORM models: User, MealPlan, WorkoutPlan, HistoryLog
│   │
│   ├── routes/
│   │   ├── auth_routes.py              # POST /register, /login, /update-password, etc.
│   │   ├── meal_routes.py              # POST /step-2-body, /generate-meal-plan
│   │   ├── workout_routes.py           # POST /generate-workout-plan
│   │   └── history_routes.py           # GET meal plans, workout plans, activity log
│   │
│   ├── schemas/
│   │   ├── auth_schema.py              # Pydantic models for auth
│   │   ├── meal_schema.py              # Pydantic model for MealRequest
│   │   └── workout_schema.py           # Pydantic model for WorkoutRequest
│   │
│   ├── services/
│   │   ├── gemini_service.py           # Gemini API client wrapper
│   │   ├── prompt_service.py           # Builds AI prompt for meal generation
│   │   ├── validation_service.py       # Business-rule validation for meal inputs
│   │   ├── nutrition_calc_service.py   # Mifflin-St Jeor BMR + TDEE calculation
│   │   ├── plan_math_service.py        # Server-side macro math validation + overwrite
│   │   ├── workout_prompt_service.py   # Builds AI prompt for workout generation
│   │   └── workout_validation_service.py
│   │
│   └── utils/
│       └── json_parser.py              # Safe JSON parsing (handles malformed AI output)
│
├── test_api.py                         # Integration test runner (5 scenarios)
├── requirements.txt                    # All Python dependencies
└── README.md
```

---

## 🗄️ Database Schema

### Entity Relationship Overview

```
users (1) ─────────────────────────── (∞) meal_plans
  │                                              │
  │                                              │ (optional FK)
  └─────────────── (∞) workout_plans ────────────┘
  │
  └─────────────── (∞) history_logs ──── references meal_plans & workout_plans
```

---

### Table: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | INTEGER | PK, AUTO | Primary key |
| `name` | VARCHAR(255) | NOT NULL | Full name |
| `email` | VARCHAR(255) | UNIQUE, INDEX | Login email |
| `password_hash` | VARCHAR(255) | NOT NULL | bcrypt hash |
| `is_active` | BOOLEAN | NOT NULL, default=true | Soft-delete flag |
| `created_at` | TIMESTAMPTZ | server_default=now() | Account creation time |

---

### Table: `meal_plans`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `meal_plan_id` | INTEGER | PK, AUTO | Primary key |
| `user_id` | INTEGER | FK → users (CASCADE) | Owner |
| `goal` | VARCHAR(100) | | e.g. "lose weight" |
| `diet_type` | VARCHAR(100) | | e.g. "vegetarian" |
| `activity_level` | VARCHAR(50) | | low / moderate / active |
| `gender` | VARCHAR(50) | | male / female |
| `age` | INTEGER | | User age |
| `body_metrics` | VARCHAR(100) | | e.g. "170cm 70kg" |
| `meals_per_day` | INTEGER | | 1–6 |
| `medical_conditions` | TEXT | default="none" | Conditions string |
| `allergies` | VARCHAR(10) | default="no" | yes / no |
| `allergy_items` | TEXT | default="" | e.g. "peanuts, dairy" |
| `target_calories` | INTEGER | | Computed via BMR/TDEE |
| `target_protein_g` | INTEGER | | Computed target |
| `target_carbs_g` | INTEGER | | Computed target |
| `target_fat_g` | INTEGER | | Computed target |
| `full_meal_plan` | JSON (TEXT) | NOT NULL | Full AI-generated plan |
| `created_at` | TIMESTAMPTZ | server_default=now() | Generation time |

**Index:** `idx_meal_plans_user` on `(user_id)`

---

### Table: `workout_plans`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `workout_plan_id` | INTEGER | PK, AUTO | Primary key |
| `user_id` | INTEGER | FK → users (CASCADE) | Owner |
| `meal_plan_id` | INTEGER | FK → meal_plans (SET NULL), NULLABLE | Linked meal plan |
| `fitness_level` | VARCHAR(50) | | Beginner / Intermediate / Advanced |
| `days_available` | INTEGER | | 1–7 training days/week |
| `equipment` | VARCHAR(100) | | None / Dumbbells / Gym etc. |
| `training_style` | VARCHAR(50) | | Strength / Cardio / Mixed etc. |
| `injuries_or_limitations` | TEXT | default="none" | Known injuries |
| `full_workout_plan` | JSON (TEXT) | NOT NULL | Full AI-generated plan |
| `created_at` | TIMESTAMPTZ | server_default=now() | Generation time |

**Indexes:** `idx_workout_plans_user`, `idx_workout_plans_meal_plan`

---

### Table: `history_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `log_id` | INTEGER | PK, AUTO | Primary key |
| `user_id` | INTEGER | FK → users (CASCADE) | Owner |
| `action_type` | ENUM | NOT NULL | `MEAL_PLAN_GENERATED` or `WORKOUT_PLAN_GENERATED` |
| `meal_plan_id` | INTEGER | FK → meal_plans (SET NULL), NULLABLE | Referenced meal plan |
| `workout_plan_id` | INTEGER | FK → workout_plans (SET NULL), NULLABLE | Referenced workout plan |
| `created_at` | TIMESTAMPTZ | server_default=now() | Action time |

**Index:** `idx_history_logs_user_created` on `(user_id, created_at)`

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Google Gemini API Key → [Get one here](https://aistudio.google.com/app/apikey)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/meal_planner_api.git
cd meal_planner_api
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the PostgreSQL database

```sql
CREATE DATABASE meal_planner_api;
```

### 5. Configure environment variables

Create `app/.env` with the following:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/meal_planner_api
JWT_SECRET_KEY=your_very_long_random_secret_key_here
```

> **Generate a secure JWT secret:** `python -c "import secrets; print(secrets.token_hex(32))"`

---

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini AI API key |
| `DATABASE_URL` | ✅ Yes | Async PostgreSQL connection string |
| `JWT_SECRET_KEY` | ✅ Yes | Secret for signing JWT tokens (min 32 chars) |

---

## 🚀 Running the Server

```bash
# From inside the meal_planner_api/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will auto-create all database tables on first run.

| Resource | URL |
|----------|-----|
| **API Base URL** | `http://localhost:8000` |
| **Swagger UI (interactive docs)** | `http://localhost:8000/docs` |
| **ReDoc** | `http://localhost:8000/redoc` |

---

## 📚 API Reference

### Base URL
```
http://localhost:8000
```

### Authentication
Protected endpoints require a **Bearer Token** in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

> The JWT token is returned on successful **register** or **login**. It expires after **24 hours**.

---

## 🔑 Auth Endpoints

### `POST /api/auth/register`
Register a new user and receive a JWT token.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "StrongPass123@"
}
```

Password rules: min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special character.

**Success Response `201`:**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "user_id": 1,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### `POST /api/auth/login`
Login and receive a JWT token.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "StrongPass123@"
}
```

**Success Response `200`:**
```json
{
  "status": "success",
  "message": "Logged in successfully",
  "user_id": 1,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### `PATCH /api/auth/update-password`
Update password using email (no old password required).

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "new_password": "NewStrongPass123@"
}
```

**Success Response `200`:**
```json
{
  "status": "success",
  "message": "Password updated successfully"
}
```

---

### `DELETE /api/auth/delete-account`
🔐 Requires Bearer token.
Soft-delete the authenticated user account (`is_active = false`).

**Success Response `200`:**
```json
{
  "status": "success",
  "message": "Account deactivated successfully"
}
```

---

### `POST /api/auth/signout`
Stateless logout. Client must discard the JWT token.

**Success Response `200`:**
```json
{
  "status": "success",
  "message": "Signed out. Please discard your token client-side."
}
```

---

## 🥗 Meal Plan Endpoints

### `POST /api/step-2-body`
Validate meal plan inputs without generating a plan. Use as a pre-check step.

**Request Body:**
```json
{
  "goal": "lose weight",
  "body_metrics": "170cm 70kg",
  "activity_level": "moderate",
  "diet_type": "vegetarian",
  "allergies": "yes",
  "allergy_items": "peanuts, dairy",
  "meals_per_day": 3,
  "medical_conditions": "none",
  "age": 25,
  "gender": "female"
}
```

**Field Reference:**

| Field | Type | Accepted Values | Required |
|-------|------|-----------------|----------|
| `goal` | string | `lose weight` / `gain muscle` / `maintain` / `eat healthy` | ✅ |
| `body_metrics` | string | `"170cm 70kg"` or `"5'9 65kg"` | ✅ |
| `activity_level` | string | `low` / `moderate` / `active` | ✅ |
| `diet_type` | string | `none` / `halal` / `vegetarian` / `vegan` / `keto` | ✅ |
| `allergies` | string | `yes` / `no` | ✅ |
| `allergy_items` | string | Comma-separated e.g. `"peanuts, dairy"` | Only if allergies=yes |
| `meals_per_day` | integer | `1` to `6` | ✅ |
| `medical_conditions` | string | e.g. `"diabetes"` or `"none"` | ✅ |
| `age` | integer | `18` to `100` | ✅ |
| `gender` | string | `male` / `female` / `prefer not to say` | ✅ |

---

### `POST /api/generate-meal-plan`
🔐 Requires Bearer token.
Generate and save a personalised AI meal plan.

**Request Body:** Same fields as `/api/step-2-body` above.

**Success Response `200`:**
```json
{
  "status": "success",
  "meal_plan_id": 7,
  "meal_plan": {
    "meals": [
      {
        "meal_name": "Breakfast",
        "meal_totals": {
          "calories": 450,
          "protein_g": 35,
          "carbs_g": 50,
          "fat_g": 12
        },
        "items": [
          {
            "food": "Oats with berries",
            "portion": "1 cup",
            "calories": 300,
            "protein_g": 10,
            "carbs_g": 55,
            "fat_g": 5
          }
        ]
      }
    ],
    "nutrition_breakdown": {
      "total_calories": 1850,
      "total_protein_g": 95,
      "total_carbs_g": 210,
      "total_fat_g": 55
    },
    "summary": {
      "target_calories": 1800,
      "target_protein_g": 90,
      "target_carbs_g": 200,
      "target_fat_g": 50
    }
  }
}
```

> **Important:** Save the `meal_plan_id` — it is required to generate a workout plan.

---

## 🏋️ Workout Plan Endpoints

### `POST /api/generate-workout-plan`
🔐 Requires Bearer token.
Generate and save a personalised weekly workout schedule, linked to an existing meal plan.

**Request Body:**
```json
{
  "meal_plan_id": 7,
  "fitness_level": "Intermediate",
  "days_available": 4,
  "equipment": "Dumbbells",
  "training_style": "Mixed",
  "injuries_or_limitations": "none"
}
```

**Field Reference:**

| Field | Type | Accepted Values | Required |
|-------|------|-----------------|----------|
| `meal_plan_id` | integer | ID from `/generate-meal-plan` | ✅ |
| `fitness_level` | string | `Beginner` / `Intermediate` / `Advanced` | ✅ |
| `days_available` | integer | `1` to `7` | ✅ |
| `equipment` | string | `None` / `Dumbbells` / `Barbell` / `Resistance Bands` / `Gym` / `Bodyweight` | ✅ |
| `training_style` | string | `Strength` / `Cardio` / `Mixed` / `HIIT` / `Yoga` / `Calisthenics` | ✅ |
| `injuries_or_limitations` | string | e.g. `"bad knee"` or `"none"` | Optional |

**Success Response `200`:**
```json
{
  "status": "success",
  "workout_plan_id": 3,
  "meal_plan_id": 7,
  "workout_plan": {
    "workout_summary": {
      "fitness_level": "Intermediate",
      "training_days": 4,
      "training_style": "Mixed"
    },
    "weekly_schedule": [
      {
        "day": "Monday",
        "focus": "Upper Body Strength",
        "exercises": [
          {
            "name": "Dumbbell Press",
            "sets": 4,
            "reps": "8-10",
            "rest": "60s"
          }
        ]
      }
    ],
    "rest_days": [
      { "day": "Thursday", "activity": "Light stretching" }
    ],
    "weekly_targets": {},
    "progression_plan": {},
    "nutrition_timing_tips": {},
    "safety_notes": {}
  }
}
```

---

## 📜 History Endpoints

All history endpoints require: 🔐 `Authorization: Bearer <token>`

---

### `GET /api/meal-plans/{meal_plan_id}`
Retrieve a previously generated meal plan by ID (scoped to authenticated user).

**Example:** `GET /api/meal-plans/7`

**Success Response `200`:**
```json
{
  "status": "success",
  "meal_plan_id": 7,
  "created_at": "2026-07-15T09:00:00Z",
  "inputs": {
    "goal": "lose weight",
    "diet_type": "vegetarian",
    "activity_level": "moderate",
    "gender": "female",
    "age": 25,
    "body_metrics": "170cm 70kg",
    "meals_per_day": 3,
    "medical_conditions": "none",
    "allergies": "yes",
    "allergy_items": "peanuts, dairy"
  },
  "targets": {
    "target_calories": 1800,
    "target_protein_g": 90,
    "target_carbs_g": 200,
    "target_fat_g": 50
  },
  "meal_plan": { "meals": [...], "summary": {...} }
}
```

---

### `GET /api/workout-plans/{workout_plan_id}`
Retrieve a previously generated workout plan by ID.

**Example:** `GET /api/workout-plans/3`

---

### `GET /api/meal-plans/{meal_plan_id}/workouts`
List all workout plans generated for a specific meal plan.

**Example:** `GET /api/meal-plans/7/workouts`

**Success Response `200`:**
```json
{
  "status": "success",
  "meal_plan_id": 7,
  "total": 2,
  "workout_plans": [
    {
      "workout_plan_id": 3,
      "fitness_level": "Intermediate",
      "training_style": "Mixed",
      "days_available": 4,
      "created_at": "2026-07-15T10:00:00Z"
    }
  ]
}
```

---

### `GET /api/users/{user_id}/activity-log`
Get the full chronological activity history for the authenticated user.

**Example:** `GET /api/users/1/activity-log`

> Returns `403` if `user_id` does not match the authenticated user.

**Success Response `200`:**
```json
{
  "status": "success",
  "user_id": 1,
  "total": 5,
  "activity_log": [
    {
      "log_id": 5,
      "action_type": "WORKOUT_PLAN_GENERATED",
      "created_at": "2026-07-15T10:00:00Z",
      "workout_plan": {
        "workout_plan_id": 3,
        "inputs": { "fitness_level": "Intermediate", "days_available": 4 },
        "workout_summary": {}
      },
      "linked_meal_plan": {
        "meal_plan_id": 7,
        "goal": "lose weight",
        "diet_type": "vegetarian",
        "target_calories": 1800
      }
    }
  ]
}
```

---

## 🧪 Testing with Postman

### Step-by-Step Guide

#### Step 1 — Set Base URL Variable
In Postman create a variable:
- `base_url` = `http://localhost:8000`

---

#### Step 2 — Register a User

| | Value |
|-|-------|
| **Method** | `POST` |
| **URL** | `{{base_url}}/api/auth/register` |
| **Body type** | `raw → JSON` |

```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "MyPass123@"
}
```

✅ Copy the `access_token` from the response.

---

#### Step 3 — Set the Bearer Token

In Postman, on any protected request go to the **Authorization** tab:
- **Type:** `Bearer Token`
- **Token:** Paste your `access_token`

Or create a collection-level variable `{{token}}` and use `Bearer {{token}}`.

---

#### Step 4 — Generate a Meal Plan

| | Value |
|-|-------|
| **Method** | `POST` |
| **URL** | `{{base_url}}/api/generate-meal-plan` |
| **Auth** | Bearer `{{token}}` |
| **Body type** | `raw → JSON` |

```json
{
  "goal": "lose weight",
  "body_metrics": "170cm 70kg",
  "activity_level": "moderate",
  "diet_type": "vegetarian",
  "allergies": "yes",
  "allergy_items": "peanuts, dairy",
  "meals_per_day": 3,
  "medical_conditions": "none",
  "age": 25,
  "gender": "female"
}
```

✅ Save the `meal_plan_id` from the response (e.g., `7`).

---

#### Step 5 — Generate a Workout Plan

| | Value |
|-|-------|
| **Method** | `POST` |
| **URL** | `{{base_url}}/api/generate-workout-plan` |
| **Auth** | Bearer `{{token}}` |
| **Body type** | `raw → JSON` |

```json
{
  "meal_plan_id": 7,
  "fitness_level": "Intermediate",
  "days_available": 4,
  "equipment": "Dumbbells",
  "training_style": "Mixed",
  "injuries_or_limitations": "none"
}
```

---

#### Step 6 — View Your Activity Log

| | Value |
|-|-------|
| **Method** | `GET` |
| **URL** | `{{base_url}}/api/users/1/activity-log` |
| **Auth** | Bearer `{{token}}` |

> Replace `1` with your actual `user_id` from register/login response.

---

#### Suggested Postman Collection Layout

```
📁 Meal Planner API
 ├── 📁 Auth
 │   ├── POST Register
 │   ├── POST Login
 │   ├── PATCH Update Password
 │   ├── DELETE Delete Account
 │   └── POST Signout
 ├── 📁 Meal Plans
 │   ├── POST Validate Inputs (step-2-body)
 │   └── POST Generate Meal Plan
 ├── 📁 Workout Plans
 │   └── POST Generate Workout Plan
 └── 📁 History
     ├── GET Meal Plan by ID
     ├── GET Workout Plan by ID
     ├── GET Workouts for Meal Plan
     └── GET Activity Log
```

---

## ❌ Error Responses

All errors follow a consistent JSON structure:

### Validation Error `422`
```json
{
  "status": "error",
  "errors": {
    "email": "value is not a valid email address",
    "password": "String should have at least 8 characters"
  }
}
```

### Unauthorized `401`
```json
{
  "status": "error",
  "message": "Invalid email"
}
```

### Forbidden `403`
```json
{
  "status": "error",
  "message": "You are not authorised to access another user's activity log."
}
```

### Not Found `404`
```json
{
  "status": "error",
  "message": "Meal plan with id=99 not found."
}
```

### Server Error `500`
```json
{
  "status": "error",
  "message": "Something went wrong. Please try again."
}
```

---

## 🔁 Typical User Flow

```
1. POST /api/auth/register            →  Get JWT token + user_id
2. POST /api/generate-meal-plan       →  Get meal_plan_id
3. POST /api/generate-workout-plan    →  Get workout_plan_id (requires meal_plan_id)
4. GET  /api/users/{id}/activity-log  →  View full history
5. GET  /api/meal-plans/{id}          →  Re-fetch a past meal plan
6. GET  /api/workout-plans/{id}       →  Re-fetch a past workout plan
```

---

## 🧑‍💻 Running Integration Tests

```bash
# Make sure the server is running first, then:
python test_api.py
```

This runs 5 pre-built scenarios and checks:
- ✅ Calorie deviation (within ±100 kcal)
- ✅ Protein deviation (within ±15g)
- ⚠️ Diet compliance warnings (flags meat in vegetarian plans)

---

## 📄 License

This project is open-source. Feel free to fork and build upon it.

---

<div align="center">
Made with ❤️ using FastAPI + Google Gemini AI
</div>
