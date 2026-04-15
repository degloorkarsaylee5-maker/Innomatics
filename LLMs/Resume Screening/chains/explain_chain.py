from langchain_core.runnables import RunnableLambda
import json

def explain(inputs):
    score = json.loads(inputs["score"])["final_score"]

    if score >= 75:
        msg = "Strong candidate"
    elif score >= 40:
        msg = "Average candidate"
    else:
        msg = "Weak candidate"

    return type("Obj", (), {
        "content": json.dumps({
            "explanation": msg
        })
    })()

explain_chain = RunnableLambda(explain)