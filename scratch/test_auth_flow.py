import urllib.request
import json
import sys

BACKEND_URL = "http://127.0.0.1:8001"
AGENT_URL = "http://127.0.0.1:8000"

def make_request(method, url, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            status_code = resp.status
            res_body = json.loads(resp.read().decode("utf-8"))
            return status_code, res_body
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(err_body)
        except Exception:
            err_json = err_body
        return e.code, err_json
    except Exception as e:
        return 0, str(e)

def run_tests():
    results = {}
    print("--- Starting Auth Flow Verification ---", flush=True)

    # 0. Health checks
    ag_status, ag_health = make_request("GET", f"{AGENT_URL}/health")
    print(f"Agent Health ({AGENT_URL}/health): HTTP {ag_status} -> {ag_health}", flush=True)
    bk_status, bk_health = make_request("GET", f"{BACKEND_URL}/health")
    print(f"Backend Health ({BACKEND_URL}/health): HTTP {bk_status} -> {bk_health}", flush=True)

    # A. Signup
    signup_data = {"email": "test_user@lifelink.ai", "password": "password123", "name": "Test User"}
    status_a, res_a = make_request("POST", f"{BACKEND_URL}/api/v1/auth/signup", signup_data)
    print(f"\nA. Signup: HTTP {status_a} -> {json.dumps(res_a)}", flush=True)
    results['signup'] = status_a == 200 and res_a.get('success') == True

    # B. Login
    login_data = {"email": "test_user@lifelink.ai", "password": "password123"}
    status_b, res_b = make_request("POST", f"{BACKEND_URL}/api/v1/auth/login", login_data)
    print(f"B. Login: HTTP {status_b} -> {json.dumps(res_b)}", flush=True)
    results['login'] = status_b == 200 and res_b.get('success') == True
    
    token = res_b.get('data', {}).get('token') if isinstance(res_b, dict) and res_b.get('data') else "firebase_id_token"
    print(f"Token obtained: {token}", flush=True)

    # C. GET /api/v1/medications/user_123
    status_c, res_c = make_request("GET", f"{BACKEND_URL}/api/v1/medications/user_123", token=token)
    print(f"\nC. Medications GET: HTTP {status_c} -> {json.dumps(res_c)[:200]}", flush=True)
    results['medications_get'] = status_c == 200

    # D. GET /api/v1/beds/HOSP-01
    status_d, res_d = make_request("GET", f"{BACKEND_URL}/api/v1/beds/HOSP-01", token=token)
    print(f"D. Beds GET: HTTP {status_d} -> {json.dumps(res_d)[:200]}", flush=True)
    results['beds_get'] = status_d == 200

    # E. POST /api/v1/chat
    chat_payload = {"message": "What is hemoglobin?"}
    status_e, res_e = make_request("POST", f"{BACKEND_URL}/api/v1/chat", chat_payload, token=token)
    print(f"E. Chat POST: HTTP {status_e} -> {json.dumps(res_e)[:300]}", flush=True)
    results['chat'] = status_e == 200

    # Check chatbot response quality
    reply = res_e.get('data', {}).get('reply', '') if isinstance(res_e, dict) else ''
    is_fallback = "operating in safety mode" in reply or "safety fallback mode" in reply
    results['chatbot_response'] = status_e == 200 and not is_fallback
    print(f"   Chatbot Live Response: {reply[:150]}...", flush=True)
    print(f"   Chatbot Live Check: {'PASS' if not is_fallback else 'FAIL (Fallback returned)'}", flush=True)

    # F. POST /api/v1/medications/schedule
    med_sched_payload = {
        "patientId": "user_123",
        "medications": [{"name": "Aspirin", "dosage": "75mg", "frequency": "Daily", "mealRelationship": "AFTER_MEAL", "durationDays": 7}],
        "wakeTime": "08:00",
        "sleepTime": "22:00"
    }
    status_f, res_f = make_request("POST", f"{BACKEND_URL}/api/v1/medications/schedule", med_sched_payload, token=token)
    print(f"\nF. Medication Schedule POST: HTTP {status_f} -> {json.dumps(res_f)[:200]}", flush=True)
    results['medications_schedule'] = status_f == 200

    # G. POST /api/v1/reports/analyze
    report_payload = {"reportText": "Hemoglobin: 14.5 g/dL (Normal). WBC: 6500 /mcL.", "reportTitle": "Complete Blood Count"}
    status_g, res_g = make_request("POST", f"{BACKEND_URL}/api/v1/reports/analyze", report_payload, token=token)
    print(f"G. Reports Analyze POST: HTTP {status_g} -> {json.dumps(res_g)[:200]}", flush=True)
    results['reports'] = status_g == 200

    # H. POST /api/v1/claims
    claim_payload = {"patientId": "user_123", "insuranceProvider": "Apollo Health", "policyNumber": "POL-99281", "claimedAmount": 5000.0}
    status_h, res_h = make_request("POST", f"{BACKEND_URL}/api/v1/claims", claim_payload, token=token)
    print(f"H. Claims POST: HTTP {status_h} -> {json.dumps(res_h)[:200]}", flush=True)
    results['claims'] = status_h == 200

    # I. POST /api/v1/triage/emergency
    triage_payload = {
        "symptoms": "Severe chest pain and shortness of breath",
        "location": {"lat": 17.4486, "lng": 78.3908},
        "patientAge": 45,
        "medicalHistory": ["Hypertension"]
    }
    status_i, res_i = make_request("POST", f"{BACKEND_URL}/api/v1/triage/emergency", triage_payload, token=token)
    print(f"I. Emergency Triage POST: HTTP {status_i} -> {json.dumps(res_i)[:200]}", flush=True)
    results['triage'] = status_i == 200

    print("\n--- FINAL VERIFICATION RESULTS SUMMARY ---", flush=True)
    for key, val in results.items():
        print(f"{key}: {'PASS' if val else 'FAIL'}", flush=True)

if __name__ == "__main__":
    run_tests()
