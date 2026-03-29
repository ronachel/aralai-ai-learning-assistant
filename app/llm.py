import os
import numpy as np
import pandas as pd
import google.generativeai as genai

def get_key_from_env():
    """Try system env var first, then .env file relative to app folder."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key.strip():
        return api_key.strip()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    for _ in range(3):
        potential_path = os.path.join(current_dir, ".env")
        if os.path.exists(potential_path):
            with open(potential_path, "r", encoding="utf-8") as f:
                for line in f:
                    clean_line = line.strip().lstrip("\ufeff")
                    if clean_line.startswith("GEMINI_API_KEY"):
                        return clean_line.split("=", 1)[1].strip().replace('"', '').replace("'", "")
        current_dir = os.path.dirname(current_dir)

    return None

def _compute_score_trend(df):
    if "date" not in df.columns or "score" not in df.columns or df.empty:
        return "stable"
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "score"])
    if len(df) < 2:
        return "stable"
    x = (df["date"] - df["date"].min()).dt.days.astype(float)
    y = df["score"].astype(float)
    if len(x) < 2:
        return "stable"
    slope = np.polyfit(x, y, 1)[0]
    return "improving" if slope > 0.05 else "declining" if slope < -0.05 else "stable"


def generate_study_plan(subject, risk_level, avg_score, student_df=None, low_resource=False):
    score_trend = _compute_score_trend(student_df) if student_df is not None else "stable"
    time_score_corr = None
    if student_df is not None and "time_spent_minutes" in student_df.columns and "score" in student_df.columns:
        time_score_corr = student_df["time_spent_minutes"].corr(student_df["score"])

    weakest_explanation = f"Weakest subject is {subject}, with consistent lower scores versus other fields." if subject else "Weakest subject data is limited."

    def _basic_plan():
        insight = (
            f"Score trend: {score_trend}. {weakest_explanation} "
            f"Current average score is {avg_score:.1f}. "
            f"Study time correlation with score is {'positive' if time_score_corr is None or time_score_corr >= 0 else 'negative'}."
        )
        steps = [
            "1. Focus on your weakest subject with targeted practice and review.",
            "2. Keep daily study sessions short with active recall and spaced repetition.",
            "3. Granularly track progress and adjust topics every week.",
            "4. Pair content practice with timed quizzes to build confidence.",
            "5. Reflect on errors and prioritize concepts with low accuracy.",
        ]
        return f"{insight}\n\n" + "\n".join(steps[:5])

    if low_resource or not get_key_from_env():
        return "⚠️ AI unavailable (low-resource or no key). Using basic fallback plan." + "\n\n" + _basic_plan()

    api_key = get_key_from_env()
    if not api_key:
        return "⚠️ AI Error: GEMINI_API_KEY not found. Set it in environment or .env file in project root."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        corr_text = f"{time_score_corr:.2f}" if time_score_corr is not None else "unknown"
        prompt = f"""You are an expert educational psychologist and personalized learning specialist.

Student data:
- Subject: {subject}
- Risk level: {risk_level}
- Average score: {avg_score:.1f}
- Trend: {score_trend}
- Weakest subject: {weakest_explanation}
- Time-vs-score correlation: {corr_text}

Please provide:
1) short paragraph insight
2) 3-5 bullet-point actionable steps tied to this student's data
"""

        response = model.generate_content(prompt)
        response_text = (response.text or "").strip()
        if not response_text:
            return "⚠️ AI Error: Empty response from Gemini model. Using fallback plan.\n\n" + _basic_plan()

        return response_text

    except Exception as e:
        return f"⚠️ AI Connection Error: {str(e)}. Using fallback plan.\n\n" + _basic_plan()


def explain_student_performance(student_df):
    if student_df is None or student_df.empty:
        return "Not enough data to explain student performance."

    trend = _compute_score_trend(student_df)
    difficulty_score = None
    if "difficulty_level" in student_df.columns and "score" in student_df.columns:
        difficulty_score = student_df.groupby("difficulty_level")["score"].mean().to_dict()

    time_corr = None
    if "time_spent_minutes" in student_df.columns and "score" in student_df.columns:
        time_corr = student_df["time_spent_minutes"].corr(student_df["score"])

    explanation = [f"The student's score trend is {trend}."]

    if time_corr is not None:
        if time_corr > 0.2:
            explanation.append("Study time has positive correlation with score, indicating effort helps.")
        elif time_corr < -0.1:
            explanation.append("Study time is negatively correlated with score, which may indicate inefficient study habits.")
        else:
            explanation.append("Study time has weak correlation with score, suggesting method quality matters more.")

    if difficulty_score:
        sorted_diff = sorted(difficulty_score.items(), key=lambda item: item[1])
        formatted_diff = ", ".join([f"{level}: {score:.1f}" for level, score in sorted_diff])
        explanation.append(f"Average score by difficulty – {formatted_diff}.")

    if trend == "declining":
        explanation.append("Despite effort, performance is declining; focus on fundamentals and active practice.")

    if trend == "improving":
        explanation.append("Performance is improving, keep the current approach with incremental adjustments.")

    return " ".join(explanation)


def generate_learning_path(subject, risk_level):
    api_key = get_key_from_env()

    if not api_key:
        return "⚠️ AI Error: GEMINI_API_KEY not found. Set it in environment or .env file in project root."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""You are an expert learning experience designer.

The student needs a learning path for {subject} with risk level {risk_level}.

Provide a 3-week structured plan with actionable steps:
- Week 1
- Week 2
- Week 3

Keep it concise and practical.
"""

        response = model.generate_content(prompt)
        response_text = (response.text or "").strip()
        if not response_text:
            return "⚠️ AI Error: Empty response from Gemini model."

        return response_text

    except Exception as e:
        return f"⚠️ AI Connection Error: {str(e)}"


def tutor_chat(user_question):
    api_key = get_key_from_env()

    if not api_key:
        return "⚠️ AI Error: GEMINI_API_KEY not found. Set it in environment or .env file in project root."

    if not user_question or not user_question.strip():
        return "Please enter a question for the tutor."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""You are a knowledgeable study coach.

User question: {user_question}

Provide a clear, friendly explanation with practical steps.
"""

        response = model.generate_content(prompt)
        response_text = (response.text or "").strip()
        if not response_text:
            return "⚠️ AI Error: Empty response from Gemini model."

        return response_text

    except Exception as e:
        return f"⚠️ AI Connection Error: {str(e)}"
