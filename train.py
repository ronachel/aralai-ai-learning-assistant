import pandas as pd
import os
from app.model import train_model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_student_data.csv")

if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
    train_model(df)
    print("✅ Model trained successfully!")
else:
    print("❌ Error: data/sample_student_data.csv not found. Run data/generate_data.py first.")
