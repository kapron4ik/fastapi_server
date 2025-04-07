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
    desired_weight: float = None  # Добавлено поле для желаемого веса
    health_condition: str = None  # Добавлено поле для состояния здоровья

def calculate_nutrition_profile(age, gender, height_cm, weight_kg, activity_level, goal, intensity="moderate", desired_weight=None, health_condition=None):
    # Шаг 1: BMR (Basal Metabolic Rate)
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Шаг 2: Activity multiplier
    activity_multipliers = {
        "low": 1.2,
        "moderate": 1.375,
        "active": 1.55,
        "very_active": 1.725
    }
    activity_multiplier = activity_multipliers.get(activity_level, 1.2)
    tdee = bmr * activity_multiplier

    # Шаг 3: Целевые калории (по проценту)
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

    # Если цель - похудение, добавляем дефицит калорий
    if goal == "lose":
        target_calories = round(target_calories * 0.85)  # 15% дефицит калорий

    # Если задан желаемый вес, используем его для расчёта макроэлементов
    if desired_weight:
        # Проверяем состояние здоровья и корректируем норму белка
        if health_condition == "hypothyroidism":  # Гипотиреоз
            protein_g = round(desired_weight * 1.5)  # Увеличиваем норму белка
        elif health_condition == "kidney_problems":  # Проблемы с почками
            protein_g = round(desired_weight * 0.8)  # Уменьшаем норму белка
        else:
            protein_g = round(desired_weight * 1.2)  # Стандартное значение

        # Проверяем ИМТ для корректировки нормы жира
        bmi = weight_kg / (height_cm / 100) ** 2  # Расчет ИМТ
        if bmi < 25:
            fat_g = round(desired_weight * 1)  # Норма жиров 1 г на кг тела
        elif 25 <= bmi < 30:
            fat_g = round(desired_weight * 0.8)  # Уменьшаем норму жиров для избыточного веса
        else:
            fat_g = round(desired_weight * 0.6)  # Уменьшаем норму жиров для ожирения
    else:
        # Для фактического веса
        if health_condition == "hypothyroidism":  # Гипотиреоз
            protein_g = round(weight_kg * 1.5)
        elif health_condition == "kidney_problems":  # Проблемы с почками
            protein_g = round(weight_kg * 0.8)
        else:
            protein_g = round(weight_kg * 1.2)
        
        # Расчет ИМТ для корректировки жиров
        bmi = weight_kg / (height_cm / 100) ** 2
        if bmi < 25:
            fat_g = round(weight_kg * 1)  # Норма жиров 1 г на кг массы тела
        elif 25 <= bmi < 30:
            fat_g = round(weight_kg * 0.8)  # Для избыточного веса уменьшаем норму жиров
        else:
            fat_g = round(weight_kg * 0.6)  # Для ожирения уменьшаем норму жиров

    # Оставшиеся калории идут на углеводы
    protein_kcal = protein_g * 4
    fat_kcal = fat_g * 9
    carb_kcal = target_calories - (protein_kcal + fat_kcal)

    # Углеводы в граммах
    carb_g = round(carb_kcal / 4)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_calories": target_calories,
        "macros": {
            "protein_g": protein_g,
            "fat_g": fat_g,
            "carbs_g": carb_g
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
        intensity=data.intensity,
        desired_weight=data.desired_weight,  # Передаем желаемый вес
        health_condition=data.health_condition  # Передаем состояние здоровья
    )

@app.get("/")
def root():
    return {"status": "ok"}