from typing import Any, Dict, List, Optional
from pydantic import AliasChoices, BaseModel, Field
from core.schemas import BaseDecisionResponse, WorkflowStepLog


class ReportValueObservation(BaseModel):
    """Extracted parameter, test value, and clinical observation."""
    parameter: str = Field(description="Parameter or test name e.g. Hemoglobin, WBC, Glucose", examples=["Hemoglobin"])
    value: str = Field(description="Measured parameter value with units", examples=["11.2 g/dL"])
    reference_range: Optional[str] = Field(default=None, description="Normal reference range if stated in report", examples=["13.5 - 17.5 g/dL"])
    observation: str = Field(default="Extracted test value", description="Clinical observation e.g. Normal, Mildly Low, Elevated", examples=["Mildly below reference range"])


class HistoricalReportInput(BaseModel):
    """Historical medical report payload supplied by Backend."""
    report_text: str = Field(description="Text content of previous medical report")
    report_title: Optional[str] = Field(default=None, description="Title or type of previous report")
    report_date: Optional[str] = Field(default=None, description="Report date e.g. 2026-01-15")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional document metadata")


class HistoricalMeasurement(BaseModel):
    """Single historical data point for a measurable health parameter."""
    date: str = Field(description="Date of measurement e.g. 2026-01-10", examples=["2026-01-10"])
    value: Any = Field(description="Numerical or string value e.g. 12.1 or '12.1 g/dL'", examples=[12.1])
    unit: Optional[str] = Field(default=None, description="Measurement unit e.g. g/dL, mg/dL", examples=["g/dL"])
    observation: Optional[str] = Field(default=None, description="Optional note e.g. Normal, Low")


class ParameterTrend(BaseModel):
    """Extracted trend across multiple reports for a single health parameter."""
    parameter: str = Field(description="Name of health parameter e.g. Hemoglobin", examples=["Hemoglobin"])
    unit: Optional[str] = Field(default=None, description="Measurement unit e.g. g/dL", examples=["g/dL"])
    latest_value: Optional[str] = Field(default=None, description="Latest recorded value with unit", examples=["13.0 g/dL"])
    latest_date: Optional[str] = Field(default=None, description="Date of latest measurement", examples=["2026-08-10"])
    historical_measurements: List[HistoricalMeasurement] = Field(default_factory=list, description="Chronologically sorted historical data points")
    trend_direction: str = Field(
        default="stable",
        description="Trend classification: increasing, decreasing, stable, fluctuating, single_measurement",
        examples=["increasing"]
    )
    change_description: Optional[str] = Field(default=None, description="Concise description of change from previous measurement")
    trend_explanation: str = Field(description="Clinical trend explanation phrase e.g. Hemoglobin levels increased from 11.8 to 13.0 g/dL.")


class ChartReadyDataset(BaseModel):
    """Structured data point formatted for React frontend line graph rendering."""
    parameter: str = Field(description="Parameter name for graph legend", examples=["Hemoglobin"])
    unit: str = Field(description="Y-axis unit e.g. g/dL", examples=["g/dL"])
    measurements: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of dicts: [{'date': '2026-01-10', 'value': 12.1}, ...]"
    )
    trend: str = Field(description="Trend type: increasing, decreasing, stable, fluctuating", examples=["increasing"])
    latest_value: Any = Field(description="Latest value recorded", examples=[13.0])


class ReportMetadata(BaseModel):
    """Metadata regarding current and historical report processing."""
    current_report_date: Optional[str] = Field(default=None, description="Date of current report being analyzed")
    reports_analyzed_count: int = Field(default=1, description="Total number of reports included in analysis")
    historical_comparison_performed: bool = Field(default=False, description="True if multiple reports were compared")


class ReportAnalyzerRequest(BaseModel):
    """Medical report analysis request payload received from Backend/User."""
    report_text: str = Field(
        description="Raw text content of medical report or lab findings",
        examples=["CBC Report: Hemoglobin 11.2 g/dL, WBC 11,500 /mcL, Platelets 210,000 /mcL. Impression: Mild anemia."]
    )
    report_title: Optional[str] = Field(default=None, description="Report title or document category e.g. Complete Blood Count")
    report_date: Optional[str] = Field(default=None, description="Date of current report e.g. 2026-08-10")
    patient_age: Optional[int] = Field(default=None, description="Patient age in years")
    patient_gender: Optional[str] = Field(default=None, description="Patient gender")
    previous_reports: List[HistoricalReportInput] = Field(
        default_factory=list,
        description="Optional list of historical reports provided by Backend"
    )
    historical_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional pre-structured historical patient lab data passed from Backend"
    )
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Backend file/document metadata")


class ReportAnalyzerResponse(BaseDecisionResponse):
    """Structured Medical Report Analysis AI Decision Output."""
    report_metadata: Optional[ReportMetadata] = Field(default=None, description="Metadata on reports analyzed")
    summary: str = Field(description="Clear, easy-to-understand executive summary of the report text")
    report_type: str = Field(
        description="Report category: LABORATORY_BLOOD_TEST, RADIOLOGY_IMAGING, DISCHARGE_SUMMARY, PRESCRIPTION_REPORT, GENERAL_MEDICAL_REPORT",
        examples=["LABORATORY_BLOOD_TEST"]
    )
    key_findings: List[str] = Field(default_factory=list, description="Key clinical findings extracted from report")
    important_values: List[ReportValueObservation] = Field(
        default_factory=list,
        description="Extracted measurable parameters and test values"
    )
    observations: List[str] = Field(default_factory=list, description="General observations")
    historical_comparison: List[str] = Field(
        default_factory=list,
        description="Bullet points comparing current report against past reports"
    )
    health_trends: List[ParameterTrend] = Field(
        default_factory=list,
        description="Extracted trends across historical reports"
    )
    parameters_for_visualization: List[ChartReadyDataset] = Field(
        default_factory=list,
        description="Structured data ready for React frontend line charts"
    )
    items_requiring_professional_review: List[str] = Field(
        default_factory=list,
        description="Values or findings requiring review by a physician"
    )
    missing_or_unclear_information: List[str] = Field(
        default_factory=list,
        description="Potentially missing or unclear information in report text"
    )
    recommended_next_action: str = Field(
        default="CONSULT_PHYSICIAN_FOR_CLINICAL_CORRELATION",
        description="Actionable next step for user"
    )
    disclaimer: str = Field(
        default="LifeLink AI assists with medical report text understanding and structuring. This report analysis is not a medical diagnosis or prescription. Always consult a qualified physician for clinical evaluation.",
        description="Mandatory medical safety disclaimer"
    )
