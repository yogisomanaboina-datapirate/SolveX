from fastapi.testclient import TestClient
from main import app
from tools.insurance_tools import calculate_coverage_estimate, inspect_and_match_claims
from agents.insurance.schemas import (
    ClaimAnalysisRequest,
    ExistingClaimData,
    PolicyInfo,
)
from workflows.insurance import run_claims_workflow

client = TestClient(app)


def test_claim_matching_tool_existing_claim():
    existing_claims = [
        ExistingClaimData(
            claim_id="CLM-4401",
            policy_id="POL-99281",
            hospital_name="Apollo Emergency Hospital Jubilee Hills",
            treatment_type="CARDIAC_EMERGENCY",
            claim_amount_inr=150000.0,
            status="UNDER_REVIEW",
            submission_date="2026-09-02"
        )
    ]
    policy = PolicyInfo(policy_id="POL-99281", provider_name="Star Health")

    res = inspect_and_match_claims(
        user_request="Has claim CLM-4401 been processed for Apollo Hospital?",
        policy_info=policy,
        existing_claims=existing_claims
    )

    assert res.claim_exists is True
    assert res.matched_claim_id == "CLM-4401"
    assert res.matched_claim_status == "UNDER_REVIEW"


def test_claim_matching_tool_no_hallucination():
    """
    CRITICAL SAFETY TEST: Verify that when backend has no existing claims,
    the tool strictly returns claim_exists=False (no AI hallucination).
    """
    policy = PolicyInfo(policy_id="POL-99281", provider_name="Star Health")

    res = inspect_and_match_claims(
        user_request="Check status of my claim for heart treatment",
        policy_info=policy,
        existing_claims=[]  # Empty list from backend database
    )

    assert res.claim_exists is False
    assert res.matched_claim_id is None


def test_coverage_estimation_calculation():
    policy = PolicyInfo(
        policy_id="POL-99281",
        provider_name="Star Health",
        coverage_limit_inr=500000.0,
        copay_percentage=10.0,
        network_hospitals=["Apollo Emergency Hospital Jubilee Hills"]
    )

    calc = calculate_coverage_estimate(
        policy_info=policy,
        estimated_bill_inr=100000.0,
        hospital_name="Apollo Emergency Hospital Jubilee Hills"
    )

    assert calc["is_network_cashless_hospital"] is True
    assert calc["estimated_patient_copay_inr"] == 10000.0
    assert calc["estimated_insurer_payable_inr"] == 90000.0


def test_insurance_claims_workflow_execution():
    request = ClaimAnalysisRequest(
        user_request="What is the status of my claim CLM-4401 under policy POL-99281 at Apollo Hospital?",
        policy_info=PolicyInfo(policy_id="POL-99281", provider_name="Star Health"),
        existing_claims=[
            ExistingClaimData(
                claim_id="CLM-4401",
                policy_id="POL-99281",
                hospital_name="Apollo Hospital",
                treatment_type="CARDIAC_EMERGENCY",
                claim_amount_inr=120000.0,
                status="APPROVED",
                submission_date="2026-09-01",
                approved_amount_inr=108000.0
            )
        ]
    )
    res = run_claims_workflow(request)

    assert res.claim_exists is True
    assert res.matched_claim_id == "CLM-4401"
    assert res.matched_claim_status == "APPROVED"
    assert res.assistance_type == "EXISTING_CLAIM_STATUS"
    assert "disclaimer" in res.model_dump()


def test_claims_endpoint_http():
    payload = {
        "user_request": "How do I file a pre-authorization for emergency admission under policy POL-99281?",
        "policy_info": {
            "policy_id": "POL-99281",
            "provider_name": "Star Health Insurance",
            "coverage_limit_inr": 500000.0,
            "copay_percentage": 10.0,
            "network_hospitals": ["Apollo Emergency Hospital Jubilee Hills"],
            "pre_authorization_required": True
        },
        "existing_claims": []
    }
    response = client.post("/agent/claims", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["claim_exists"] is False
    assert data["assistance_type"] in ["PRE_AUTH_ASSISTANCE", "NEW_CLAIM_FILING_GUIDANCE"]
    assert "recommended_next_step" in data
    assert len(data["workflow_steps"]) >= 3
