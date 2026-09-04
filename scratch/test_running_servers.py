import urllib.request
import json

def test_ep(name, url, payload=None, headers=None):
    if headers is None: headers = {}
    headers['Content-Type'] = 'application/json'
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method='POST' if payload else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode('utf-8')
            print(f"[OK] {name}: HTTP {resp.status}\n   Response: {body[:300]}\n")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        print(f"[HTTP ERROR] {name}: HTTP {e.code}\n   Error Body: {err_body[:300]}\n")
    except Exception as e:
        print(f"[EXCEPTION] {name}: -> {e}\n")

if __name__ == "__main__":
    print("--- TESTING LIVE SERVERS ---")
    test_ep("Agent OpenAPI", "http://127.0.0.1:8000/openapi.json")
    test_ep("Agent /agent/chat", "http://127.0.0.1:8000/agent/chat", {"message": "What is hemoglobin?"})
    test_ep("Agent /agent/triage", "http://127.0.0.1:8000/agent/triage", {"symptoms": "Chest pain"})
    test_ep("Backend Health", "http://127.0.0.1:8001/health")
    test_ep("Backend /api/v1/chat (no auth)", "http://127.0.0.1:8001/api/v1/chat", {"message": "What is hemoglobin?"})
    test_ep("Backend /api/v1/chat (with auth)", "http://127.0.0.1:8001/api/v1/chat", {"message": "What is hemoglobin?"}, {"Authorization": "Bearer mock_token"})
