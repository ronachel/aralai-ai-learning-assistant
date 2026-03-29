import streamlit as st
import pandas as pd
import numpy as np
import os
from analytics import analyze_performance, weakest_subject
from model import predict_risk, train_model, load_model, predict_score
from llm import generate_study_plan, generate_learning_path, tutor_chat, explain_student_performance
from tutor import explain

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_pdf(text, filename="study_plan.pdf"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.drawString(100, height - 100, "AI Learning Assistant - Study Plan")
    y = height - 150
    for line in text.split('\n'):
        if y < 100:
            c.showPage()
            y = height - 100
        c.drawString(100, y, line)
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

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

st.info("Designed to work in low-resource environments with minimal data and optional AI usage.")

tab1, tab2 = st.tabs(["👤 Student View", "🧑‍🏫 Teacher View"])

with tab1:
    student_ids = df["student_id"].unique()
    selected_student = st.selectbox("Select Student", student_ids)
    filtered_df = df[df["student_id"] == selected_student]

    low_bandwidth_mode = st.checkbox("🌏 Low Bandwidth Mode", value=False)

    col1, col2, col3 = st.columns(3)

    avg_score = round(filtered_df["score"].mean(), 2)
    total_time = int(filtered_df["time_spent_minutes"].sum())
    weak = weakest_subject(filtered_df)

    risk_level = predict_risk(filtered_df)

    col1.metric("📊 Avg Score", avg_score)
    col2.metric("⏱ Total Study Time", f"{total_time} mins")
    col3.metric("⚠️ Weakest Subject", weak)

    st.subheader("🚨 Student Risk Level")
    if risk_level == "High Risk":
        st.warning(f"⚠️ {risk_level} (avg score: {avg_score}%)")
    elif risk_level == "Moderate":
        st.warning(f"⚠️ {risk_level} (avg score: {avg_score}%)")
    else:
        st.success(f"✅ {risk_level} (avg score: {avg_score}%)")

    st.subheader("📊 Progress Over Time")
    if "date" in filtered_df.columns:
        progress_df = (
            filtered_df
            .assign(date=pd.to_datetime(filtered_df["date"]))
            .groupby("date")["score"]
            .mean()
            .sort_index()
        )
        st.line_chart(progress_df)
    else:
        st.info("No date field available for progress chart.")

    st.subheader(f"📊 Analysis for Student {selected_student}")

    chart_col, insights_col = st.columns([1.2, 1])  
    with chart_col:
        avg_scores = analyze_performance(filtered_df)
        st.bar_chart(avg_scores, height=700)

    with insights_col:
        weak = weakest_subject(filtered_df)
        st.metric("⚠️ Weakest Subject", weak)

        st.subheader("🧠 Why You’re Struggling")
        struggle_message = explain_student_performance(filtered_df)
        st.write(struggle_message)

        use_ai = st.checkbox("Use AI recommendation", value=not low_bandwidth_mode)

        st.subheader("🧠 Personalized Study Plan")
        study_plan = generate_study_plan(weak, risk_level, avg_score, student_df=filtered_df, low_resource=low_bandwidth_mode)
        if isinstance(study_plan, str) and study_plan.startswith("⚠️"):
            header, _, plan_text = study_plan.partition("\n\n")
            safe_notice = "⚠️ AI unavailable or quota exceeded, using fallback plan." if "AI Connection Error" in header or "AI unavailable" in header else header
            st.info(safe_notice)
            st.write(plan_text)
            if plan_text:
                pdf_buffer = generate_pdf(plan_text)
                st.download_button(
                    label="Download Study Plan as PDF",
                    data=pdf_buffer,
                    file_name="study_plan_fallback.pdf",
                    mime="application/pdf"
                )
        else:
            st.markdown("**🤖 AI Study Plan:**")
            st.write(study_plan)
            if not low_bandwidth_mode:
                pdf_buffer = generate_pdf(study_plan)
                st.download_button(
                    label="Download Study Plan as PDF",
                    data=pdf_buffer,
                    file_name="study_plan.pdf",
                    mime="application/pdf"
                )

        st.subheader("🎯 AI Learning Path")
        if low_bandwidth_mode:
            st.write("Low bandwidth mode: AI learning path is disabled. Use basic study recommendations.")
        else:
            learning_path = generate_learning_path(weak, risk_level)
            if isinstance(learning_path, str) and learning_path.startswith("⚠️"):
                st.warning(learning_path)
            else:
                st.write(learning_path)

        st.subheader("🤖 Chat Tutor")
        if low_bandwidth_mode:
            st.info("Low bandwidth mode: chat tutor is disabled.")
        else:
            user_question = st.text_input("Ask your tutor a question:", key="tutor_question")
            if st.button("Ask Tutor", key="tutor_button"):
                tutor_response = tutor_chat(user_question)
                st.write(tutor_response)

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

        st.subheader("📊 Prediction Insight")
        if "time_spent_minutes" in filtered_df.columns and "score" in filtered_df.columns:
            corr = filtered_df["time_spent_minutes"].corr(filtered_df["score"])
            mean_time = filtered_df["time_spent_minutes"].mean()
            if corr > 0.2:
                st.write(f"According to historical data, increasing study time is positively correlated with score (corr={corr:.2f}).")
            elif corr < -0.1:
                st.write(f"Study time is inversely correlated with score (corr={corr:.2f}), suggesting method quality may need improvement.")
            else:
                st.write(f"Study time has weak correlation with score (corr={corr:.2f}), focusing on learning techniques may help.")
            st.write(f"Average study time for this student is {mean_time:.1f} minutes.")
        else:
            st.write("Insufficient data for prediction insight.")
    else:
        st.write("Not enough data for prediction.")

with tab2:
    st.subheader("🧑‍🏫 Teacher Insights")
    
    st.subheader("👥 Student Overview")
    student_avg_scores = df.groupby("student_id")["score"].mean()
    st.bar_chart(student_avg_scores)
    
    student_total_time = df.groupby("student_id")["time_spent_minutes"].sum()
    st.write("Total Study Time per Student:")
    st.bar_chart(student_total_time)
    
    overall_weakest = weakest_subject(df)
    st.metric("Overall Weakest Subject", overall_weakest)
    
    at_risk_students = df.groupby("student_id")["score"].mean()
    at_risk_list = at_risk_students[at_risk_students < 70].index.tolist()
    st.write("At-Risk Students (avg score < 70):")
    if at_risk_list:
        st.write(", ".join(str(x) for x in at_risk_list))
    else:
        st.write("None")
    
    class_avg = round(df["score"].mean(), 2)
    st.metric("Average Class Performance", f"{class_avg}%")

    st.subheader("📉 Students Declining Over Time")
    declining_students = []
    for sid in df["student_id"].unique():
        sdf = df[df["student_id"] == sid].copy()
        if "date" in sdf.columns:
            sdf["date"] = pd.to_datetime(sdf["date"], errors="coerce")
            sdf = sdf.dropna(subset=["date", "score"])
            if len(sdf) >= 2:
                x = (sdf["date"] - sdf["date"].min()).dt.days.astype(float)
                y = sdf["score"].astype(float)
                slope = np.polyfit(x, y, 1)[0]
                if slope < -0.05:
                    declining_students.append(sid)
    if declining_students:
        st.write(", ".join(str(x) for x in declining_students))
    else:
        st.write("None")

    st.subheader("🚨 Top 3 At-Risk Students")
    bottom_students = df.groupby("student_id")["score"].mean().sort_values().head(3)
    st.table(bottom_students.reset_index().rename(columns={"score": "avg_score"}))

    st.subheader("📊 Subject Difficulty Impact")
    if "difficulty_level" in df.columns:
        diff_performance = df.groupby("difficulty_level")["score"].mean().sort_index()
        st.bar_chart(diff_performance)
    else:
        st.write("No difficulty_level data available.")

with st.expander("ℹ️ About This Project"):
    st.write("""
    **AI Learning Assistant** provides:
    • Gemini-powered AI recommendations
    • ML-based score predictions
    • Interactive performance dashboard

    Built with: Python, Streamlit, Scikit-learn, Google Gemini
    """)