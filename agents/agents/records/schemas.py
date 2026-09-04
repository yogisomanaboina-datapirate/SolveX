from typing import Any, Dict, List, Optional
from pydantic import AliasChoices, BaseModel, Field
from core.schemas import BaseDecisionResponse, WorkflowStepLog


class ReportValueObservation(BaseModel):
    """Extracted parameter, test value, and clinical observation."""
    parameter: str = Field(description="Parameter or test name e.g. Hemoglobin, WBC, Glucose", examples=["Hemoglobin"])
    value: str = Field(description="Measured parameter value with units", examples=["11.2 g/dL"])
    reference_range: Optional[str] = Field(default=None, description="Normal reference range if stated in report", examples=["13.5 - 17.5 g/dL"])
    observation: str = Field(description="Clinical observation e.g. Normal, Mildly Low, Elevated", examples=["Mildly below reference range"])


class ReportAnalyzerRequest(BaseModel):
    """Medical report analysis request payload received from Backend/User."""
    report_text: str = Field(
        description="Raw text content of medical report or lab findings",
        examples=["CBC Report: Hemoglobin 11.2 g/dL, WBC 11,500 /mcL, Platelets 210,000 /mcL. Impression: Mild anemia and mild leukocytosis."]
    )
    report_title: Optional[str] = Field(default=None, description="Report title or document category e.g. Complete Blood Count")
    patient_age: Optional[int] = Field(default=None, description="Patient age in years")
    patient_gender: Optional[str] = Field(default=None, description="Patient gender")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Backend file/document metadata")


class ReportAnalyzerResponse(BaseDecisionResponse):
    """Structured Medical Report Analysis AI Decision Output."""
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
