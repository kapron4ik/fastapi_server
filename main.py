
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class InputData(BaseModel):
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: str
    goal: str
    intensity: str = "moderate"

def calculate_nutrition_profile(age, gender, height_cm, weight_kg, activity_level, goal, intensity="moderate"):
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    activity_multipliers = {
        "low": 1.2,
        "moderate": 1.375,
        "active": 1.55,
        "very_active": 1.725
    }
    activity_multiplier = activity_multipliers.get(activity_level, 1.2)
    tdee = bmr * activity_multiplier

    intensity_map = {
        "mild": 0.10,
        "moderate": 0.15,
        "aggressive": 0.20
    }
    percent = intensity_map.get(intensity, 0.15)

    if goal == "lose":
        target_calories = round(tdee * (1 - percent))
    elif goal == "gain":
        target_calories = round(tdee * (1 + percent))
    else:
        target_calories = round(tdee)

    protein_kcal = target_calories * 0.30
    fat_kcal = target_calories * 0.30
    carb_kcal = target_calories * 0.40

    protein_grams = round(protein_kcal / 4)
    fat_grams = round(fat_kcal / 9)
    carb_grams = round(carb_kcal / 4)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_calories": target_calories,
        "macros": {
            "protein_g": protein_grams,
            "fat_g": fat_grams,
            "carbs_g": carb_grams
        }
    }

@app.post("/calculate")
def calculate(data: InputData):
    return calculate_nutrition_profile(
        age=data.age,
        gender=data.gender,
        height_cm=data.height_cm,
        weight_kg=data.weight_kg,
        activity_level=data.activity_level,
        goal=data.goal,
        intensity=data.intensity
    )

@app.get("/")
def root():
    return {"status": "ok"}
