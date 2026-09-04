import pytest
from fastapi.testclient import TestClient
from main import app
from core.errors import InvalidInputException
from agents.records.schemas import ReportAnalyzerRequest
from workflows.records import run_report_analyzer_workflow

client = TestClient(app)


def test_normal_medical_report():
    request = ReportAnalyzerRequest(
        report_text="Complete Blood Count: Hemoglobin 14.5 g/dL, WBC 6,500 /mcL, Platelets 250,000 /mcL. All parameters within normal limits.",
        report_title="CBC Annual Health Checkup"
    )
    response = run_report_analyzer_workflow(request)

    assert response.report_type == "LABORATORY_BLOOD_TEST"
    assert response.summary != ""
    assert len(response.key_findings) >= 1
    assert "disclaimer" in response.model_dump()
    assert len(response.workflow_steps) == 5


def test_report_with_measurable_values():
    request = ReportAnalyzerRequest(
        report_text="Lipid Profile Report: Fasting Glucose 110 mg/dL, Total Cholesterol 220 mg/dL, HDL 45 mg/dL, LDL 145 mg/dL, Blood Pressure 135/85 mmHg.",
        report_title="Lipid & Metabolic Panel"
    )
    response = run_report_analyzer_workflow(request)

    assert response.summary != ""
    assert len(response.important_values) >= 1
    assert response.important_values[0].parameter != ""
    assert response.important_values[0].value != ""


def test_incomplete_medical_report():
    request = ReportAnalyzerRequest(
        report_text="Abdominal Ultrasound: Liver normal size, gallbladder clear. Note: Patient was non-fasting, pancreas partially obscured by bowel gas.",
        report_title="Abdominal USG"
    )
    response = run_report_analyzer_workflow(request)

    assert response.report_type == "RADIOLOGY_IMAGING"
    assert response.summary != ""
    assert "disclaimer" in response.model_dump()


def test_empty_invalid_report_input():
    with pytest.raises(InvalidInputException):
        run_report_analyzer_workflow(ReportAnalyzerRequest(report_text="   "))


def test_report_with_medication_info_safety_check():
    """
    Safety constraint: Report contains listed medications.
    Analyzer summarizes explicit text without prescribing or inventing dosages.
    """
    request = ReportAnalyzerRequest(
        report_text="Discharge Summary: Patient admitted for acute asthma exacerbation. Discharged on Inhaler Salbutamol 100mcg as needed and Tab Prednisolone 20mg daily for 5 days.",
        report_title="Hospital Discharge Summary"
    )
    response = run_report_analyzer_workflow(request)

    assert response.report_type in ["DISCHARGE_SUMMARY", "PRESCRIPTION_REPORT"]
    assert "prescribe" not in response.summary.lower() or "not prescribe" in response.disclaimer.lower()
    assert "disclaimer" in response.model_dump()
    assert "always consult a qualified physician" in response.disclaimer.lower()


def test_report_analyzer_endpoint_http():
    payload = {
        "report_text": "CBC Report: Hemoglobin 10.8 g/dL (Low), WBC 12,200 /mcL (Elevated), Platelets 210,000 /mcL.",
        "report_title": "Routine Blood Test",
        "patient_age": 42
    }
    response = client.post("/agent/report-analyzer", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["report_type"] == "LABORATORY_BLOOD_TEST"
    assert "summary" in data
    assert "important_values" in data
    assert "items_requiring_professional_review" in data
    assert "disclaimer" in data
    assert len(data["workflow_steps"]) == 5
