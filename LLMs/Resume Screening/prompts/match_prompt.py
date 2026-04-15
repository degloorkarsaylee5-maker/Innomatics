match_prompt = """
Compare candidate with job description.

Rules:
- Do NOT assume skills
- Only use extracted data

Return STRICT JSON:
{
  "matched_skills": [],
  "missing_skills": []
}

Candidate:
{candidate}

Job Description:
{jd}
"""