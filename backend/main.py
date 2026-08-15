from __future__ import annotations
import io, re
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from backend import db
from backend.services.ai import semantic_assessment
from backend.services.scoring import assess_text
from backend.services.url_analysis import analyze_url as inspect_url

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="ScamShield AI")
app.mount("/static", StaticFiles(directory=ROOT / "frontend" / "static"), name="static")

class TextRequest(BaseModel): text: str = Field(min_length=2, max_length=6000)
class UrlRequest(BaseModel): url: str = Field(min_length=3, max_length=2048)

def level(score: int) -> str: return "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
def actions(score: int) -> list[str]:
    base=["Do not click links or open attachments from this message.", "Verify through the organisation’s official app or website—not the contact details in the message."]
    return (["Do not share an OTP, PIN, password, CVV, or bank details.", "Do not transfer money; report it to cybercrime.gov.in or call 1930 if money is at risk."] + base) if score >= 40 else base + ["If anything feels unusual, contact the sender through a trusted channel."]

def result(text: str, kind: str, url_data: dict | None = None):
    assessment = assess_text(text, (url_data or {}).get("score", 0)); semantic = semantic_assessment(text)
    # Semantic output enriches explanations/category but never controls transparent score.
    category = semantic.get("category") if semantic and isinstance(semantic.get("category"), str) else assessment.category
    confidence = semantic.get("confidence") if semantic and isinstance(semantic.get("confidence"), int) else min(95, 55 + len(assessment.reasons) * 8)
    reasons = assessment.reasons + ([r for r in semantic.get("reasons", []) if isinstance(r, str)][:2] if semantic else [])
    score=assessment.score; risk_level=level(score)
    db.add(kind, re.sub(r"\s+", " ", text).strip(), score, risk_level, category)
    return {"score":score,"risk_level":risk_level,"category":category,"confidence":confidence,"reasons":list(dict.fromkeys(reasons)) or ["No strong known scam patterns were detected."],"phrases":assessment.phrases,"actions":actions(score),"ai_used":bool(semantic),"disclaimer":"This is an automated risk assessment, not a guarantee that content is safe or fraudulent."}

@app.get("/")
def home(): return FileResponse(ROOT / "frontend" / "templates" / "index.html")

@app.post("/api/analyze/message")
def analyze_message(body: TextRequest): return result(body.text, "message")

@app.post("/api/analyze/url")
def analyze_url(body: UrlRequest):
    data=inspect_url(body.url); response=result(body.url, "url", data); response["url_analysis"]=data; return response

@app.post("/api/analyze/screenshot")
async def analyze_screenshot(image: UploadFile = File(...)):
    if image.content_type not in {"image/jpeg","image/png","image/webp"}: raise HTTPException(415, "Please upload a PNG, JPEG, or WebP image.")
    data=await image.read()
    if len(data) > 6_000_000: raise HTTPException(413, "Image must be smaller than 6 MB.")
    try:
        from PIL import Image
        import pytesseract
        extracted=pytesseract.image_to_string(Image.open(io.BytesIO(data))).strip()
    except Exception as exc:
        raise HTTPException(422, "Could not extract text. Install Tesseract OCR and try a sharper image.") from exc
    if len(extracted) < 2: raise HTTPException(422, "No readable text was found in this image.")
    response=result(extracted, "screenshot"); response["extracted_text"]=extracted[:6000]; return response

@app.get("/api/history")
def get_history(): return db.history()
@app.delete("/api/history")
def delete_history(): db.clear(); return {"ok":True}
