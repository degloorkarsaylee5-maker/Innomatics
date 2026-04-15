import json
from dotenv import load_dotenv

from utils.loader import load_file

from chains.extract_chain import extract_chain
from chains.match_chain import match_chain
from chains.score_chain import score_chain
from chains.explain_chain import explain_chain

from langchain_core.runnables import RunnableConfig

load_dotenv()


def run_pipeline(resume, jd):

    extracted = extract_chain.invoke(
        {"resume": resume},
        config=RunnableConfig(tags=["extract"])
    )
    extracted_data = json.loads(extracted.content)

    matched = match_chain.invoke(
        {
            "candidate": extracted.content,
            "jd": jd
        },
        config=RunnableConfig(tags=["match"])
    )
    match_data = json.loads(matched.content)

    score = score_chain.invoke(
        {"match": matched.content},
        config=RunnableConfig(tags=["score"])
    )
    score_data = json.loads(score.content)

    explanation = explain_chain.invoke(
        {
            "score": score.content,
            "match": matched.content
        },
        config=RunnableConfig(tags=["explain"])
    )
    explanation_data = json.loads(explanation.content)

    return {
        **extracted_data,
        **match_data,
        **score_data,
        **explanation_data
    }


if __name__ == "__main__":
    jd = load_file("data/job_description.txt")

    resumes = [
        ("Strong Candidate", load_file("data/resume_strong.txt")),
        ("Average Candidate", load_file("data/resume_average.txt")),
        ("Weak Candidate", load_file("data/resume_weak.txt")),
        ("Debug Case", load_file("data/resume_debug.txt")),
    ]

    for name, resume in resumes:
        print(name)
        

        try:
            result = run_pipeline(resume, jd)
            print(json.dumps(result, indent=4))
        except Exception as e:
            print("Error:", e)