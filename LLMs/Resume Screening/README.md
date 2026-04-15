# AI Resume Screening System

## Overview
An AI-powered system that evaluates resumes against job descriptions using NLP and LangChain.

## Features
- Extract skills from resumes
- Match candidate skills with job description
- Calculate performance score
- Explain candidate suitability
- Flask-based web interface
- PDF upload support

## Tech Stack
- Python
- LangChain
- Flask
- PyPDF2
- HTML, CSS

## Project Structure
```
chains/        # Chain logic
prompts/       # LLM prompts
utils/         # Helper functions
templates/    # HTML templates
app.py         # Flask application
main.py        # Main entry point
```


## How to Run

### 1. Clone Repository
```bash
git clone <your-repo-link>
cd project-folder
```

### 2. Setup Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run Application
```bash
python app.py
```


## Output
- Candidate name
- Extracted skills
- Matching skills
- Match score with progress bar
- Suitability explanation

## Future Improvements
- Enhanced scoring algorithm
- Improved UI/UX
- Cloud deployment integration

