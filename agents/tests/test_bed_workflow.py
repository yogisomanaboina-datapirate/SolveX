from fastapi.testclient import TestClient
from main import app
from tools.bed_tools import evaluate_and_rank_bed_allocations
from agents.beds.schemas import BedInventory, BedOptimizationRequest
from workflows.beds import run_bed_optimizer_workflow

client = TestClient(app)


def test_bed_ranking_tool_availability_and_specialty():
    inventories = [
        BedInventory(
            hospital_id="HOSP-A",
            hospital_name="Hospital A",
            icu_beds_total=10,
            icu_beds_occupied=9,  # 1 available
            specialties=["CARDIOLOGY"]
        ),
        BedInventory(
            hospital_id="HOSP-B",
            hospital_name="Hospital B",
            icu_beds_total=10,
            icu_beds_occupied=4,  # 6 available
            specialties=["CARDIOLOGY"]
        )
    ]

    ranked = evaluate_and_rank_bed_allocations(
        inventories=inventories,
        required_bed_type="ICU",
        required_specialty="CARDIOLOGY",
        patient_urgency="HIGH",
        surge_factor=1.0
    )

    # Hospital B should be ranked #1 because it has 6 available ICU beds vs 1
    assert ranked[0].recommended_hospital_id == "HOSP-B"
    assert ranked[0].beds_available_before_allocation == 6


def test_predictive_surge_factor_impact():
    inventories = [
        BedInventory(
            hospital_id="HOSP-A",
            hospital_name="Hospital A",
            icu_beds_total=10,
            icu_beds_occupied=5,
            specialties=["CARDIOLOGY"]
        )
    ]

    # Baseline 1.0x surge
    baseline = evaluate_and_rank_bed_allocations(inventories, "ICU", "CARDIOLOGY", "HIGH", 1.0)
    # Surged 1.5x demand (5 occupied * 1.5 = 8 occupied -> 9 post-allocation)
    surged = evaluate_and_rank_bed_allocations(inventories, "ICU", "CARDIOLOGY", "HIGH", 1.5)

    assert surged[0].projected_occupancy_after_allocation_pct > baseline[0].projected_occupancy_after_allocation_pct


def test_bed_optimizer_workflow_execution():
    request = BedOptimizationRequest(
        required_bed_type="ICU",
        required_specialty="CARDIOLOGY",
        patient_urgency="CRITICAL",
        expected_surge_factor=1.1
    )
    response = run_bed_optimizer_workflow(request)

    assert response.recommended_allocation.recommended_hospital_name != ""
    assert response.recommended_allocation.allocated_bed_type == "ICU"
    assert response.recommended_action == "RESERVE_BED_IN_BACKEND"
    assert len(response.workflow_steps) >= 3


def test_bed_optimizer_endpoint_http():
    payload = {
        "required_bed_type": "ICU",
        "required_specialty": "NEUROLOGY",
        "patient_urgency": "HIGH",
        "expected_surge_factor": 1.4
    }
    response = client.post("/agent/bed-optimizer", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "recommended_allocation" in data
    assert data["recommended_allocation"]["allocated_bed_type"] == "ICU"
    assert "surge_warning" in data
    assert len(data["workflow_steps"]) >= 3
