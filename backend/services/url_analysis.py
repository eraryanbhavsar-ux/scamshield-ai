from __future__ import annotations
import ipaddress, re
from urllib.parse import urlparse

HIGH_RISK_WORDS = ("kyc", "verify", "login", "otp", "secure", "reward", "prize", "refund", "upi", "bank")
BRANDS = ("sbi", "hdfc", "icici", "axis", "paytm", "phonepe", "googlepay", "amazon", "rbi")

def analyze_url(raw_url: str) -> dict:
    candidate = raw_url.strip()
    if not re.match(r"^https?://", candidate, re.I): candidate = "http://" + candidate
    p = urlparse(candidate); host = (p.hostname or "").lower(); reasons=[]; score=0
    if p.scheme != "https": score += 18; reasons.append("Does not use HTTPS")
    try: ipaddress.ip_address(host); score += 32; reasons.append("Uses an IP address instead of a normal domain")
    except ValueError: pass
    if host.count(".") >= 3: score += 12; reasons.append("Has an unusually deep subdomain structure")
    if len(candidate) > 100: score += 10; reasons.append("URL is unusually long")
    words = [w for w in HIGH_RISK_WORDS if w in candidate.lower()]
    if words: score += min(28, 7 * len(words)); reasons.append("Contains high-risk keywords: " + ", ".join(words[:4]))
    if any(b in host for b in BRANDS) and not host.endswith((".com", ".in", ".org")):
        score += 18; reasons.append("Brand-like name appears on an unusual domain")
    if "@" in p.netloc or "xn--" in host: score += 20; reasons.append("Uses a misleading URL structure")
    if len(p.query) > 80: score += 8; reasons.append("Contains a long query string")
    return {"score": min(score, 100), "host": host or "Could not identify host", "https": p.scheme == "https", "reasons": reasons or ["No obvious structural risk signals found. Still verify the sender independently."], "normalized_url": candidate}
