# Meal Planner & Workout Assistant API

**Meal Planner & Workout Assistant API** is an AI-powered backend that generates personalised meal plans and weekly workout schedules based on a user's body metrics, goals, diet type, and fitness level. Nutrition targets are computed server-side (Mifflin-St Jeor BMR + TDEE) and the AI output is always validated and overwritten — never trusted blindly.

---

## 🏗️ How It Works (Simple Flow)

```mermaid
flowchart TD
    A[User Registers / Logs In] -->|JWT Token| B(Authenticated Request)
    B --> C[POST /generate-meal-plan]
    C -->|Body metrics, goal, diet| D{Validate & Compute Nutrition Targets}
    D -->|BMR + TDEE| E(Build Gemini Prompt)
    E -->|Gemini AI| F[Generated Meal Plan JSON]
    F -->|Server-side math overwrite| G[(PostgreSQL - meal_plans)]
    G --> H[meal_plan_id returned]
    H --> I[POST /generate-workout-plan]
    I -->|Fitness level, equipment, style| J(Build Workout Prompt)
    J -->|Gemini AI| K[Generated Workout Plan JSON]
    K -->|Structural validation| L[(PostgreSQL - workout_plans)]
    L --> M[Final Response to User]
```

1. **Register / Login** — User gets a JWT Bearer token.
2. **Validate** — Inputs (goal, body metrics, diet type, age, gender) are validated via Pydantic v2 + custom business rules.
3. **Compute Targets** — Server computes calorie, protein, carb and fat targets using BMR/TDEE formulas.
4. **Meal Generation** — A structured prompt is sent to Gemini AI; response is parsed and math is overwritten server-side.
5. **Save** — Meal plan is persisted to PostgreSQL and a history log entry is created.
6. **Workout Generation** — Using the saved meal plan's summary, a linked workout schedule is generated and validated.
7. **History** — All generated plans are retrievable per user via history endpoints.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Backend Framework** | FastAPI (async, Python 3.11+) |
| **Database** | PostgreSQL (async via `asyncpg`) |
| **ORM** | SQLAlchemy 2.0 (async) |
| **AI Model** | Google Gemini (`google-genai`) |
| **Auth** | JWT Bearer Token (HS256, `python-jose`) |
| **Password Hashing** | bcrypt via `passlib` |
| **Schema Validation** | Pydantic v2 |
| **Server** | Uvicorn (ASGI) |

---

## 📂 Project Folder Structure

```
meal_planner_api/
├── app/
│   ├── main.py                  ← FastAPI app, routers, CORS, error handlers
│   ├── .env                     ← Environment variables (not committed)
│   ├── core/
│   │   ├── config.py            ← Loads .env, Settings object
│   │   └── security.py          ← JWT create/decode, bcrypt, get_current_user
│   ├── db/
│   │   ├── database.py          ← Async engine + session factory
│   │   ├── init_db.py           ← Creates tables on startup
│   │   └── models.py            ← User, MealPlan, WorkoutPlan, HistoryLog
│   ├── routes/
│   │   ├── auth_routes.py       ← Register, Login, Update Password, Delete, Signout
│   │   ├── meal_routes.py       ← Validate inputs, Generate & save meal plan
│   │   ├── workout_routes.py    ← Generate & save workout plan
│   │   └── history_routes.py   ← Retrieve past plans + activity log
│   ├── schemas/
│   │   ├── auth_schema.py       ← Register / Login / UpdatePassword Pydantic models
│   │   ├── meal_schema.py       ← MealRequest Pydantic model
│   │   └── workout_schema.py    ← WorkoutRequest Pydantic model
│   ├── services/
│   │   ├── gemini_service.py         ← Gemini API client wrapper
│   │   ├── prompt_service.py         ← Builds meal plan prompt for Gemini
│   │   ├── validation_service.py     ← Business-rule validation for meal inputs
│   │   ├── nutrition_calc_service.py ← BMR + TDEE macro calculation
│   │   ├── plan_math_service.py      ← Server-side macro overwrite (meal + workout)
│   │   ├── workout_prompt_service.py ← Builds workout prompt for Gemini
│   │   └── workout_validation_service.py ← Workout input validation
│   └── utils/
│       └── json_parser.py       ← Safe JSON parser for Gemini output
├── test_api.py                  ← Integration test (5 scenarios)
├── requirements.txt
└── README.md
```

---

## 🗄️ Database Tables

1. **`users`** — Stores registered accounts: name, email, bcrypt password hash, `is_active` (soft delete).
2. **`meal_plans`** — Stores user inputs snapshot, computed nutrition targets (calories, protein, carbs, fat) and the full AI-generated meal plan JSON.
3. **`workout_plans`** — Stores fitness inputs, linked `meal_plan_id`, and the full AI-generated weekly workout schedule JSON.
4. **`history_logs`** — Chronological log of every `MEAL_PLAN_GENERATED` or `WORKOUT_PLAN_GENERATED` action per user.

---

## 🚀 How to Run the Project

### Prerequisites
- Python 3.11+
- PostgreSQL running locally
- Google Gemini API Key → [Get one here](https://aistudio.google.com/app/apikey)

### Step 1: Setup Environment Variables
Create `app/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/meal_planner_api
JWT_SECRET_KEY=your_random_secret_key_here
```

### Step 2: Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Step 3: Create the Database
```sql
CREATE DATABASE meal_planner_api;
```

### Step 4: Run the Server
```bash
uvicorn app.main:app --reload --port 8000
```

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 📡 API Endpoints

### 🔑 Auth — `/api/auth`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register` | ❌ | Register new user, returns JWT |
| POST | `/login` | ❌ | Login, returns JWT |
| PATCH | `/update-password` | ❌ | Update password by email |
| DELETE | `/delete-account` | ✅ | Soft-delete account |
| POST | `/signout` | ❌ | Stateless logout |

### 🥗 Meal Plans — `/api`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/step-2-body` | ❌ | Validate meal inputs only |
| POST | `/generate-meal-plan` | ✅ | Generate + save AI meal plan |

### 🏋️ Workout Plans — `/api`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/generate-workout-plan` | ✅ | Generate + save AI workout plan (needs `meal_plan_id`) |

### 📜 History — `/api`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/meal-plans/{id}` | ✅ | Get a saved meal plan |
| GET | `/workout-plans/{id}` | ✅ | Get a saved workout plan |
| GET | `/meal-plans/{id}/workouts` | ✅ | List all workouts for a meal plan |
| GET | `/users/{id}/activity-log` | ✅ | Full chronological activity history |

---

## 🧪 Testing on Postman

1. **Register** → `POST /api/auth/register` → copy `access_token`
2. In Postman: **Authorization tab → Bearer Token** → paste token
3. **Generate Meal Plan** → `POST /api/generate-meal-plan` → copy `meal_plan_id`
4. **Generate Workout** → `POST /api/generate-workout-plan` with `meal_plan_id`
5. **View History** → `GET /api/users/{user_id}/activity-log`

**Sample Meal Plan Request Body:**
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

**Sample Workout Request Body:**
```json
{
  "meal_plan_id": 1,
  "fitness_level": "Intermediate",
  "days_available": 4,
  "equipment": "Dumbbells",
  "training_style": "Mixed",
  "injuries_or_limitations": "none"
}
```

---

## 🧑‍💻 Integration Tests

```bash
python test_api.py
```

Runs 5 automated scenarios (muscle gain, weight loss, keto, athlete, vegan) and checks calorie/protein deviation tolerances.
