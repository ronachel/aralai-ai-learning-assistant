import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "student_model.pkl")

def train_model(df):
    """Trains a general model based on all data."""
    X = df[["time_spent_minutes"]]
    y = df["score"]
    model = LinearRegression()
    model.fit(X, y)
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model

def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def predict_score(model, time_spent):
    X_input = pd.DataFrame([[time_spent]], columns=["time_spent_minutes"])
    return model.predict(X_input)[0]
