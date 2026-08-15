# Beginner guide

## What each folder is for

- `frontend/` contains the page people see: `templates/index.html`, its styling, and browser interactions.
- `backend/main.py` is the app’s secure server and API.
- `backend/services/` holds separate analysis features: transparent scoring, safe URL inspection, and optional AI analysis.
- `backend/db.py` stores small local history summaries in `backend/scamshield.db` after the first scan.
- `backend/tests/` contains automated checks.

## Start and stop it

Open a terminal in this project folder, then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Visit `http://127.0.0.1:8000`. To stop the app, click the terminal and press `Ctrl+C`.

## Optional AI key

The app works without an AI key. To add an OpenAI semantic second opinion, get an API key from your OpenAI account, then run this in the same terminal before starting the app:

```bash
export OPENAI_API_KEY="paste-your-key-here"
```

Never place keys in the browser files or upload them to GitHub.

## Screenshot OCR

The app needs Tesseract installed to read screenshot text. On macOS, after installing Homebrew, run `brew install tesseract`; then restart the server. If this isn’t installed, message and URL scanning still work.

## Run tests

With the virtual environment active, run:

```bash
pytest backend/tests -q
```

## Common problems

- **“command not found: uvicorn”** — activate `.venv` and run `pip install -r requirements.txt` again.
- **Port already in use** — use `uvicorn backend.main:app --reload --port 8001` and open port 8001.
- **Screenshot says OCR unavailable** — install Tesseract, then restart the server.
- **AI is not shown** — this is expected without `OPENAI_API_KEY`; the transparent scoring system is still working.
