from backend.services.scoring import assess_text
from backend.services.url_analysis import analyze_url

def test_kyc_is_high_risk():
    r=assess_text("URGENT KYC expired. Account blocked today. Share OTP and verify http://bad.xyz")
    assert r.score >= 70 and r.category == "Fake KYC / Bank Impersonation"
def test_safe_message_is_low_risk():
    assert assess_text("Your dentist appointment is tomorrow at 10 AM.").score < 40
def test_ip_url_is_risky():
    r=analyze_url("http://192.168.10.10/verify?otp=1")
    assert r["score"] >= 40 and any("IP address" in x for x in r["reasons"])
def test_https_normal_url_has_no_structural_alert():
    assert analyze_url("https://example.com/about")["score"] == 0
