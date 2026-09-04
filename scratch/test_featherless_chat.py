import urllib.request
import json
import sys

BACKEND_URL = "http://127.0.0.1:8001"
TOKEN = "firebase_id_token"

def send_chat(message):
    url = f"{BACKEND_URL}/api/v1/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    payload = {
        "message": message,
        "patientProfile": {
            "patient_name": "Demo Patient",
            "patient_age": 45,
            "active_conditions": ["Hypertension"],
            "current_medications": ["Amoxicillin 500mg twice daily", "Aspirin 75mg daily"],
            "latest_lab_results": {"Hemoglobin": "14.2 g/dL", "WBC": "6500 /mcL", "Glucose": "95 mg/dL"},
            "insurance_policy": "Apollo Health Emergency Plan (Policy #POL-99281, Claim CLM-992 Status: APPROVED for INR 5,000)"
        }
    }
    
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return resp.status, data
    except Exception as e:
        return 0, str(e)

def run_tests():
    queries = [
        "What is hemoglobin?",
        "What was my latest hemoglobin?",
        "What medications are scheduled for me?",
        "What is the status of my insurance claim?",
        "I am experiencing severe chest pain"
    ]

    for q in queries:
        print(f"\n==========================================", flush=True)
        print(f"QUERY: '{q}'", flush=True)
        status, res = send_chat(q)
        print(f"HTTP Status: {status}", flush=True)
        if isinstance(res, dict) and res.get("success"):
            data = res.get("data", {})
            msg = data.get("message") or data.get("reply") or str(data)
            intent = data.get("intent")
            print(f"INTENT: {intent}", flush=True)
            print(f"AI RESPONSE:\n{msg}", flush=True)
            is_fallback = "operating in safety mode" in msg or "safety fallback mode" in msg
            print(f"FALLBACK DETECTED: {is_fallback}", flush=True)
        else:
            print(f"ERROR: {res}", flush=True)

if __name__ == "__main__":
    run_tests()
