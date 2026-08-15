# ScamShield AI

**Stop the scam before you pay.** ScamShield AI is a hackathon-ready early-warning web app that assesses suspicious messages, screenshots, and URLs. It is an assistive risk assessment, not a guarantee that something is safe or fraudulent.

## What it does

- Scans SMS, WhatsApp messages, and email text for explainable scam signals.
- Checks URL structure safely without visiting or crawling submitted links.
- Extracts screenshot text with OCR, then applies the same analysis pipeline.
- Assigns a transparent 0–100 risk score and Low / Medium / High assessment.
- Keeps only short local scan summaries in SQLite; history can be deleted in one click.
- Includes fictional, safe demo cases for hackathon judging.

## Architecture

```
Browser → FastAPI API → input validation → URL signals / OCR → scoring engine
                                                ↘ optional server-side LLM
                                                          ↓
                                                 SQLite scan summary history
```

The deterministic scoring engine is always used, so an LLM outage does not stop the app. If configured, a server-only OpenAI call adds category/reasoning context but does **not** set the numerical risk score.

## Run locally

Requires Python 3.10+ and (for screenshots) the Tesseract system application.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000. Stop with `Ctrl+C`.

## Optional AI configuration

Copy `.env.example` values into your shell (do not commit real keys):

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4.1-mini"
```

Without a key, ScamShield remains fully functional using its transparent rules-based assessment. API keys are never sent to browser code.

## Tests

```bash
pytest backend/tests -q
```

## Publish it publicly (Render)

1. Create a GitHub repository and upload this entire project folder. Keep `.gitignore`; it prevents API keys and local scan history from being uploaded.
2. Create a free Render account, select **New → Blueprint**, and connect the GitHub repository.
3. Render reads `render.yaml` and the included `Dockerfile` (which also installs screenshot OCR). Click **Apply** and wait for the deploy to complete.
4. Share the generated `https://scamshield-ai.onrender.com`-style URL. If you use OpenAI, add `OPENAI_API_KEY` in Render's Environment settings; never put the key in GitHub.

## Limitations and safety

URL checks are structural only and deliberately do not open submitted URLs. OCR depends on text clarity and Tesseract being installed. This MVP detects common patterns and can make mistakes; verify important communications using an organisation’s genuine website/app. Never share OTPs, PINs, passwords, CVVs, or financial details.

## Future improvements

Add Indian-language OCR, calibrated model evaluation data, brand/domain allow-lists, a privacy-preserving cloud history option, and official reporting integrations.
