from typing import Any, Dict, List
from core.featherless import featherless_client
from core.logging import logger, log_workflow_event
from agents.ambulance.schemas import HospitalSelection, TriageResponse

HOSPITAL_SELECTION_SYSTEM_PROMPT = """You are LifeLink AI Hospital Matching Agent.
Your task is to review the evaluated hospital options and select the single best facility for an incoming emergency patient.

Explain concisely in 2-3 sentences why the chosen hospital is preferred based on:
1. Specialty match (e.g., Cardiology, Neurology, Trauma)
2. Immediate ICU/ER bed availability
3. Distance and travel ETA

Format response as clear reasoning text.
"""


class HospitalMatchingAgent:
    """
    AI Agent responsible for evaluating candidate hospitals and selecting the optimal facility.
    """

    def select_best_hospital(
        self,
        evaluated_hospitals: List[Dict[str, Any]],
        triage: TriageResponse
    ) -> HospitalSelection:
        """
        Evaluate candidate hospitals and produce structured HospitalSelection recommendation.
        """
        if not evaluated_hospitals:
            raise ValueError("No candidate hospitals provided for evaluation.")

        top_candidate = evaluated_hospitals[0]

        reasoning = (
            f"Selected {top_candidate['hospital_name']} because it supports required {triage.required_specialty} specialty, "
            f"has {top_candidate['icu_beds_available']} ICU beds and {top_candidate['er_beds_available']} ER beds available, "
            f"and is closest at {top_candidate['distance_km']} km (Estimated ETA: {top_candidate['estimated_eta_minutes']} mins)."
        )

        if featherless_client.is_available:
            try:
                candidates_summary = "\n".join([
                    f"- {h['hospital_name']}: {h['distance_km']} km (ETA {h['estimated_eta_minutes']}m), "
                    f"ICU Beds: {h['icu_beds_available']}, ER Beds: {h['er_beds_available']}, Score: {h['suitability_score']}"
                    for h in evaluated_hospitals[:3]
                ])

                prompt = (
                    f"Emergency Context: {triage.category} ({triage.urgency} urgency), Required Specialty: {triage.required_specialty}\n"
                    f"Candidate Hospitals:\n{candidates_summary}\n\n"
                    f"Top Hospital Selected: {top_candidate['hospital_name']}\n"
                    "Explain why this hospital is optimal."
                )

                ai_reasoning = featherless_client.generate_completion(
                    prompt=prompt,
                    system_prompt=HOSPITAL_SELECTION_SYSTEM_PROMPT,
                    temperature=0.2,
                    max_tokens=150
                )
                if ai_reasoning and "[MOCK AI RESPONSE]" not in ai_reasoning:
                    reasoning = ai_reasoning.strip()

            except Exception as e:
                logger.warning(f"Featherless hospital reasoning call failed, using rule-based reasoning: {e}")

        log_workflow_event(
            workflow_name="Emergency Hospital Matching",
            step_number=3,
            step_name="Selected Best Hospital",
            details={
                "selected_hospital": top_candidate["hospital_name"],
                "distance_km": top_candidate["distance_km"],
                "eta_minutes": top_candidate["estimated_eta_minutes"]
            }
        )

        return HospitalSelection(
            hospital_id=top_candidate["hospital_id"],
            hospital_name=top_candidate["hospital_name"],
            distance_km=top_candidate["distance_km"],
            estimated_eta_minutes=top_candidate["estimated_eta_minutes"],
            icu_beds_available=top_candidate["icu_beds_available"],
            er_beds_available=top_candidate["er_beds_available"],
            suitability_score=top_candidate["suitability_score"],
            suitability_reason=reasoning
        )


hospital_matching_agent = HospitalMatchingAgent()
