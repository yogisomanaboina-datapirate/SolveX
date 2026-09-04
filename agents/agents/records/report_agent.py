from datetime import datetime, timezone
from typing import List, Optional
from core.featherless import featherless_client
from core.logging import logger, log_workflow_event
from core.schemas import WorkflowStepLog
from tools.report_tools import (
    classify_report_type,
    extract_basic_report_values,
    extract_historical_parameter_series,
    sanitize_and_validate_report_input,
)
from agents.records.schemas import (
    ReportAnalyzerRequest,
    ReportAnalyzerResponse,
    ReportMetadata,
)

REPORT_ANALYZER_SYSTEM_PROMPT = """You are LifeLink AI Medical Report Analyzer Agent.

YOUR MANDATE:
1. Analyze the supplied current medical report text, along with previous historical reports when provided by the Backend.
2. Extract lab parameters, test values, clinical observations, key findings, and items requiring professional physician review.
3. Compare historical values over time across reports to identify trends (e.g. increasing, decreasing, stable).
4. Output ONLY a valid JSON object matching these exact keys:
{
  "summary": "Clear, patient-friendly executive summary of current report and historical comparison",
  "report_type": "LABORATORY_BLOOD_TEST" | "RADIOLOGY_IMAGING" | "DISCHARGE_SUMMARY" | "PRESCRIPTION_REPORT" | "GENERAL_MEDICAL_REPORT",
  "key_findings": ["Finding 1", "Finding 2"],
  "important_values": [
    {
      "parameter": "Parameter Name",
      "value": "Measured Value",
      "reference_range": "Normal range if stated",
      "observation": "Clinical observation"
    }
  ],
  "observations": ["General observation 1"],
  "historical_comparison": ["Bullet point 1 comparing past vs current values"],
  "health_trends": [
    {
      "parameter": "Hemoglobin",
      "unit": "g/dL",
      "latest_value": "13.0 g/dL",
      "latest_date": "2026-08-10",
      "historical_measurements": [
        {"date": "2026-01-10", "value": 12.1, "unit": "g/dL", "observation": "Baseline"},
        {"date": "2026-04-10", "value": 11.8, "unit": "g/dL", "observation": "Slight dip"},
        {"date": "2026-08-10", "value": 13.0, "unit": "g/dL", "observation": "Improved"}
      ],
      "trend_direction": "increasing",
      "change_description": "Increased by 1.2 g/dL compared to previous measurement",
      "trend_explanation": "Hemoglobin level increased from 11.8 to 13.0 g/dL over the reported period."
    }
  ],
  "parameters_for_visualization": [
    {
      "parameter": "Hemoglobin",
      "unit": "g/dL",
      "measurements": [
        {"date": "2026-01-10", "value": 12.1},
        {"date": "2026-04-10", "value": 11.8},
        {"date": "2026-08-10", "value": 13.0}
      ],
      "trend": "increasing",
      "latest_value": 13.0
    }
  ],
  "items_requiring_professional_review": ["Item requiring doctor review 1"],
  "missing_or_unclear_information": ["Missing detail if any"],
  "recommended_next_action": "CONSULT_PHYSICIAN_FOR_CLINICAL_CORRELATION",
  "disclaimer": "LifeLink AI assists with medical report text understanding and structuring. This report analysis is not a medical diagnosis or prescription. Always consult a qualified physician for clinical evaluation.",
  "decision": "Brief decision summary of report analysis",
  "reasoning": "Detailed rationale explaining extracted findings and parameters",
  "next_action": "CONSULT_PHYSICIAN_FOR_CLINICAL_CORRELATION",
  "confidence": 0.95
}

SAFETY MANDATE:
- Do NOT diagnose medical conditions or diseases.
- Do NOT prescribe medications or dosage recommendations.
- Do NOT invent test values, missing report details, or dates.
- If only ONE report exists, do NOT generate fake historical trends or chart datasets.
- Always include the mandatory medical safety disclaimer.
"""


