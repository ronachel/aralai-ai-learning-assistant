from fastapi import FastAPI
import pandas as pd
from .model import load_model, predict_score

app = FastAPI()

model = load_model()

@app.get("/")
def home():
    return {"message": "AI Learning Assistant API running"}

@app.get("/predict")
def predict(time_spent: int):
    if model is None:
        return {"error": "Model not trained"}

    prediction = predict_score(model, time_spent)

    return {
        "predicted_score": round(prediction, 2)
    }