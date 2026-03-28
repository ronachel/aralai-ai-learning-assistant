import pandas as pd
import random
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(CURRENT_DIR, "sample_student_data.csv")

subjects = ["Math", "Science", "English"]
difficulty_levels = ["Easy", "Medium", "Hard"]

data = []

for student in range(1, 21):
    if student <= 5:
        base_score = 85
        base_time = 30
    elif student <= 10:
        base_score = 40
        base_time = 80
    else:
        base_score = 65
        base_time = 50

    for subject in subjects:
        score = min(100, max(0, base_score + random.randint(-10, 10)))
        time = max(10, base_time + random.randint(-10, 10))

        data.append({
            "student_id": student,
            "subject": subject,
            "score": score,
            "time_spent_minutes": time,
            "difficulty_level": random.choice(difficulty_levels),
            "date": f"2026-03-{random.randint(1, 28):02d}"
        })

df = pd.DataFrame(data)
df.to_csv(FILE_PATH, index=False)

print("✅ generated DISTINCT student data! Student 1 will now be very different from Student 6.")
