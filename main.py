
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class InputData(BaseModel):
    weight: float
    height: float
    age: int
    sex: str
    activity_level: float

@app.post("/calculate")
def calculate(data: InputData):
    bmr = (10 * data.weight + 6.25 * data.height - 5 * data.age +
           (5 if data.sex == "male" else -161))
    calories = bmr * data.activity_level
    return {"calories": round(calories, 2)}

@app.get("/")
def root():
    return {"status": "ok"}
