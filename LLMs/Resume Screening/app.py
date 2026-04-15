from flask import Flask, render_template, request, send_file
from main import run_pipeline
import PyPDF2
import json

app = Flask(__name__)

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        jd = request.form.get("jd")

        file = request.files.get("resume_file")

        if file:
            resume_text = extract_text_from_pdf(file)
        else:
            resume_text = request.form.get("resume")

        result = run_pipeline(resume_text, jd)

    return render_template("index.html", result=result)


@app.route("/download", methods=["POST"])
def download():
    data = request.form.get("data")
    with open("result.json", "w") as f:
        f.write(data)
    return send_file("result.json", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)