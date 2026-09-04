import urllib.request
import json
import sys

AGENT_URL = "http://127.0.0.1:8000"
BACKEND_URL = "http://127.0.0.1:8001"
TOKEN = "firebase_id_token"

def request_json(url, payload, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
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
    test_queries = [
        ("1. GENERAL", "What is hemoglobin?"),
        ("2. USER-SPECIFIC", "What was my latest hemoglobin?"),
        ("3. HISTORICAL", "How has my hemoglobin changed?"),
        ("4. MEDICATION", "What medications am I currently scheduled to take?"),
        ("5. INSURANCE", "Do I have an insurance claim?"),
        ("6. EMERGENCY", "I'm having severe chest pain and difficulty breathing."),
        ("7. UNKNOWN", "Tell me something you know about me that isn't in my data.")
    ]

    print("==================================================", flush=True)
    print("STARTING END-TO-END CHATBOT FEATHERLESS VERIFICATION", flush=True)
    print("==================================================", flush=True)

    results = []
    for label, query in test_queries:
        print(f"\n--- {label}: '{query}' ---", flush=True)
        # Direct Agent Call
        status_ag, res_ag = request_json(f"{AGENT_URL}/agent/chat", {"message": query})
        msg_ag = res_ag.get("message", str(res_ag)) if isinstance(res_ag, dict) else str(res_ag)
        intent_ag = res_ag.get("intent", "UNKNOWN") if isinstance(res_ag, dict) else "UNKNOWN"
        print(f"Agent Port 8000: HTTP {status_ag} | Intent: {intent_ag}")
        print(f"Response: {msg_ag[:200]}...")

        # Backend Proxy Call
        status_bk, res_bk = request_json(f"{BACKEND_URL}/api/v1/chat", {"message": query}, token=TOKEN)
        data_bk = res_bk.get("data", {}) if isinstance(res_bk, dict) else {}
        msg_bk = data_bk.get("message") or data_bk.get("reply") or str(res_bk)
        print(f"Backend Port 8001: HTTP {status_bk}")
        print(f"Response: {msg_bk[:200]}...")

        pass_flag = (status_ag == 200) and (status_bk == 200) and ("safety fallback mode" not in msg_ag.lower())
        results.append((label, pass_flag, intent_ag, msg_bk[:150]))

    print("\n==========================================", flush=True)
    print("CHATBOT VERIFICATION SUMMARY", flush=True)
    print("==========================================", flush=True)
    all_pass = True
    for label, pass_flag, intent, text in results:
        status_str = "PASS" if pass_flag else "FAIL"
        if not pass_flag: all_pass = False
        print(f"[{'x' if pass_flag else ' '}] {label}: {status_str} (Intent: {intent})\n    Preview: {text}...\n")

    print(f"OVERALL E2E STATUS: {'ALL PASSED SUCCESSFULLY' if all_pass else 'FEATHERLESS UNREACHABLE / FALLBACK'}")

if __name__ == "__main__":
    run_tests()
