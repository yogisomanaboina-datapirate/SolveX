import re
from typing import Any, Dict, List, Optional, Tuple
from core.errors import InvalidInputException
from agents.records.schemas import (
    ChartReadyDataset,
    HistoricalMeasurement,
    HistoricalReportInput,
    ParameterTrend,
    ReportValueObservation,
)


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

    if any(w in combined for w in ["cbc", "blood count", "hemoglobin", "wbc", "platelets", "glucose", "hba1c", "creatinine", "lipid", "lab"]):
        return "LABORATORY_BLOOD_TEST"
    elif any(w in combined for w in ["x-ray", "mri", "ct scan", "ultrasound", "radiology", "imaging", "echo"]):
        return "RADIOLOGY_IMAGING"
    elif any(w in combined for w in ["discharge", "summary", "hospital course", "admission note"]):
        return "DISCHARGE_SUMMARY"
    elif any(w in combined for w in ["prescription", "medication list", "rx", "dosage"]):
        return "PRESCRIPTION_REPORT"
    else:
        return "GENERAL_MEDICAL_REPORT"


# Lab Parameter Parsing Configurations
PARAM_PATTERNS = [
    (r"(?:hemoglobin|hb)[:\s]+([\d\.]+)\s*(g/dl|g/l)?", "Hemoglobin", "g/dL", "12.0 - 16.0 g/dL"),
    (r"(?:fasting glucose|blood glucose|glucose)[:\s]+([\d\.]+)\s*(mg/dl)?", "Fasting Glucose", "mg/dL", "70 - 99 mg/dL"),
    (r"(?:hba1c|glycated hemoglobin)[:\s]+([\d\.]+)\s*(%)?", "HbA1c", "%", "< 5.7%"),
    (r"(?:serum creatinine|creatinine)[:\s]+([\d\.]+)\s*(mg/dl)?", "Serum Creatinine", "mg/dL", "0.6 - 1.2 mg/dL"),
    (r"(?:wbc|white blood cells)[:\s]+([\d,]+)\s*(/mcl|/ul)?", "WBC", "/mcL", "4,500 - 11,000 /mcL"),
    (r"(?:platelets)[:\s]+([\d,]+)\s*(/mcl|/ul)?", "Platelets", "/mcL", "150,000 - 450,000 /mcL"),
    (r"(?:egfr)[:\s]+([\d\.]+)\s*(ml/min)?", "eGFR", "mL/min/1.73m2", "> 90 mL/min/1.73m2"),
    (r"(?:bun|blood urea nitrogen|urea)[:\s]+([\d\.]+)\s*(mg/dl)?", "Urea / BUN", "mg/dL", "7 - 20 mg/dL"),
    (r"(?:spo2)[:\s]+([\d]+)\s*(%)?", "SpO2", "%", "95 - 100%"),
    (r"(?:blood pressure|bp)[:\s]+([\d\/]+)\s*(mmhg)?", "Blood Pressure", "mmHg", "120/80 mmHg"),
]


def extract_basic_report_values(report_text: str) -> List[ReportValueObservation]:
    """
    Deterministic Tool: Extract key measurable parameters and test values from report text using pattern parsing.
    """
    values: List[ReportValueObservation] = []
    text_lower = report_text.lower()

    for pattern, param_name, default_unit, ref_range in PARAM_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            val_num = match.group(1).strip()
            unit_matched = match.group(2) if len(match.groups()) >= 2 and match.group(2) else default_unit
            val_str = f"{val_num} {unit_matched}".strip()

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


def extract_numerical_value(val_str: str) -> Optional[float]:
    """Helper to convert string measurement e.g. '12.1' or '12.1 g/dL' to float."""
    try:
        clean = re.sub(r"[^\d\.]", "", str(val_str).split()[0])
        return float(clean) if clean else None
    except Exception:
        return None


