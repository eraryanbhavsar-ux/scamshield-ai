"""Optional server-only LLM semantic assessment; never required for a safe fallback."""
import json, os

def semantic_assessment(text: str) -> dict | None:
    key = os.getenv("OPENAI_API_KEY")
    if not key: return None
    try:
        from openai import OpenAI
        response = OpenAI(api_key=key).chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), temperature=0,
            response_format={"type": "json_object"},
            messages=[{"role":"system","content":"You assess scam risk. Return JSON only with keys category, confidence (0-100), reasons (array of <=3 plain strings). Do not claim certainty."}, {"role":"user","content":text[:6000]}])
        data=json.loads(response.choices[0].message.content or "{}")
        return data if isinstance(data, dict) else None
    except Exception:
        return None
