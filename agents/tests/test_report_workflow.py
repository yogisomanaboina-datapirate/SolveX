import pytest
from fastapi.testclient import TestClient
from main import app
from core.errors import InvalidInputException
from agents.records.schemas import HistoricalReportInput, ReportAnalyzerRequest
from workflows.records import run_report_analyzer_workflow

client = TestClient(app)


# TEST 1: Single Report Behavior (no fake trends or chart datasets)
def test_single_medical_report():
    request = ReportAnalyzerRequest(
        report_text="Complete Blood Count: Hemoglobin 14.5 g/dL, WBC 6,500 /mcL, Platelets 250,000 /mcL. All parameters within normal limits.",
        report_title="CBC Annual Health Checkup",
        report_date="2026-08-10"
    )
    response = run_report_analyzer_workflow(request)

    assert response.report_type == "LABORATORY_BLOOD_TEST"
    assert response.summary != ""
    assert len(response.key_findings) >= 1
    assert len(response.important_values) >= 1
    assert response.health_trends == []  # No fake trends for single report
    assert response.parameters_for_visualization == []  # No fake chart data for single report
    assert "disclaimer" in response.model_dump()
    assert response.report_metadata.reports_analyzed_count == 1
    assert response.report_metadata.historical_comparison_performed is False
    assert len(response.workflow_steps) == 8


# TEST 2: Multiple Reports with Hemoglobin Values (12.1 -> 11.8 -> 13.0)
def test_multiple_reports_hemoglobin_trend():
    request = ReportAnalyzerRequest(
        report_text="CBC Report: Hemoglobin 13.0 g/dL, WBC 7,100 /mcL, Platelets 240,000 /mcL.",
        report_title="Latest CBC Test",
        report_date="2026-08-10",
        previous_reports=[
            HistoricalReportInput(
                report_text="CBC Lab: Hemoglobin 12.1 g/dL, WBC 6,800 /mcL.",
                report_title="Baseline CBC",
                report_date="2026-01-10"
            ),
            HistoricalReportInput(
                report_text="Mid-Year Check: Hemoglobin 11.8 g/dL, WBC 7,000 /mcL.",
                report_title="Follow-up CBC",
                report_date="2026-04-10"
            )
        ]
    )
    response = run_report_analyzer_workflow(request)

    assert response.report_metadata.reports_analyzed_count == 3
    assert response.report_metadata.historical_comparison_performed is True
    assert len(response.health_trends) >= 1

    # Find Hemoglobin trend
    hb_trend = next((t for t in response.health_trends if t.parameter == "Hemoglobin"), None)
    assert hb_trend is not None
    assert len(hb_trend.historical_measurements) == 3
    assert hb_trend.historical_measurements[0].date == "2026-01-10"
    assert hb_trend.historical_measurements[0].value == 12.1
    assert hb_trend.historical_measurements[1].date == "2026-04-10"
    assert hb_trend.historical_measurements[1].value == 11.8
    assert hb_trend.historical_measurements[2].date == "2026-08-10"
    assert hb_trend.historical_measurements[2].value == 13.0
    assert "13.0" in hb_trend.latest_value and "g/d" in hb_trend.latest_value.lower()
    assert hb_trend.latest_date == "2026-08-10"
    assert len(response.parameters_for_visualization) >= 1


# TEST 3: Multiple Reports Containing Different Parameters (Hemoglobin, Glucose, Creatinine)
def test_multiple_reports_different_parameters():
    request = ReportAnalyzerRequest(
        report_text="Metabolic Panel: Fasting Glucose 110 mg/dL, Serum Creatinine 1.1 mg/dL, Hemoglobin 13.5 g/dL.",
        report_title="Current Comprehensive Panel",
        report_date="2026-08-10",
        previous_reports=[
            HistoricalReportInput(
                report_text="Past Lab: Fasting Glucose 95 mg/dL, Serum Creatinine 0.9 mg/dL, Hemoglobin 12.8 g/dL.",
                report_title="Previous Metabolic Panel",
                report_date="2026-02-15"
            )
        ]
    )
    response = run_report_analyzer_workflow(request)

    assert len(response.parameters_for_visualization) >= 3
    param_names = [chart.parameter for chart in response.parameters_for_visualization]
    assert "Hemoglobin" in param_names
    assert "Fasting Glucose" in param_names
    assert "Serum Creatinine" in param_names


