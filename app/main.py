import os
from analytics import load_data, analyze_performance, weakest_subject
from tutor import explain
from llm import generate_recommendation

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_student_data.csv")

def run():
    df = load_data(DATA_PATH)

    print("Average Scores per Subject:")
    print(analyze_performance(df))

    weak = weakest_subject(df)
    print(f"\n⚠️ Weakest Subject: {weak}")

    print("\nAI Recommendation:")
    avg_score = df["score"].mean()
    ai_reco = generate_recommendation(weak, avg_score)
    if ai_reco.startswith("⚠️"):
        print(ai_reco)
        print("Fallback:", explain(weak))
    else:
        print(ai_reco)

if __name__ == "__main__":
    run()