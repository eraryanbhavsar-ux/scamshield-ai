from fastapi.testclient import TestClient
from backend.main import app

client=TestClient(app)

def test_message_api_returns_explainable_assessment():
    r=client.post('/api/analyze/message',json={'text':'URGENT: KYC is expired. Share your OTP now or account will be blocked.'})
    assert r.status_code == 200
    data=r.json()
    assert data['score'] >= 70 and data['risk_level'] == 'HIGH'
    assert data['reasons'] and data['actions']

def test_url_api_does_not_need_network_access():
    r=client.post('/api/analyze/url',json={'url':'http://127.0.0.1/kyc/verify'})
    assert r.status_code == 200
    assert r.json()['url_analysis']['host'] == '127.0.0.1'

def test_rejects_empty_message():
    assert client.post('/api/analyze/message',json={'text':''}).status_code == 422