# TEST 4: Parameter Exists in Only One Report (Not Presented as Historical Trend)
def test_single_instance_parameter_not_trended():
    request = ReportAnalyzerRequest(
        report_text="Lab Panel: Hemoglobin 13.0 g/dL, Fasting Glucose 105 mg/dL.",
        report_title="Current Lab Report",
        report_date="2026-08-10",
        previous_reports=[
            HistoricalReportInput(
                report_text="Previous CBC: Hemoglobin 12.0 g/dL.",
                report_title="Previous CBC Only",
                report_date="2026-03-01"
            )
        ]
    )
    response = run_report_analyzer_workflow(request)

    # Hemoglobin appears in both reports -> trended
    # Fasting Glucose appears in only ONE report -> NOT in trends
    trend_params = [t.parameter for t in response.health_trends]
    assert "Hemoglobin" in trend_params
    assert "Fasting Glucose" not in trend_params


# TEST 5: Missing or Unclear Information Handling
def test_missing_unclear_report_information():
    request = ReportAnalyzerRequest(
        report_text="Abdominal USG: Liver size normal. Note: Pancreas partially obscured by gas. Date of prior scan missing.",
        report_title="Abdominal Ultrasound"
    )
    response = run_report_analyzer_workflow(request)

    assert response.report_type == "RADIOLOGY_IMAGING"
    assert response.summary != ""
    assert "disclaimer" in response.model_dump()


# TEST 6: Medication Information Summary Safety Check (No invented dosages/prescriptions)
def test_report_medication_info_safety_check():
    request = ReportAnalyzerRequest(
        report_text="Hospital Discharge Summary: Patient treated for acute bronchitis. Discharged on Inhaler Salbutamol 100mcg as needed.",
        report_title="Hospital Discharge Summary"
    )
    response = run_report_analyzer_workflow(request)

    assert response.report_type in ["DISCHARGE_SUMMARY", "PRESCRIPTION_REPORT"]
    assert "disclaimer" in response.model_dump()
    assert "not a medical diagnosis or prescription" in response.disclaimer.lower() or "always consult a qualified physician" in response.disclaimer.lower()


# TEST 7: Featherless AI Client Integration Verification
def test_featherless_integration_verification():
    request = ReportAnalyzerRequest(
        report_text="CBC Lab: Hemoglobin 12.5 g/dL, WBC 8,000 /mcL.",
        report_title="Routine CBC Test"
    )
    response = run_report_analyzer_workflow(request)

    assert response.summary != ""
    assert response.confidence >= 0.8
    assert response.report_metadata.reports_analyzed_count == 1


# TEST 8: Invalid or Empty Input Validation
def test_invalid_empty_report_input():
    with pytest.raises(InvalidInputException):
        run_report_analyzer_workflow(ReportAnalyzerRequest(report_text="   "))


# TEST 9: HTTP Endpoint Integration
def test_report_analyzer_endpoint_http():
    payload = {
        "report_text": "CBC Report: Hemoglobin 13.5 g/dL, WBC 7,200 /mcL, Fasting Glucose 98 mg/dL.",
        "report_title": "Annual Blood Panel",
        "report_date": "2026-08-10",
        "patient_age": 35,
        "previous_reports": [
            {
                "report_text": "CBC Report: Hemoglobin 12.2 g/dL, WBC 6,900 /mcL, Fasting Glucose 92 mg/dL.",
                "report_title": "Prior Blood Panel",
                "report_date": "2026-02-10"
            }
        ]
    }
    response = client.post("/agent/report-analyzer", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["report_type"] == "LABORATORY_BLOOD_TEST"
    assert "summary" in data
    assert "important_values" in data
    assert "health_trends" in data
    assert "parameters_for_visualization" in data
    assert "items_requiring_professional_review" in data
    assert "disclaimer" in data
    assert len(data["workflow_steps"]) == 8
