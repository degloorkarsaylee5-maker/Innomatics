from langchain_core.runnables import RunnableLambda
import json

def score(inputs):
    match = json.loads(inputs["match"])
    final_score = match["match_score"]

    return type("Obj", (), {
        "content": json.dumps({
            "final_score": final_score
        })
    })()

score_chain = RunnableLambda(score)