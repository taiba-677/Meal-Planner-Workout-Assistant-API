import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

scenarios = [
    {
        "name": "Scenario 1: Muscle Gain (Male, 80kg, Active)",
        "payload": {
            "goal": "gain muscle",
            "body_metrics": "180cm 80kg",
            "activity_level": "active",
            "diet_type": "none",
            "allergies": "no",
            "allergy_items": "",
            "meals_per_day": 4,
            "medical_conditions": "none",
            "age": 25,
            "gender": "male"
        }
    },
    {
        "name": "Scenario 2: Weight Loss (Female, 80kg, Low Activity)",
        "payload": {
            "goal": "lose weight",
            "body_metrics": "170cm 80kg",
            "activity_level": "low",
            "diet_type": "vegetarian",
            "allergies": "yes",
            "allergy_items": "peanuts",
            "meals_per_day": 3,
            "medical_conditions": "none",
            "age": 30,
            "gender": "female"
        }
    },
    {
        "name": "Scenario 3: Keto & Dairy-Free (Male, 95kg, Moderate Activity)",
        "payload": {
            "goal": "lose weight",
            "body_metrics": "185cm 95kg",
            "activity_level": "moderate",
            "diet_type": "keto",
            "allergies": "yes",
            "allergy_items": "dairy",
            "meals_per_day": 3,
            "medical_conditions": "none",
            "age": 45,
            "gender": "male"
        }
    }
]

def run_test():
    for scenario in scenarios:
        print(f"\n--- Running {scenario['name']} ---")
        try:
            response = requests.post(f"{BASE_URL}/generate-meal-plan", json=scenario['payload'])
            if response.status_code == 200:
                result = response.json()
                print("SUCCESS")
                print(f"Target Calories: {result['meal_plan']['summary']['target_calories']}")
                print(f"Target Protein: {result['meal_plan']['summary']['target_protein_g']}g")
                
                actual_cal = result['meal_plan']['nutrition_breakdown']['total_calories']
                actual_protein = result['meal_plan']['nutrition_breakdown']['total_protein_g']
                
                print(f"Actual Calories: {actual_cal}")
                print(f"Actual Protein: {actual_protein}g")
                
                diff_cal = abs(actual_cal - result['meal_plan']['summary']['target_calories'])
                diff_prot = abs(actual_protein - result['meal_plan']['summary']['target_protein_g'])
                
                print(f"Calorie Difference: {diff_cal}")
                print(f"Protein Difference: {diff_prot}")
                
                if diff_cal <= 50 and diff_prot <= 10:
                    print("PASS: Within tolerances")
                else:
                    print("FAIL: Outside tolerances")
                    
                print("\nSample Meal:")
                print(json.dumps(result['meal_plan']['meals'][0], indent=2))
            else:
                print(f"FAILED: Status {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    run_test()
