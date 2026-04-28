
#Step 2:

import re


def validate_all(data: dict):
    errors = {}
    height = None
    weight = None 
    # -------------------
    # Step 1: Goal
    # -------------------
    goal = data.get("goal")

    if not goal or goal.strip() == "":
        errors["goal"] = "Please select one goal so I can plan your meals properly."
    else:
        g = goal.strip().lower()
        allowed = {
            "lose weight": "lose_weight",
            "gain muscle": "gain_muscle",
            "maintain": "maintain",
            "eat healthy": "eat_healthy"
        }

        if g not in allowed:
            errors["goal"] = "Please select one goal so I can plan your meals properly."
        else:
            goal = allowed[g]

    # -------------------
    # Step 2: Body Metrics
    # -------------------
    body_metrics = data.get("body_metrics")

    if not body_metrics or body_metrics.strip() == "":
        errors["body_metrics"] = "Please enter both height and weight (e.g., 170cm 70kg OR 5'9 65kg)."
    else:
        text = body_metrics.lower().strip()

        # ✅ Pattern 1: 170cm 70kg OR 170 cm 70 kg
        cm_pattern = r"^(\d{2,3})\s*cm\s+(\d{2,3})\s*kg$"

        # ✅ Pattern 2: 5'9 65kg OR 5' 9 65kg
        ft_pattern = r"^(\d)'\s*(\d{1,2})\s+(\d{2,3})\s*kg$"

        cm_match = re.match(cm_pattern, text)
        ft_match = re.match(ft_pattern, text)

        if cm_match:
            height = int(cm_match.group(1))
            weight = int(cm_match.group(2))

        elif ft_match:
            feet = int(ft_match.group(1))
            inches = int(ft_match.group(2))
            weight = int(ft_match.group(3))

            # convert to cm
            height = round((feet * 30.48) + (inches * 2.54))

        else:
            errors["body_metrics"] =  errors["body_metrics"] = "Please enter both height and weight (e.g., 170cm 70kg OR 5'9 65kg)."
    
    # -------------------
    # Step 3: Activity Level
    # -------------------
    activity = data.get("activity_level")

    if not activity or activity.strip() == "":
        errors["activity_level"] = "Please choose: Low, Moderate, or Active."
    else:
        a = activity.strip().lower()

        allowed_activity = {
            "low": "low",
            "moderate": "moderate",
            "active": "active"
        }

        if a not in allowed_activity:
            errors["activity_level"] = "Please choose: Low, Moderate, or Active."
        else:
            activity = allowed_activity[a]    

    # -------------------
    # Step 4: Diet Type
    # -------------------
    diet = data.get("diet_type")

    if not diet or diet.strip() == "":
        errors["diet_type"] = "Please select one diet type (or choose 'None')."
    else:
        d = diet.strip().lower()

        allowed_diet = {
            "none": "none",
            "halal": "halal",
            "vegetarian": "vegetarian",
            "vegan": "vegan",
            "keto": "keto"
        }

        if d not in allowed_diet:
            errors["diet_type"] = "Please select one diet type (or choose 'None')."
        else:
            diet = allowed_diet[d]



    # # -------------------
    # # Step 5: Allergies
    # # -------------------
    # allergies = data.get("allergies")
    # items = data.get("allergy_items")

    # if not allergies or allergies.strip() == "":
    #     errors["allergies"] = "Please answer Yes or No. If yes list the foods to avoid."
    # else:
    #     a = allergies.strip().lower()

    #     if a not in ["yes", "no"]:
    #         errors["allergies"] = "Please answer Yes or No. If yes list the foods to avoid."

    #     elif a == "yes":
    #         if not items or items.strip() == "":
    #             errors["allergy_items"] = "Please answer Yes or No. If yes list the foods to avoid."
    #         else:
    #             allergy_list = [i.strip() for i in items.split(",") if i.strip()]

    #             if not allergy_list:
    #                 errors["allergy_items"] = "Please answer Yes or No. If yes list the foods to avoid."
    #     else:
    #         allergy_list = []





    #improved
    # -------------------
    # Step 5: Allergies
    # -------------------
    allergies = data.get("allergies")
    items = data.get("allergy_items")

    allergy_list = []  # always define

    if not allergies or allergies.strip() == "":
        errors["allergies"] = "Please answer Yes or No. If yes list the foods to avoid."

    else:
        a = allergies.strip().lower()

        # ❌ Invalid input
        if a not in ["yes", "no"]:
            errors["allergies"] = "Please answer Yes or No. If yes list the foods to avoid."

        # ✅ YES case
        elif a == "yes":
            if not items or items.strip() == "":
                errors["allergy_items"] = "Please answer Yes or No. If yes list the foods to avoid."
            else:
                # Normalize + clean
                allergy_list = [
                    i.strip().lower()
                    for i in items.split(",")
                    if i.strip()
                ]

                # ❌ Empty after cleaning
                if not allergy_list:
                    errors["allergy_items"] = "Please answer Yes or No. If yes list the foods to avoid."

        # ✅ NO case
        else:
            allergy_list = []

    # 🔥 IMPORTANT: store clean result back
    data["allergy_items"] = allergy_list
    data["allergies"] = a if allergies else "no"




    # -------------------
    # Step 6: Meals per day
    # -------------------
    meals = data.get("meals_per_day")

    if meals is None:
        errors["meals_per_day"] = "Please enter a number (e.g., 1 or 3)."
    else:
        try:
            meals = int(meals)

            if meals < 1 or meals > 6:
                errors["meals_per_day"] = "Meals per day must be between 1 and 6."

        except:
            errors["meals_per_day"] = "Please enter a number (e.g., 1 or 3)."


    # -------------------
    # Step 7: Medical Conditions
    # -------------------
    medical = data.get("medical_conditions")

    if not medical or medical.strip() == "":
        errors["medical_conditions"] = "You can type 'none' if not applicable."
    else:
        text = medical.strip().lower()

        # normalize input
        text = text.replace(",", " ")
        text = " ".join(text.split())

        if text == "none":
            medical_list = []

        else:
            # split into words/conditions
            items = [i.strip() for i in text.split() if i.strip()]

            # ❌ reject garbage input
            if not items:
                errors["medical_conditions"] = "You can type 'none' if not applicable."
            else:
                medical_list = items


    # # -------------------
    # # Step 8: Age (Range)
    # # -------------------
    # age = data.get("age")

    # allowed_age = ["18-26", "27-38", "39-50", "50+"]

    # if not age or age.strip() == "":
    #     errors["age"] = "Please select your age range."
    # else:
    #     a = age.strip()

    #     if a not in allowed_age:
    #         errors["age"] = "Please select a valid age range."

     
  
    
    # Step 8: Age
    age = data.get("age")

    if age is None:
        errors["age"] = "Please enter your age."
    else:
        try:
            age = int(age)
            if age < 18 or age > 100:
                errors["age"] = "Please enter a valid age between 18 and 100."
        except:
            errors["age"] = "Please enter your age as a number (e.g. 25)."


    # -------------------
    # Step 9: Gender
    # -------------------
    gender = data.get("gender")

    allowed_gender = ["male", "female", "prefer not to say"]

    if not gender or gender.strip() == "":
        errors["gender"] = "Please select your gender."
    else:
        g = gender.strip().lower()

        if g not in allowed_gender:
            errors["gender"] = "Please select: Male, Female, or Prefer not to say."
        else:
            gender = g


    #You may delete this its optional Cusine , preferences , budget
    # -------------------
    # Step 10: Cuisine
    # -------------------
    # cuisine = data.get("cuisine")

    # allowed_cuisine = [
    #     "pakistani",
    #     "indian",
    #     "western",
    #     "middle eastern",
    #     "mixed"
    # ]

    # if not cuisine or cuisine.strip() == "":
    #     errors["cuisine"] = "Please select your preferred cuisine."
    # else:
    #     c = cuisine.strip().lower()

    #     if c not in allowed_cuisine:
    #         errors["cuisine"] = "Please select a valid cuisine."
    #     else:
    #         cuisine = c


    # -------------------
    # Step 11: Food Preference
    # -------------------
    # food_pref = data.get("food_preference")

    # allowed_food_pref = [
    #     "spicy",
    #     "mild",
    #     "sweet",
    #     "balanced",
    #     "high protein",
    #     "low carb"
    # ]

    # if not food_pref or food_pref.strip() == "":
    #     errors["food_preference"] = "Please select your food preference."
    # else:
    #     f = food_pref.strip().lower()

    #     if f not in allowed_food_pref:
    #         errors["food_preference"] = "Please select a valid food preference."
    #     else:
    #         food_pref = f



    # -------------------
    # Step 12: Budget
    # -------------------
    # budget = data.get("budget")

    # allowed_budget = ["low", "medium", "high"]

    # if not budget or budget.strip() == "":
    #     errors["budget"] = "Please select your budget."
    # else:
    #     b = budget.strip().lower()

    #     if b not in allowed_budget:
    #         errors["budget"] = "Please select: Low, Medium, or High."
    #     else:
    #         budget = b



    # -------------------
    # FINAL
    # -------------------
    if errors:
        return {"errors": errors}

    return {
        "goal": goal,
        "height_cm": height,
        "weight_kg": weight,
        "activity_level": activity,
        "diet_type": diet,
        "allergies": a,
        "allergy_items": allergy_list,
        "meals_per_day": meals,
        "medical_conditions": medical_list,
        "age": age,
        "gender": gender
        # "cuisine": cuisine,
        # "food_preference": food_pref,
        # "budget": budget
    } 