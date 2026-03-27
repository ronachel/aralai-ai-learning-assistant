import pandas as pd
import random

subjects = ["Math", "Science", "English"]

data = []

for student in range(1, 21):
    for subject in subjects:
        data.append({
            "student_id": student,
            "subject": subject,
            "score": random.randint(50, 100),
            "time_spent_minutes": random.randint(30, 90),
        })

df = pd.DataFrame(data)
df.to_csv("data/sample_student_data.csv", index=False)

print("✅ Dataset generated!")