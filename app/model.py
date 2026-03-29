import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "student_model.pkl")

_DIFFICULTY_MAP = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3,
}

def _encode_difficulty(df_or_series):
    if isinstance(df_or_series, pd.Series):
        return df_or_series.map(_DIFFICULTY_MAP).fillna(2).astype(int)
    df = df_or_series.copy()
    if "difficulty_level" not in df.columns:
        raise ValueError("difficulty_level column is required")
    df = df.copy()
    df["difficulty_level"] = df["difficulty_level"].map(_DIFFICULTY_MAP).fillna(2).astype(int)
    return df


def train_model(df):
    """Trains a RandomForest model with feature engineering and evaluation."""
    if "difficulty_level" not in df.columns or "time_spent_minutes" not in df.columns:
        raise ValueError("Input DataFrame must include time_spent_minutes and difficulty_level")

    df_encoded = _encode_difficulty(df)

    X = df_encoded[["time_spent_minutes", "difficulty_level"]]
    y = df_encoded["score"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    return {
        "model": model,
        "mae": mae,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred,
    }


def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None


def predict_score(model, time_spent_minutes, difficulty_level):
    difficulty_encoded = _DIFFICULTY_MAP.get(difficulty_level, 2)
    X_input = pd.DataFrame(
        [[time_spent_minutes, difficulty_encoded]],
        columns=["time_spent_minutes", "difficulty_level"],
    )
    pred = model.predict(X_input)
    return float(np.clip(pred[0], 0, 100))


def predict_risk(df):
    """Predict student overall risk based on average score rules."""
    if "score" not in df.columns:
        raise ValueError("DataFrame must contain 'score' column")

    avg_score = df["score"].mean()
    if avg_score < 70:
        return "High Risk"
    if avg_score <= 85:
        return "Moderate"
    return "Low Risk"

