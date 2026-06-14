import os
import io
import json
import requests
from flask import Flask, request, jsonify, render_template
from datetime import datetime
from pypdf import PdfReader

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def call_claude(prompt):
    if not ANTHROPIC_KEY:
        return "Set ANTHROPIC_API_KEY to enable AI features."
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}]
    }
    r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
    return r.json()["content"][0]["text"]

def extract_pdf_text(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/extract-pdf", methods=["POST"])
def extract_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400
    try:
        text = extract_pdf_text(file.read())
        if not text:
            return jsonify({"error": "Could not extract text from PDF"}), 400
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    resume = data.get("resume", "").strip()
    job_desc = data.get("job_description", "").strip()
    if not resume or not job_desc:
        return jsonify({"error": "Both resume and job description are required"}), 400

    prompt = f"""Analyze the match between this resume and job description.

RESUME:
{resume}

JOB DESCRIPTION:
{job_desc}

Return raw JSON only (no markdown, no backticks):
{{
  "match_score": <0-100>,
  "matched_keywords": [<keywords in both>],
  "missing_keywords": [<important missing keywords>],
  "strengths": [<2-3 specific strengths>],
  "gaps": [<2-3 specific gaps>],
  "verdict": "<one sentence summary>"
}}"""

    try:
        raw = call_claude(prompt).strip().replace("```json", "").replace("```", "").strip()
        return jsonify(json.loads(raw))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/cover-letter", methods=["POST"])
def cover_letter():
    data = request.get_json()
    resume = data.get("resume", "").strip()
    job_desc = data.get("job_description", "").strip()
    company = data.get("company", "the company").strip()
    role = data.get("role", "this role").strip()

    prompt = f"""Write a concise 3-paragraph cover letter for this candidate applying to {role} at {company}.
Sound human and direct. No cliche openers. Reference specifics from both the resume and job description.

RESUME:
{resume}

JOB DESCRIPTION:
{job_desc}"""

    try:
        return jsonify({"cover_letter": call_claude(prompt)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "ai_enabled": bool(ANTHROPIC_KEY), "timestamp": datetime.utcnow().isoformat()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