def extract_historical_parameter_series(
    current_text: str,
    current_title: Optional[str],
    current_date: Optional[str],
    previous_reports: List[HistoricalReportInput]
) -> Tuple[List[ParameterTrend], List[ChartReadyDataset], List[str]]:
    """
    Extract historical measurements for parameters found across current and previous reports.
    Groups parameters, orders by date, calculates trends, and outputs chart-ready datasets.
    """
    all_reports: List[Dict[str, Any]] = []

    # 1. Previous reports
    for idx, prev in enumerate(previous_reports):
        p_date = prev.report_date or f"2026-01-0{idx+1}"
        all_reports.append({
            "text": prev.report_text,
            "title": prev.report_title or f"Previous Medical Report {idx+1}",
            "date": p_date,
            "is_current": False
        })

    # 2. Current report
    c_date = current_date or "2026-12-31"
    all_reports.append({
        "text": current_text,
        "title": current_title or "Current Medical Report",
        "date": c_date,
        "is_current": True
    })

    # Sort reports chronologically by date string
    def sort_key(rep: Dict[str, Any]) -> str:
        d = str(rep["date"])
        # Format YYYY-MM-DD if matching
        match = re.search(r"\d{4}-\d{2}-\d{2}", d)
        return match.group(0) if match else d

    all_reports.sort(key=sort_key)

    # Map parameters: param_name -> list of {"date": date, "value": num_val, "val_str": val_str, "unit": unit}
    param_map: Dict[str, List[Dict[str, Any]]] = {}

    for rep in all_reports:
        extracted = extract_basic_report_values(rep["text"])
        for obs in extracted:
            p_name = obs.parameter
            num_val = extract_numerical_value(obs.value)

            # Find matching unit if available
            unit = ""
            for _, p_key, p_unit, _ in PARAM_PATTERNS:
                if p_key == p_name:
                    unit = p_unit
                    break

            if p_name not in param_map:
                param_map[p_name] = []

            param_map[p_name].append({
                "date": rep["date"],
                "value": num_val if num_val is not None else obs.value,
                "val_str": obs.value,
                "unit": unit,
                "observation": obs.observation
            })

    health_trends: List[ParameterTrend] = []
    chart_datasets: List[ChartReadyDataset] = []
    comparison_bullets: List[str] = []

    # Process each parameter series
    for param_name, measurements in param_map.items():
        # Only process trends and graphs if at least 2 reports/measurements exist for this parameter
        if len(measurements) >= 2:
            unit = measurements[0]["unit"]
            hist_points: List[HistoricalMeasurement] = []
            chart_points: List[Dict[str, Any]] = []

            for m in measurements:
                hist_points.append(
                    HistoricalMeasurement(
                        date=str(m["date"]),
                        value=m["value"],
                        unit=unit,
                        observation=m.get("observation")
                    )
                )
                chart_points.append({
                    "date": str(m["date"]),
                    "value": m["value"]
                })

            # Calculate direction if numerical values exist
            num_values = [m["value"] for m in measurements if isinstance(m["value"], (int, float))]
            trend_dir = "stable"
            change_desc = None

            if len(num_values) >= 2:
                first_v = num_values[0]
                last_v = num_values[-1]
                diff = round(last_v - first_v, 2)

                if diff > 0.1:
                    trend_dir = "increasing"
                    change_desc = f"Increased by {abs(diff)} {unit}"
                elif diff < -0.1:
                    trend_dir = "decreasing"
                    change_desc = f"Decreased by {abs(diff)} {unit}"
                else:
                    trend_dir = "stable"
                    change_desc = f"Remained stable (change: {diff} {unit})"
            else:
                change_desc = "Historical measurements recorded"

            latest_val_str = measurements[-1]["val_str"]
            latest_dt_str = str(measurements[-1]["date"])

            values_arrow_str = " → ".join([str(m["value"]) for m in measurements])
            explanation = f"{param_name} trend: {values_arrow_str} ({trend_dir.capitalize()}). Latest: {latest_val_str} on {latest_dt_str}."

            health_trends.append(
                ParameterTrend(
                    parameter=param_name,
                    unit=unit,
                    latest_value=latest_val_str,
                    latest_date=latest_dt_str,
                    historical_measurements=hist_points,
                    trend_direction=trend_dir,
                    change_description=change_desc,
                    trend_explanation=explanation
                )
            )

            chart_datasets.append(
                ChartReadyDataset(
                    parameter=param_name,
                    unit=unit or "units",
                    measurements=chart_points,
                    trend=trend_dir,
                    latest_value=measurements[-1]["value"]
                )
            )

            comparison_bullets.append(
                f"{param_name}: Observed {trend_dir} trend across {len(measurements)} reports ({values_arrow_str})."
            )

    return health_trends, chart_datasets, comparison_bullets
