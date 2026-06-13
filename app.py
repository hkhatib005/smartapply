import os
import json
import requests
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY","")

def claude(prompt):
    if not ANTHROPIC_KEY: return "Set ANTHROPIC_API_KEY to enable AI."
    h = {"x-api-key":ANTHROPIC_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"}
    b = {"model":"claude-sonnet-4-6","max_tokens":1024,"messages":[{"role":"user","content":prompt}]}
    r = requests.post("https://api.anthropic.com/v1/messages",headers=h,json=b)
    return r.json()["content"][0]["text"]

@app.route("/")
def index(): return render_template("index.html")

@app.route("/api/analyze",methods=["POST"])
def analyze():
    d = request.get_json()
    resume = d.get("resume","").strip()
    job = d.get("job_description","").strip()
    if not resume or not job: return jsonify({"error":"Both fields required"}),400
    prompt = f"""Analyze the match between this resume and job description.\n\nRESUME:\n{resume}\n\nJOB DESCRIPTION:\n{job}\n\nReturn raw JSON only (no markdown, no backticks):\n{{\n  \"match_score\": <0-100>,\n  \"matched_keywords\": [<keywords in both>],\n  \"missing_keywords\": [<important missing keywords>],\n  \"strengths\": [<2-3 strengths>],\n  \"gaps\": [<2-3 gaps>],\n  \"verdict\": \"<one sentence>\"\n}}"""
    try:
        raw = claude(prompt).strip().replace("```json","").replace("```","").strip()
        return jsonify(json.loads(raw))
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/cover-letter",methods=["POST"])
def cover():
    d = request.get_json()
    resume=d.get("resume","").strip(); job=d.get("job_description","").strip()
    company=d.get("company","the company"); role=d.get("role","this role")
    prompt = f"Write a concise 3-paragraph cover letter for this candidate applying to {role} at {company}. Sound human, not like a template. Be direct.\n\nRESUME:\n{resume}\n\nJOB DESCRIPTION:\n{job}"
    try: return jsonify({"cover_letter":claude(prompt)})
    except Exception as e: return jsonify({"error":str(e)}),500

@app.route("/api/health")
def health(): return jsonify({"status":"ok","ai":bool(ANTHROPIC_KEY),"ts":datetime.utcnow().isoformat()})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=False)
