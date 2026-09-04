import re
from typing import Any, Dict, List, Optional
from core.errors import InvalidInputException
from agents.records.schemas import ReportValueObservation


def sanitize_and_validate_report_input(report_text: str) -> str:
    """
    Validate report input text is non-empty and contains readable medical content.
    """
    if not report_text or not report_text.strip():
        raise InvalidInputException("Report text is empty or invalid. Please provide report text for analysis.")
    return report_text.strip()


def classify_report_type(report_text: str, report_title: Optional[str] = None) -> str:
    """
    Classify medical report category based on text content and title.
    """
    combined = f"{report_title or ''} {report_text}".lower()

    if any(w in combined for w in ["cbc", "blood count", "hemoglobin", "wbc", "platelets", "glucose", "cholesterol", "lipid", "creatinine", "lab"]):
        return "LABORATORY_BLOOD_TEST"
    elif any(w in combined for w in ["x-ray", "mri", "ct scan", "ultrasound", "radiology", "imaging", "echo"]):
        return "RADIOLOGY_IMAGING"
    elif any(w in combined for w in ["discharge", "summary", "hospital course", "admission note"]):
        return "DISCHARGE_SUMMARY"
    elif any(w in combined for w in ["prescription", "medication list", "rx", "dosage"]):
        return "PRESCRIPTION_REPORT"
    else:
        return "GENERAL_MEDICAL_REPORT"


def extract_basic_report_values(report_text: str) -> List[ReportValueObservation]:
    """
    Deterministic Tool: Extract key measurable parameters and test values from report text using pattern parsing.
    """
    values: List[ReportValueObservation] = []

    # Common Regex Patterns for Lab Values
    patterns = [
        (r"hemoglobin[:\s]+([\d\.]+\s*(?:g/dl|g/L)?)", "Hemoglobin", "12.0 - 16.0 g/dL"),
        (r"wbc[:\s]+([\d,]+\s*(?:/mcl|/uL|/\w+)?)", "WBC (White Blood Cells)", "4,500 - 11,000 /mcL"),
        (r"platelets[:\s]+([\d,]+\s*(?:/mcl|/uL|/\w+)?)", "Platelets", "150,000 - 450,000 /mcL"),
        (r"glucose[:\s]+([\d\.]+\s*(?:mg/dl)?)", "Fasting Glucose", "70 - 99 mg/dL"),
        (r"creatinine[:\s]+([\d\.]+\s*(?:mg/dl)?)", "Serum Creatinine", "0.6 - 1.2 mg/dL"),
        (r"spo2[:\s]+([\d\%]+)", "SpO2 Oxygen Saturation", "95 - 100%"),
        (r"blood pressure[:\s]+([\d\/]+\s*mmhg?)", "Blood Pressure", "120/80 mmHg"),
        (r"heart rate[:\s]+([\d]+\s*bpm?)", "Heart Rate", "60 - 100 bpm"),
    ]

    text_lower = report_text.lower()

    for pattern, param_name, ref_range in patterns:
        match = re.search(pattern, text_lower)
        if match:
            val_str = match.group(1).strip()
            obs = "Extracted test value"
            if "high" in text_lower or "elevated" in text_lower:
                obs = "Elevated value noted in report"
            elif "low" in text_lower or "anemia" in text_lower:
                obs = "Low value noted in report"
            elif "normal" in text_lower:
                obs = "Within reported reference range"

            values.append(
                ReportValueObservation(
                    parameter=param_name,
                    value=val_str,
                    reference_range=ref_range,
                    observation=obs
                )
            )

    return values
