import os
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

def generate_recommendation(subject, score, student_data=None):
    api_key = get_key_from_env()

    if not api_key:
        return "⚠️ AI Error: GEMINI_API_KEY not found. Set it in environment or .env file in project root."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        profile_info = ""
        if student_data is not None:
            avg_score_all = student_data['score'].mean()
            total_time = student_data['time_spent_minutes'].sum()
            subjects_count = len(student_data['subject'].unique())

            subject_data = student_data[student_data['subject'] == subject]
            subject_avg_time = subject_data['time_spent_minutes'].mean() if not subject_data.empty else 0
            subject_difficulty = subject_data['difficulty_level'].mode().iloc[0] if not subject_data.empty else "Unknown"

            other_subjects = student_data[student_data['subject'] != subject]
            other_avg = other_subjects['score'].mean() if not other_subjects.empty else score

            profile_info = f"""
Student Performance Profile:
- Overall average score: {avg_score_all:.1f}/100 across {subjects_count} subjects
- Total study time: {total_time} minutes across all subjects
- {subject} specific: {score:.1f}/100 score, {subject_avg_time:.0f} min average study time, {subject_difficulty} difficulty
- Performance vs other subjects: {'above' if score > other_avg else 'below'} average ({other_avg:.1f})
"""

        prompt = f"""You are an expert educational psychologist and personalized learning specialist.

{profile_info}

The student needs improvement in {subject} where they scored {score:.1f}/100.

Provide a highly personalized, actionable study plan that includes:

1. **Specific Learning Strategy**: Based on their current performance level and difficulty perception
2. **Time Management**: Realistic daily/weekly schedule considering their current study habits
3. **Targeted Resources**: Specific tools/apps/books that match their learning style and current level
4. **Progress Tracking**: Concrete ways to measure improvement and stay motivated
5. **Common Pitfalls**: Address potential challenges based on their performance patterns

Make this recommendation feel personal, encouraging, and immediately actionable. Keep it to 3-4 sentences maximum.
"""

        response = model.generate_content(prompt)
        response_text = (response.text or "").strip()
        if not response_text:
            return "⚠️ AI Error: Empty response from Gemini model."

        return response_text

    except Exception as e:
        return f"⚠️ AI Connection Error: {str(e)}"
