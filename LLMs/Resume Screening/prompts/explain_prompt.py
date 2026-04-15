explain_prompt = """
Explain why the score was given.

Include:
- Strengths
- Weaknesses
- Justification

Return STRICT JSON:
{
  "explanation": ""
}

Score:
{score}

Match Data:
{match}
"""