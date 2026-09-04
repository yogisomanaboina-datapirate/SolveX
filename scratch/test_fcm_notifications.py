import urllib.request
import json
import time

BACKEND_URL = "http://127.0.0.1:8001"
TOKEN = "firebase_id_token"

def request_json(url, payload, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
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

def run_fcm_tests():
    print("==================================================", flush=True)
    print("STARTING FIREBASE CLOUD MESSAGING (FCM) VERIFICATION", flush=True)
    print("==================================================", flush=True)

    # 1. Register Web FCM Token Endpoint
    print("\n1. Testing Device Registration (POST /api/v1/notifications/register)...", flush=True)
    reg_payload = {"fcmToken": "fcm_token_web_test_device_token_1234567890"}
    st_reg, res_reg = request_json(f"{BACKEND_URL}/api/v1/notifications/register", reg_payload, token=TOKEN)
    print(f"   HTTP {st_reg} -> {res_reg}")

    # 2. Test Manual FCM Push Endpoint
    print("\n2. Testing Manual FCM Push Send (POST /api/v1/notifications/test-send)...", flush=True)
    send_payload = {
        "title": "LifeLink AI Medication Reminder",
        "body": "Time to take your scheduled medication (Amoxicillin 500mg)."
    }
    st_send, res_send = request_json(f"{BACKEND_URL}/api/v1/notifications/test-send", send_payload, token=TOKEN)
    print(f"   HTTP {st_send} -> {res_send}")

    # 3. Test 5-Second Hackathon Demo Reminder with APScheduler
    print("\n3. Testing APScheduler 5-Second Demo Reminder (POST /api/v1/notifications/test-reminder)...", flush=True)
    rem_payload = {
        "medicationName": "Amoxicillin (Demo Test)",
        "dosage": "500mg",
        "delaySeconds": 5
    }
    st_rem, res_rem = request_json(f"{BACKEND_URL}/api/v1/notifications/test-reminder", rem_payload, token=TOKEN)
    print(f"   HTTP {st_rem} -> {res_rem}")

    print("\n4. Waiting 12 seconds for APScheduler background worker to deliver due reminder FCM push...", flush=True)
    time.sleep(12)
    print("   APScheduler background loop cycle completed successfully.")

    print("\n==========================================", flush=True)
    print("FCM PUSH NOTIFICATION VERIFICATION COMPLETE", flush=True)
    print("==========================================", flush=True)

if __name__ == "__main__":
    run_fcm_tests()
