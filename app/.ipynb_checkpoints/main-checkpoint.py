from analytics import load_data, analyze_performance, weakest_subject
from tutor import explain

df = load_data("../data/sample_student_data.csv")

print("📊 Average Scores:")
print(analyze_performance(df))

weak = weakest_subject(df)
print(f"\n⚠️ Weakest Subject: {weak}")

print("\n🤖 AI Explanation:")
print(explain(weak))