class MedicalReportAgent:
    """
    AI Agent responsible for analyzing medical report text, historical reports, and structuring health trends.
    """

    def analyze_report(self, request: ReportAnalyzerRequest) -> ReportAnalyzerResponse:
        """
        Process medical report input (single or multiple historical reports) and return structured analysis.
        """
        # Validate non-empty input
        valid_text = sanitize_and_validate_report_input(request.report_text)
        prev_reports = request.previous_reports or []

        logger.info("MedicalReportAgent analyzing report text and historical data...")
        log_workflow_event(
            workflow_name="Medical Report Analyzer",
            step_number=1,
            step_name="Report Input Received",
            details={"text_length": len(valid_text), "report_title": request.report_title}
        )

        steps: List[WorkflowStepLog] = []

        # STEP 1: Report Input Received
        steps.append(
            WorkflowStepLog(
                step_number=1,
                step_name="Report Input Received",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"report_title": request.report_title or "Unspecified Medical Report", "date": request.report_date}
            )
        )

        # STEP 2: Historical Reports/Data Received
        steps.append(
            WorkflowStepLog(
                step_number=2,
                step_name="Historical Reports Received" if prev_reports else "Single Report Mode Initialized",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"previous_reports_count": len(prev_reports)}
            )
        )

        # STEP 3: Report Information Structured
        detected_type = classify_report_type(valid_text, request.report_title)
        extracted_values = extract_basic_report_values(valid_text)

        steps.append(
            WorkflowStepLog(
                step_number=3,
                step_name="Report Information Structured",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"report_type": detected_type, "parameters_found": len(extracted_values)}
            )
        )

        # STEP 4: Important Parameters Identified
        param_names = [v.parameter for v in extracted_values]
        steps.append(
            WorkflowStepLog(
                step_number=4,
                step_name="Important Parameters Identified",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"parameters": param_names}
            )
        )

        # STEP 5: Historical Measurements Compared
        health_trends, chart_datasets, comparison_bullets = extract_historical_parameter_series(
            current_text=valid_text,
            current_title=request.report_title,
            current_date=request.report_date,
            previous_reports=prev_reports
        )

        steps.append(
            WorkflowStepLog(
                step_number=5,
                step_name="Historical Measurements Compared",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"trends_count": len(health_trends), "chart_datasets_count": len(chart_datasets)}
            )
        )

        # Base default fallback values
        summary = (
            f"Analyzed {detected_type.replace('_', ' ').title()} text containing {len(valid_text)} characters."
            if not prev_reports
            else f"Compared current report with {len(prev_reports)} historical report(s). Identified {len(health_trends)} parameter trend(s)."
        )
        key_findings = [f"Report text categorized as {detected_type}."]
        observations = ["Text parsed for clinical parameters."]
        items_review = ["All abnormal or flagged test parameters should be reviewed by an attending physician."]
        missing_info: List[str] = []
        decision = f"Medical report analysis finalized for {detected_type}."
        reasoning = f"Extracted {len(extracted_values)} parameter(s) and compared {len(prev_reports)} previous report(s)."
        next_action = "CONSULT_PHYSICIAN_FOR_CLINICAL_CORRELATION"
        confidence = 0.92
        disclaimer = "LifeLink AI assists with medical report text understanding and structuring. This report analysis is not a medical diagnosis or prescription. Always consult a qualified physician for clinical evaluation."

        # STEP 6: Featherless AI Analysis Performed
        if featherless_client.is_available:
            try:
                values_summary = "\n".join([
                    f"- {v.parameter}: {v.value} (Ref: {v.reference_range or 'N/A'}) - {v.observation}"
                    for v in extracted_values
                ]) if extracted_values else "No specific numerical test values parsed."

                prev_summary = ""
                if prev_reports:
                    prev_summary = "\nHistorical Reports Provided:\n" + "\n".join([
                        f"- [{p.report_date or 'Undated'}] {p.report_title or 'Report'}: {p.report_text[:200]}..."
                        for p in prev_reports
                    ])

                prompt = (
                    f"Report Title: {request.report_title or 'Unspecified'}\n"
                    f"Report Date: {request.report_date or 'Not stated'}\n"
                    f"Report Category: {detected_type}\n"
                    f"Patient Age: {request.patient_age or 'Not stated'}, Gender: {request.patient_gender or 'Not stated'}\n"
                    f"Current Report Text Content:\n\"\"\"{valid_text}\"\"\"\n\n"
                    f"Parsed Baseline Values:\n{values_summary}\n"
                    f"{prev_summary}\n\n"
                    "Provide a structured, patient-friendly medical report analysis with historical comparisons and trends."
                )

                ai_res = featherless_client.generate_structured_json(
                    prompt=prompt,
                    system_prompt=REPORT_ANALYZER_SYSTEM_PROMPT,
                    response_model=ReportAnalyzerResponse
                )

                summary = ai_res.summary or summary
                detected_type = ai_res.report_type or detected_type
                key_findings = ai_res.key_findings or key_findings
                if ai_res.important_values:
                    extracted_values = ai_res.important_values
                observations = ai_res.observations or observations
                if ai_res.historical_comparison and prev_reports:
                    comparison_bullets = ai_res.historical_comparison

                # Prioritize complete deterministically extracted series across reports if available; otherwise use AI trends
                if prev_reports and health_trends:
                    pass
                elif ai_res.health_trends and prev_reports:
                    health_trends = ai_res.health_trends

                if prev_reports and chart_datasets:
                    pass
                elif ai_res.parameters_for_visualization and prev_reports:
                    chart_datasets = ai_res.parameters_for_visualization

                items_review = ai_res.items_requiring_professional_review or items_review
                missing_info = ai_res.missing_or_unclear_information or missing_info
                decision = ai_res.decision or decision
                reasoning = ai_res.reasoning or reasoning
                next_action = ai_res.recommended_next_action or next_action
                confidence = ai_res.confidence or confidence
                disclaimer = ai_res.disclaimer or disclaimer

                steps.append(
                    WorkflowStepLog(
                        step_number=6,
                        step_name="Featherless AI Analysis Performed",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="completed",
                        details={"model": featherless_client.model, "report_type": detected_type}
                    )
                )

            except Exception as e:
                logger.warning(f"Featherless AI report analyzer call failed, using rule-based reasoning: {e}")
                steps.append(
                    WorkflowStepLog(
                        step_number=6,
                        step_name="Completed Rule-Based Report Analysis",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="completed",
                        details={"rule_based": True}
                    )
                )
        else:
            steps.append(
                WorkflowStepLog(
                    step_number=6,
                    step_name="Completed Rule-Based Report Analysis",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="completed",
                    details={"rule_based": True}
                )
            )

        # STEP 7: Trend Data Validated
        # Single report safety check: Clear trends/charts if only 1 report exists
        if not prev_reports:
            health_trends = []
            chart_datasets = []
            comparison_bullets = ["Single report analysis. Historical trends require multiple reports."]

        steps.append(
            WorkflowStepLog(
                step_number=7,
                step_name="Trend Data Validated",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"single_report_safety_enforced": len(prev_reports) == 0}
            )
        )

        # STEP 8: Structured Health Report Finalized
        steps.append(
            WorkflowStepLog(
                step_number=8,
                step_name="Structured Health Report Finalized",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"total_workflow_steps": 8}
            )
        )

        log_workflow_event("Medical Report Analyzer", 8, "Structured Health Report Finalized")

        report_meta = ReportMetadata(
            current_report_date=request.report_date,
            reports_analyzed_count=1 + len(prev_reports),
            historical_comparison_performed=len(prev_reports) > 0
        )

        return ReportAnalyzerResponse(
            report_metadata=report_meta,
            decision=decision,
            reasoning=reasoning,
            confidence=confidence,
            next_action=next_action,
            summary=summary,
            report_type=detected_type,
            key_findings=key_findings,
            important_values=extracted_values,
            observations=observations,
            historical_comparison=comparison_bullets,
            health_trends=health_trends,
            parameters_for_visualization=chart_datasets,
            items_requiring_professional_review=items_review,
            missing_or_unclear_information=missing_info,
            recommended_next_action=next_action,
            disclaimer=disclaimer,
            data_used=[
                {"report_type": detected_type},
                {"reports_count": 1 + len(prev_reports)},
                {"extracted_values_count": len(extracted_values)}
            ],
            workflow_steps=steps
        )


medical_report_agent = MedicalReportAgent()
