import urllib.request
import json

AGENT_URL = "http://127.0.0.1:8000"
BACKEND_URL = "http://127.0.0.1:8001"
TOKEN = "firebase_id_token"

def test_agent_directly():
    print("\n==========================================")
    print("TEST 1 — Agent directly (port 8000)")
    print("==========================================")
    url = f"{AGENT_URL}/agent/chat"
    payload = {"message": "What is hemoglobin?"}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            res_json = json.loads(resp.read().decode("utf-8"))
            print(f"HTTP Status: {status}")
            print(f"Agent Response JSON keys: {list(res_json.keys())}")
            print(f"Agent 'message' field: {res_json.get('message')[:100]}...")
            print(f"Agent 'reply' field: {res_json.get('reply')}")
            return status, res_json
    except Exception as e:
        print(f"Error calling Agent: {e}")
        return 0, str(e)

def test_backend():
    print("\n==========================================")
    print("TEST 2 — Backend (port 8001)")
    print("==========================================")
    url = f"{BACKEND_URL}/api/v1/chat"
    payload = {"message": "What is hemoglobin?"}
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            res_json = json.loads(resp.read().decode("utf-8"))
            print(f"HTTP Status: {status}")
            print(f"Backend Response Outer keys: {list(res_json.keys())}")
            data_dict = res_json.get("data", {})
            print(f"Backend 'data' keys: {list(data_dict.keys())}")
            print(f"Backend data['message']: {data_dict.get('message')[:100] if data_dict.get('message') else None}")
            print(f"Backend data['reply']: {data_dict.get('reply')}")
            return status, res_json
    except Exception as e:
        print(f"Error calling Backend: {e}")
        return 0, str(e)

if __name__ == "__main__":
    test_agent_directly()
    test_backend()
