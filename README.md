# SmartApply

Paste a job description and your resume, get an AI-powered match score, keyword gap analysis, and a tailored cover letter.

Built this while applying to internships and wasting time manually comparing resumes to job descriptions. SmartApply automates the first pass.

## Features
- Match Score (0-100)
- Matched vs missing keywords
- Strengths and gaps analysis
- AI cover letter generator

## Tech Stack
- Python, Flask, Gunicorn
- Claude API (Anthropic)
- Vanilla JS
- Render (deployment)

## Getting Started

```bash
git clone https://github.com/hkhatib005/smartapply
cd smartapply
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
python app.py
```

## API
| Method | Route | Description |
|--------|-------|-------------|
| POST | /api/analyze | Match score + keyword analysis |
| POST | /api/cover-letter | Generate cover letter |
| GET | /api/health | Health check |

## License
MIT