
#Step 2:

import re


def validate_all(data: dict):
    errors = {}

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



    # -------------------
    # Step 5: Allergies
    # -------------------
    allergies = data.get("allergies")
    items = data.get("allergy_items")

    if not allergies or allergies.strip() == "":
        errors["allergies"] = "Please answer Yes or No. If yes list the foods to avoid."
    else:
        a = allergies.strip().lower()

        if a not in ["yes", "no"]:
            errors["allergies"] = "Please answer Yes or No. If yes list the foods to avoid."

        elif a == "yes":
            if not items or items.strip() == "":
                errors["allergy_items"] = "Please answer Yes or No. If yes list the foods to avoid."
            else:
                allergy_list = [i.strip() for i in items.split(",") if i.strip()]

                if not allergy_list:
                    errors["allergy_items"] = "Please answer Yes or No. If yes list the foods to avoid."
        else:
            allergy_list = []


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
        "allergy_items": allergy_list
    } 