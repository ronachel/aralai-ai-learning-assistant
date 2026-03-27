import streamlit as st
import pandas as pd
import os
from analytics import analyze_performance, weakest_subject
from tutor import explain

# Fix path (professional way)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_student_data.csv")

# Load data
df = pd.read_csv(DATA_PATH)

# UI
st.title("AI Learning Assistant Dashboard")

st.markdown("Analyze student performance and get AI-powered recommendations.")

# Show raw data (optional but nice)
if st.checkbox("Show raw data"):
    st.write(df)

# Performance chart
st.subheader("Average Scores per Subject")
avg_scores = analyze_performance(df)
st.bar_chart(avg_scores)

# Weakest subject
weak = weakest_subject(df)

st.subheader("⚠️ Weakest Subject")
st.write(f"**{weak}**")

# AI recommendation
st.subheader("AI Recommendation")
st.write(explain(weak))