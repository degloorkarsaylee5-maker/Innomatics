score_prompt = """
Assign a score (0–100).

Rules:
- Strong: 80–100
- Average: 50–79
- Weak: <50
- Based ONLY on match data

Return STRICT JSON:
{
  "score": number
}

Match Data:
{match}
"""