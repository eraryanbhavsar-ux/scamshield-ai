"""Transparent, deterministic risk scoring used for every analysis."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


CATEGORY_PATTERNS = {
    "Fake KYC / Bank Impersonation": [r"\bkyc\b", r"bank account", r"account (?:will be )?blocked", r"verify (?:your )?(?:account|details)"],
    "UPI / Payment Scam": [r"\bupi\b", r"(?:pay|send|transfer) (?:rs\.?|₹|inr)?\s*\d", r"collect request", r"scan (?:this )?qr"],
    "Digital Arrest Scam": [r"digital arrest", r"police case", r"arrest warrant", r"stay on (?:the )?call", r"cbi|cyber crime (?:department|cell)"],
    "Job Scam": [r"work from home", r"job offer", r"earn \d", r"registration fee", r"part.?time job"],
    "Investment Scam": [r"guaranteed return", r"double your money", r"crypto (?:profit|investment)", r"risk.?free investment"],
    "Courier / Delivery Scam": [r"courier", r"parcel", r"delivery (?:failed|fee|charge)", r"customs (?:fee|charge)"],
    "Fake Customer-Care Scam": [r"customer care", r"helpline", r"remote access", r"anydesk|teamviewer"],
    "OTP / Password Theft": [r"\botp\b", r"(?:share|send|tell).{0,30}(?:pin|password|cvv|otp)", r"password"],
    "Lottery / Prize Scam": [r"(?:won|winner).{0,30}(?:prize|lottery|reward)", r"claim (?:your )?(?:prize|reward)", r"free iphone"],
    "Government Impersonation": [r"income tax", r"aadhaar", r"government (?:notice|department)", r"rbi\b"],
    "Romance / Social Engineering Scam": [r"don't tell anyone", r"trust me", r"emergency.{0,30}money", r"love you"],
}

SIGNALS = {
    "urgency": (14, [r"urgent", r"immediately", r"today", r"within \d+ hours?", r"act now", r"last chance"]),
    "threat": (16, [r"blocked", r"suspended", r"arrest", r"legal action", r"penalty", r"deactivate"]),
    "financial request": (17, [r"(?:pay|send|transfer|deposit) (?:rs\.?|₹|inr)?\s*\d", r"payment", r"fee", r"refund"]),
    "credential request": (18, [r"password", r"pin", r"cvv", r"login details", r"card details"]),
    "OTP request": (22, [r"\botp\b", r"one.?time password", r"verification code"]),
    "impersonation": (13, [r"your bank", r"bank account", r"rbi\b", r"police", r"government", r"customer care"]),
    "unrealistic reward": (15, [r"guaranteed", r"won", r"free", r"double your", r"risk.?free"]),
    "manipulation": (10, [r"don't tell", r"keep this secret", r"stay on (?:the )?call", r"trust me"]),
}


@dataclass
class Assessment:
    score: int
    category: str
    reasons: list[str] = field(default_factory=list)
    phrases: list[str] = field(default_factory=list)
    signals: dict[str, bool] = field(default_factory=dict)


def assess_text(text: str, url_risk: int = 0) -> Assessment:
    lowered = text.lower()
    score, reasons, phrases, signals = 0, [], [], {}
    for name, (points, patterns) in SIGNALS.items():
        hits = [m.group(0) for pattern in patterns if (m := re.search(pattern, lowered, re.I))]
        signals[name] = bool(hits)
        if hits:
            score += points
            reasons.append(_reason(name))
            phrases.extend(hits[:2])
    if re.search(r"https?://|\bwww\.", lowered):
        score += 10 + min(10, url_risk // 10)
        reasons.append("Contains a link that should be independently verified")
    category, matches = _category(lowered)
    if category != "General phishing / suspicious message":
        score += 10
        phrases.extend(matches[:2])
    # Several suspicious signals matter more together, but cap predictable outputs.
    active = sum(signals.values())
    if active >= 3:
        score += 8
    return Assessment(min(100, score), category, _unique(reasons), _unique(phrases)[:8], signals)


def _category(text: str) -> tuple[str, list[str]]:
    best, found = "General phishing / suspicious message", []
    for category, patterns in CATEGORY_PATTERNS.items():
        hits = [m.group(0) for pattern in patterns if (m := re.search(pattern, text, re.I))]
        if len(hits) > len(found): best, found = category, hits
    return best, found

def _reason(signal: str) -> str:
    return {
        "urgency": "Uses urgency to reduce time for careful verification", "threat": "Uses a threat or consequence to pressure you",
        "financial request": "Requests money or a payment-related action", "credential request": "Requests sensitive credentials", "OTP request": "Mentions an OTP or verification code",
        "impersonation": "Uses authority or organisation language that may be impersonation", "unrealistic reward": "Makes an unusually attractive reward or return claim",
        "manipulation": "Uses pressure or secrecy tactics common in social engineering",
    }[signal]

def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(v for v in values if v))
