import streamlit as st
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
from analytics import analyze_performance, weakest_subject
from model import train_model, load_model, predict_score
from llm import generate_recommendation
from tutor import explain

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_student_data.csv")

df = pd.read_csv(DATA_PATH)

st.title("AI Learning Assistant Dashboard")

st.set_page_config(
    page_title="AralAI Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        overflow: hidden;
    }
    h1, h2, h3 {
        color: white;
    }
    .stMetric {
        background-color: #1c1f26;
        padding: 10px;
        border-radius: 10px;
    }
    .stBarChart {
        max-height: 200px !important;
        overflow: hidden !important;
    }
    .element-container {
        overflow: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

student_ids = df["student_id"].unique()
selected_student = st.selectbox("Select Student", student_ids)
filtered_df = df[df["student_id"] == selected_student]

col1, col2, col3 = st.columns(3)

avg_score = round(filtered_df["score"].mean(), 2)
total_time = int(filtered_df["time_spent_minutes"].sum())
weak = weakest_subject(filtered_df)

col1.metric("📊 Avg Score", avg_score)
col2.metric("⏱ Total Study Time", f"{total_time} mins")
col3.metric("⚠️ Weakest Subject", weak)


st.subheader(f"📊 Analysis for Student {selected_student}")

chart_col, insights_col = st.columns([1.2, 1])  
with chart_col:
    avg_scores = analyze_performance(filtered_df)
    st.bar_chart(avg_scores, height=500)

with insights_col:
    weak = weakest_subject(filtered_df)
    st.metric("⚠️ Weakest Subject", weak)
    
    use_ai = st.checkbox("Use AI recommendation", value=True)
    
    if use_ai:
        recommendation = generate_recommendation(weak, avg_score, filtered_df)
        if recommendation.startswith("⚠️"):
            if "quota" in recommendation.lower() or "429" in recommendation:
                st.warning("🤖 AI quota exceeded - using smart fallback")
                st.info("💡 " + explain(weak, filtered_df))
            else:
                st.warning("AI unavailable - using basic recommendation")
                st.info(explain(weak, filtered_df))
        else:
            st.markdown("**🤖 AI Recommendation:**")
            st.write(recommendation)
    else:
        st.info("Using basic recommendation")
        st.write(explain(weak, filtered_df))

st.subheader("📈 Score Prediction")
time_input = st.slider("Study minutes", 10, 120, 60, key="study_time")

if len(filtered_df) > 1:
    avg_student_score = filtered_df["score"].mean()
    improvement_factor = 0.1
    base_prediction = avg_student_score + (time_input * improvement_factor)
    performance_bonus = (avg_student_score - 70) * 0.05
    predicted = max(0, min(100, base_prediction + performance_bonus))

    col_pred1, col_pred2 = st.columns(2)
    with col_pred1:
        st.metric("Predicted Score", f"{round(predicted, 1)}")
    with col_pred2:
        st.metric("Current Average", f"{round(avg_student_score, 1)}")

    st.caption(f"More study time generally leads to higher scores")
else:
    st.write("Not enough data for prediction.")

with st.expander("ℹ️ About This Project"):
    st.write("""
    **AI Learning Assistant** provides:
    • Gemini-powered AI recommendations
    • ML-based score predictions
    • Interactive performance dashboard

    Built with: Python, Streamlit, Scikit-learn, Google Gemini
    """)