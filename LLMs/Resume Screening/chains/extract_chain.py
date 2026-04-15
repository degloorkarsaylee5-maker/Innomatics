from langchain_core.runnables import RunnableLambda
import json

def extract(inputs):
    resume = inputs["resume"]

    lines = resume.split("\n")

    # 🟢 Extract name (first non-empty line)
    name = "Unknown"
    for line in lines:
        if line.strip():
            name = line.strip()
            break

    resume_lower = resume.lower()

    skills = []

    keywords = {
        "Python": ["python"],
        "Java": ["java"],
        "AI": ["ai", "artificial intelligence"],
        "Machine Learning": ["machine learning"],
        "SQL": ["sql"],
        "Deep Learning": ["deep learning"]
    }

    for skill, words in keywords.items():
        for word in words:
            if word in resume_lower:
                skills.append(skill)
                break

    return type("Obj", (), {
        "content": json.dumps({
            "name": name,
            "skills": skills
        })
    })()

extract_chain = RunnableLambda(extract)