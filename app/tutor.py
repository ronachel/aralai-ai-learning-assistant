def explain(subject, student_data=None):
    base_recommendations = {
        "Math": {
            "basic": "Dedicate 45 minutes daily to targeted practice using Khan Academy's personalized exercises. Focus on your weak areas like algebra or geometry by working through 10-15 problems daily, then review mistakes immediately. Track progress weekly by timing yourself on similar problem sets to measure improvement.",
            "personalized": "Based on your current performance, focus on building foundational skills first. Use spaced repetition for key concepts and practice with increasingly complex problems. Consider working with a study partner for difficult topics."
        },
        "Science": {
            "basic": "Spend 30-45 minutes daily reading science articles from reliable sources like National Geographic or BBC Science. Create concept maps connecting different scientific principles and practice explaining them aloud. Use online simulations and virtual labs to reinforce understanding through hands-on learning.",
            "personalized": "Given your science background, emphasize connecting theoretical concepts to real-world applications. Focus on visual learning through diagrams and experiments. Regular review of core principles will help solidify your understanding."
        },
        "English": {
            "basic": "Read for 30 minutes daily from diverse sources including novels, news articles, and academic texts. Practice writing by keeping a daily journal or responding to writing prompts. Focus on vocabulary building through apps like Duolingo and grammar exercises. Record yourself reading aloud to improve pronunciation and fluency.",
            "personalized": "Work on both receptive and productive skills. Balance reading comprehension with writing practice. Focus on context clues for vocabulary and practice different writing styles. Regular conversation practice will improve fluency."
        }
    }

    subject_data = base_recommendations.get(subject, {
        "basic": "Create a daily study schedule of 45 minutes focused on your weak areas. Use active recall techniques, practice regularly, and track your progress to build confidence and improve steadily.",
        "personalized": "Focus on systematic review and practice. Break down complex topics into smaller, manageable parts. Regular self-assessment will help identify areas needing more attention."
    })

    if student_data is not None and len(student_data) > 1:
        return subject_data["personalized"]
    else:
        return subject_data["basic"]