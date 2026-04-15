extract_prompt = """
You are an AI that extracts structured information from resumes.

Example:

Resume:
"Data Scientist with Python and Machine Learning experience"

Output:
{
  "skills": ["Python", "Machine Learning"],
  "experience": "Data Scientist",
  "tools": []
}

---

Now extract from this resume:

Rules:
- Do NOT assume anything
- Only extract explicitly mentioned data

Return STRICT JSON:
{
  "skills": [],
  "experience": "",
  "tools": []
}

Resume:
{resume}
"""