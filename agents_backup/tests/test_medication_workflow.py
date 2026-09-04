from fastapi.testclient import TestClient
from main import app
from tools.medication_tools import detect_medication_schedule_conflicts, generate_deterministic_reminder_times
from agents.medication.schemas import MedicationItem, MedicationScheduleRequest, ScheduledReminder
from workflows.medication import run_scheduler_workflow

client = TestClient(app)


def test_deterministic_reminder_generation_twice_daily():
    med = MedicationItem(
        medication_name="Amoxicillin",
        prescribed_dosage="500mg",
        prescribed_frequency="Twice daily",
        meal_relationship="AFTER_MEAL"
    )
    reminders = generate_deterministic_reminder_times(
        medication=med,
        wake_time_str="08:00",
        sleep_time_str="22:00"
    )

    assert len(reminders) == 2
    assert reminders[0].medication_name == "Amoxicillin"
    assert reminders[0].scheduled_time == "09:00"  # 30 mins after 08:30 breakfast
    assert reminders[1].scheduled_time == "20:30"  # 30 mins after 20:00 dinner


def test_medication_conflict_detection():
    rems = [
        ScheduledReminder(
            reminder_id="REM-1",
            medication_name="Aspirin",
            dosage="100mg",
            scheduled_time="09:00",
            meal_relation_note="After breakfast",
            instructions="Take Aspirin"
        ),
        ScheduledReminder(
            reminder_id="REM-2",
            medication_name="Ibuprofen",
            dosage="400mg",
            scheduled_time="09:05",  # Only 5 mins after Aspirin!
            meal_relation_note="After breakfast",
            instructions="Take Ibuprofen"
        )
    ]

    conflicts = detect_medication_schedule_conflicts(
        scheduled_reminders=rems,
        wake_time_str="08:00",
        sleep_time_str="22:00"
    )

    assert len(conflicts) >= 1
    assert conflicts[0].conflict_type == "CLOSE_TIMING"
    assert "Aspirin" in conflicts[0].description
    assert "Ibuprofen" in conflicts[0].description


def test_medication_scheduler_workflow_execution():
    request = MedicationScheduleRequest(
        medications=[
            MedicationItem(
                medication_name="Metformin",
                prescribed_dosage="500mg",
                prescribed_frequency="Twice daily",
                meal_relationship="AFTER_MEAL"
            )
        ],
        user_wake_time="07:30",
        user_sleep_time="22:30"
    )
    response = run_scheduler_workflow(request)

    assert len(response.scheduled_reminders) == 2
    assert response.scheduled_reminders[0].medication_name == "Metformin"
    assert len(response.notification_payloads) == 2
    assert "disclaimer" in response.model_dump()
    assert "not prescribe" in response.disclaimer.lower()


def test_scheduler_endpoint_http():
    payload = {
        "medications": [
            {
                "medication_name": "Atorvastatin",
                "prescribed_dosage": "10mg",
                "prescribed_frequency": "Once daily",
                "meal_relationship": "AFTER_MEAL"
            }
        ],
        "user_wake_time": "08:00",
        "user_sleep_time": "22:00"
    }
    response = client.post("/agent/scheduler", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert len(data["scheduled_reminders"]) == 1
    assert data["scheduled_reminders"][0]["medication_name"] == "Atorvastatin"
    assert len(data["notification_payloads"]) == 1
    assert len(data["workflow_steps"]) >= 4
