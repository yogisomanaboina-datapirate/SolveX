import urllib.request
import json
import sys

AGENT_URL = "http://127.0.0.1:8000"
BACKEND_URL = "http://127.0.0.1:8001"
TOKEN = "firebase_id_token"

def post_json(url, payload, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            res_body = json.loads(resp.read().decode("utf-8"))
            return status, res_body
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(err_body)
        except Exception:
            err_json = err_body
        return e.code, err_json
    except Exception as e:
        return 0, str(e)

def verify_agent_endpoints():
    print("=== DIRECT AGENT ENDPOINT VERIFICATION (Port 8000) ===")
    
    # 1. /agent/chat
    chat_payload = {"message": "What is hemoglobin?"}
    st_chat, res_chat = post_json(f"{AGENT_URL}/agent/chat", chat_payload)
    print(f"\n1. POST /agent/chat -> HTTP {st_chat}")
    if st_chat == 200:
        print(f"   Intent: {res_chat.get('intent')}")
        print(f"   Message: {res_chat.get('message')[:100]}...")
    else:
        print(f"   Error: {res_chat}")

    # 2. /agent/triage
    triage_payload = {"symptoms": "Severe chest pain", "patient_age": 45, "location": {"lat": 17.44, "lng": 78.39}}
    st_triage, res_triage = post_json(f"{AGENT_URL}/agent/triage", triage_payload)
    print(f"\n2. POST /agent/triage -> HTTP {st_triage}")
    if st_triage == 200:
        print(f"   Severity: {res_triage.get('severity') or res_triage.get('urgency')}")
        print(f"   Reasoning: {res_triage.get('reasoning')[:100]}...")
    else:
        print(f"   Error: {res_triage}")

    # 3. /agent/scheduler
    sched_payload = {
        "patient_id": "user_123",
        "medications": [{"medication_name": "Aspirin", "prescribed_dosage": "75mg", "prescribed_frequency": "Daily", "meal_relationship": "AFTER_MEAL", "prescribed_duration_days": 7}],
        "user_wake_time": "08:00",
        "user_sleep_time": "22:00"
    }
    st_sched, res_sched = post_json(f"{AGENT_URL}/agent/scheduler", sched_payload)
    print(f"\n3. POST /agent/scheduler -> HTTP {st_sched}")
    if st_sched == 200:
        print(f"   Reminders count: {len(res_sched.get('scheduled_reminders', []))}")
    else:
        print(f"   Error: {res_sched}")

    # 4. /agent/claims
    claims_payload = {"user_request": "Claim for emergency treatment under policy POL-99281"}
    st_claims, res_claims = post_json(f"{AGENT_URL}/agent/claims", claims_payload)
    print(f"\n4. POST /agent/claims -> HTTP {st_claims}")
    if st_claims == 200:
        print(f"   Reasoning: {res_claims.get('reasoning')[:100]}...")
    else:
        print(f"   Error: {res_claims}")

    # 5. /agent/bed-optimizer
    bed_payload = {"target_hospital_id": "HOSP-01", "requested_bed_type": "ICU", "patient_urgency": "HIGH"}
    st_bed, res_bed = post_json(f"{AGENT_URL}/agent/bed-optimizer", bed_payload)
    print(f"\n5. POST /agent/bed-optimizer -> HTTP {st_bed}")
    if st_bed == 200:
        print(f"   Recommendation: {res_bed.get('recommended_allocation')}")
    else:
        print(f"   Error: {res_bed}")

    # 6. /agent/report-analyzer
    rep_payload = {"report_text": "CBC Report: Hemoglobin 14.2 g/dL, WBC 6500", "report_title": "Lab Report"}
    st_rep, res_rep = post_json(f"{AGENT_URL}/agent/report-analyzer", rep_payload)
    print(f"\n6. POST /agent/report-analyzer -> HTTP {st_rep}")
    if st_rep == 200:
        print(f"   Summary: {res_rep.get('summary')[:100]}...")
    else:
        print(f"   Error: {res_rep}")

def verify_backend_integration():
    print("\n=== BACKEND TO AGENT INTEGRATION VERIFICATION (Port 8001 -> Port 8000) ===")
    
    # 1. Chat
    st_b_chat, res_b_chat = post_json(f"{BACKEND_URL}/api/v1/chat", {"message": "What is hemoglobin?"}, token=TOKEN)
    print(f"\nBackend POST /api/v1/chat -> HTTP {st_b_chat}")
    print(f"   Response message: {res_b_chat.get('data', {}).get('message')[:100] if isinstance(res_b_chat, dict) else res_b_chat}")

    # 2. Triage
    st_b_triage, res_b_triage = post_json(f"{BACKEND_URL}/api/v1/triage/emergency", {
        "symptoms": "Severe chest pain and shortness of breath",
        "location": {"lat": 17.4486, "lng": 78.3908},
        "patientAge": 45
    }, token=TOKEN)
    print(f"\nBackend POST /api/v1/triage/emergency -> HTTP {st_b_triage}")
    print(f"   Severity: {res_b_triage.get('data', {}).get('severity') if isinstance(res_b_triage, dict) else res_b_triage}")

    # 3. Medications Schedule
    st_b_sched, res_b_sched = post_json(f"{BACKEND_URL}/api/v1/medications/schedule", {
        "medications": [{"name": "Aspirin", "dosage": "75mg"}]
    }, token=TOKEN)
    print(f"\nBackend POST /api/v1/medications/schedule -> HTTP {st_b_sched}")

    # 4. Claims
    st_b_claims, res_b_claims = post_json(f"{BACKEND_URL}/api/v1/claims", {
        "patientId": "user_123", "insuranceProvider": "Apollo", "policyNumber": "POL-123", "claimedAmount": 5000.0
    }, token=TOKEN)
    print(f"\nBackend POST /api/v1/claims -> HTTP {st_b_claims}")

    # 5. Beds Optimize
    st_b_beds, res_b_beds = post_json(f"{BACKEND_URL}/api/v1/beds/optimize", {
        "requestedBedType": "ICU", "patientUrgency": "HIGH"
    }, token=TOKEN)
    print(f"\nBackend POST /api/v1/beds/optimize -> HTTP {st_b_beds}")

    # 6. Reports Analyze
    st_b_rep, res_b_rep = post_json(f"{BACKEND_URL}/api/v1/reports/analyze", {
        "reportText": "Hemoglobin 14.2 g/dL"
    }, token=TOKEN)
    print(f"\nBackend POST /api/v1/reports/analyze -> HTTP {st_b_rep}")

if __name__ == "__main__":
    verify_agent_endpoints()
    verify_backend_integration()
