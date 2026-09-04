import urllib.request
import json
import sys

AGENT_URL = "http://127.0.0.1:8000"
BACKEND_URL = "http://127.0.0.1:8001"
TOKEN = "firebase_id_token"

def request_json(method, url, payload=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
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

def run_acceptance_tests():
    checklist = {}
    print("==================================================", flush=True)
    print("STARTING FULL AGENT & BACKEND ACCEPTANCE VERIFICATION", flush=True)
    print("==================================================", flush=True)

    # 1. Check OpenAPI docs and routes
    status_docs, openapi = request_json("GET", f"{AGENT_URL}/openapi.json")
    print(f"\n1. OpenAPI Spec ({AGENT_URL}/openapi.json): HTTP {status_docs}", flush=True)
    paths = list(openapi.get("paths", {}).keys()) if isinstance(openapi, dict) else []
    print(f"   Registered Paths: {paths}", flush=True)
    
    checklist["agent_starts_8000"] = status_docs == 200
    checklist["docs_works"] = status_docs == 200
    checklist["agent_chat_exists"] = "/agent/chat" in paths
    checklist["agent_triage_exists"] = "/agent/triage" in paths
    checklist["agent_scheduler_exists"] = "/agent/scheduler" in paths
    checklist["agent_claims_exists"] = "/agent/claims" in paths
    checklist["agent_bed_optimizer_exists"] = "/agent/bed-optimizer" in paths
    checklist["agent_report_analyzer_exists"] = "/agent/report-analyzer" in paths

    # 2. Test Direct Agent /agent/chat
    chat_payload = {"message": "What is hemoglobin?"}
    status_ag_chat, res_ag_chat = request_json("POST", f"{AGENT_URL}/agent/chat", chat_payload)
    print(f"\n2. Direct Agent /agent/chat -> HTTP {status_ag_chat}", flush=True)
    if isinstance(res_ag_chat, dict):
        msg = res_ag_chat.get("message", "")
        print(f"   Response message: {msg[:120]}...", flush=True)
        is_fallback = "safety fallback mode" in msg or "operating in safety mode" in msg
        checklist["direct_agent_chat_200"] = status_ag_chat == 200 and not is_fallback
        checklist["health_assistant_featherless_response"] = status_ag_chat == 200 and not is_fallback

    # 3. Test Direct Agent /agent/scheduler
    sched_payload = {
        "patient_id": "user_123",
        "medications": [
            {
                "medication_name": "Amoxicillin",
                "prescribed_dosage": "500mg",
                "prescribed_frequency": "Three times daily",
                "meal_relationship": "AFTER_MEAL",
                "prescribed_duration_days": 7
            },
            {
                "medication_name": "Paracetamol",
                "prescribed_dosage": "500mg",
                "prescribed_frequency": "Twice daily",
                "meal_relationship": "AFTER_MEAL",
                "prescribed_duration_days": 5
            }
        ],
        "user_wake_time": "08:00",
        "user_sleep_time": "22:00"
    }
    status_ag_sched, res_ag_sched = request_json("POST", f"{AGENT_URL}/agent/scheduler", sched_payload)
    print(f"\n3. Direct Agent /agent/scheduler -> HTTP {status_ag_sched}", flush=True)
    if isinstance(res_ag_sched, dict):
        reminders = res_ag_sched.get("scheduled_reminders", [])
        print(f"   Generated Reminders Count: {len(reminders)}", flush=True)
        for r in reminders[:3]:
            print(f"   - {r.get('medication_name')} {r.get('dosage')} at {r.get('scheduled_time')}", flush=True)
        checklist["direct_agent_scheduler_200"] = status_ag_sched == 200 and len(reminders) > 0
        checklist["medication_scheduler_reminders"] = status_ag_sched == 200 and len(reminders) > 0

    # 4. Backend -> Agent /chat
    status_bk_chat, res_bk_chat = request_json("POST", f"{BACKEND_URL}/api/v1/chat", {"message": "What is hemoglobin?"}, token=TOKEN)
    print(f"\n4. Backend -> Agent /chat (POST /api/v1/chat) -> HTTP {status_bk_chat}", flush=True)
    checklist["backend_agent_chat"] = status_bk_chat == 200

    # 5. Backend -> Agent /scheduler
    bk_sched_payload = {
        "patientId": "user_123",
        "medications": [
            {"name": "Amoxicillin", "dosage": "500mg", "frequency": "Three times daily", "mealRelationship": "AFTER_MEAL"},
            {"name": "Paracetamol", "dosage": "500mg", "frequency": "Twice daily", "mealRelationship": "AFTER_MEAL"}
        ],
        "wakeTime": "08:00",
        "sleepTime": "22:00"
    }
    status_bk_sched, res_bk_sched = request_json("POST", f"{BACKEND_URL}/api/v1/medications/schedule", bk_sched_payload, token=TOKEN)
    print(f"5. Backend -> Agent /scheduler (POST /api/v1/medications/schedule) -> HTTP {status_bk_sched}", flush=True)
    checklist["backend_agent_scheduler"] = status_bk_sched == 200

    # 6. Backend -> Agent /report-analyzer
    bk_rep_payload = {"reportText": "CBC Report: Hemoglobin 14.2 g/dL, WBC 6500", "reportTitle": "Complete Blood Count"}
    status_bk_rep, res_bk_rep = request_json("POST", f"{BACKEND_URL}/api/v1/reports/analyze", bk_rep_payload, token=TOKEN)
    print(f"6. Backend -> Agent /report-analyzer (POST /api/v1/reports/analyze) -> HTTP {status_bk_rep}", flush=True)
    checklist["backend_agent_report_analyzer"] = status_bk_rep == 200
    checklist["report_analyzer_reaches_agent"] = status_bk_rep == 200

    # 7. Backend -> Agent /triage
    bk_triage_payload = {"symptoms": "Severe chest pain and shortness of breath", "location": {"lat": 17.44, "lng": 78.39}, "patientAge": 45}
    status_bk_triage, res_bk_triage = request_json("POST", f"{BACKEND_URL}/api/v1/triage/emergency", bk_triage_payload, token=TOKEN)
    print(f"7. Backend -> Agent /triage (POST /api/v1/triage/emergency) -> HTTP {status_bk_triage}", flush=True)
    checklist["backend_agent_triage"] = status_bk_triage == 200
    checklist["emergency_triage_reaches_agent"] = status_bk_triage == 200

    # 8. Backend -> Agent /claims
    bk_claims_payload = {"patientId": "user_123", "insuranceProvider": "Apollo", "policyNumber": "POL-99281", "claimedAmount": 5000.0}
    status_bk_claims, res_bk_claims = request_json("POST", f"{BACKEND_URL}/api/v1/claims", bk_claims_payload, token=TOKEN)
    print(f"8. Backend -> Agent /claims (POST /api/v1/claims) -> HTTP {status_bk_claims}", flush=True)
    checklist["backend_agent_claims"] = status_bk_claims == 200

    # 9. Backend -> Agent /bed-optimizer
    bk_beds_payload = {"requestedBedType": "ICU", "patientUrgency": "HIGH"}
    status_bk_beds, res_bk_beds = request_json("POST", f"{BACKEND_URL}/api/v1/beds/optimize", bk_beds_payload, token=TOKEN)
    print(f"9. Backend -> Agent /bed-optimizer (POST /api/v1/beds/optimize) -> HTTP {status_bk_beds}", flush=True)
    checklist["backend_agent_bed_optimizer"] = status_bk_beds == 200

    print("\n==========================================", flush=True)
    print("FINAL ACCEPTANCE CHECKLIST", flush=True)
    print("==========================================", flush=True)
    all_passed = True
    for key, val in checklist.items():
        symbol = "[x]" if val else "[ ]"
        if not val: all_passed = False
        print(f"{symbol} {key}: {'PASS' if val else 'FAIL'}", flush=True)
    
    print(f"\nOVERALL STATUS: {'ALL CRITERIA PASSED SUCCESSFULLY' if all_passed else 'SOME CRITERIA FAILED'}", flush=True)

if __name__ == "__main__":
    run_acceptance_tests()
