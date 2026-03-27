import os
from analytics import load_data, analyze_performance, weakest_subject
from tutor import explain

# Get absolute path to dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_student_data.csv")

def run():
    df = load_data(DATA_PATH)

    print("Average Scores per Subject:")
    print(analyze_performance(df))

    weak = weakest_subject(df)
    print(f"\n⚠️ Weakest Subject: {weak}")

    print("\n AI Recommendation:")
    print(explain(weak))

if __name__ == "__main__":
    run()