import streamlit as st
import pandas as pd
import os
from analytics import analyze_performance, weakest_subject
from tutor import explain

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_student_data.csv")

if not os.path.exists(DATA_PATH):
    st.error("Dataset not found. Please run data/generate_data.py first.")
    st.stop()

# load data
df = pd.read_csv(DATA_PATH)

# UI
st.title("AI Learning Assistant Dashboard")

st.markdown("Analyze student performance and get AI-powered recommendations.")

# show raw data (optional)
if st.checkbox("Show raw data"):
    st.write(df)

# testing new feature
student_ids = df["student_id"].unique()

selected_student = st.selectbox("Select Student", student_ids)

filtered_df = df[df["student_id"] == selected_student]

# performance chart
st.subheader("Average Scores per Subject")
avg_scores = analyze_performance(filtered_df)
st.bar_chart(avg_scores)

# time vs performance
st.subheader("⏱ Time Spent vs Score")

st.scatter_chart(
    data=filtered_df,
    x="time_spent_minutes",
    y="score"
)

# weakest subject
weak = weakest_subject(filtered_df)

st.subheader("⚠️ Weakest Subject")
st.write(f"**{weak}**")

# AI recommendation
st.subheader("AI Recommendation")
avg_score = filtered_df["score"].mean()

if avg_score < 70:
    level = "low performance"
elif avg_score < 85:
    level = "moderate performance"
else:
    level = "high performance"

st.success(
    f"{explain(weak)}\n\n"
    f"Based on your **{level}**, focus on improving **{weak}** to boost overall performance."
)

# performance by difficulty
st.subheader("📊 Performance by Difficulty")

difficulty_scores = filtered_df.groupby("difficulty_level")["score"].mean()

st.bar_chart(difficulty_scores)