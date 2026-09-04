from datetime import datetime, timezone
from core.featherless import featherless_client
from core.logging import logger, log_workflow_event
from core.schemas import WorkflowStepLog
from agents.ambulance.schemas import TriageRequest, TriageResponse

TRIAGE_SYSTEM_PROMPT = """You are LifeLink AI Triage Agent, a senior medical triage intelligence component for emergency healthcare coordination.

YOUR MANDATE:
1. Carefully analyze the reported patient symptoms, age, gender, and vital signs.
2. Output ONLY a valid JSON object matching these exact field keys:
{
  "urgency": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "severity": "CRITICAL" | "HIGH" | "MODERATE" | "LOW",
  "category": "CARDIAC_EMERGENCY" | "RESPIRATORY_DISTRESS" | "NEUROLOGICAL_STROKE" | "TRAUMA_BLEEDING" | "GENERAL_EMERGENCY",
  "required_specialty": "CARDIOLOGY" | "PULMONOLOGY" | "NEUROLOGY" | "TRAUMA_CARE" | "GENERAL_EMERGENCY",
  "recommended_action": "IMMEDIATE_AMBULANCE_DISPATCH" | "URGENT_HOSPITAL_COORDINATION" | "NON_URGENT_CLINIC_VISIT",
  "decision": "1-sentence decision summary",
  "reasoning": "Detailed clinical reasoning explaining why this urgency, category, and specialty were determined",
  "confidence": 0.95
}

SAFETY MANDATE:
- Do NOT provide a definitive medical diagnosis.
- Do NOT prescribe medications or dosages.
- Frame all assessments as healthcare coordination guidance.
"""


class TriageAgent:
    """
    Emergency Triage AI Agent.
    Combines Featherless LLM reasoning with deterministic heuristic fallbacks.
    """

    def evaluate_triage(self, request: TriageRequest) -> TriageResponse:
        """
        Evaluate emergency request and return structured triage output.
        """
        logger.info(f"TriageAgent evaluating symptoms: '{request.symptoms}'")
        log_workflow_event(
            workflow_name="Emergency Triage",
            step_number=1,
            step_name="Received Triage Request",
            details={"symptoms": request.symptoms, "patient_age": request.patient_age}
        )

        steps = [
            WorkflowStepLog(
                step_number=1,
                step_name="Received Triage Request",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"symptoms": request.symptoms}
            )
        ]

        if featherless_client.is_available:
            try:
                user_prompt = f"""Evaluate the following emergency patient triage request:

Symptoms: {request.symptoms}
Patient Age: {request.patient_age if request.patient_age is not None else 'Not provided'}
Patient Gender: {request.patient_gender or 'Not provided'}
Vital Signs: {request.vital_signs or 'Not provided'}
Location: {request.location or 'Not provided'}
"""
                response = featherless_client.generate_structured_json(
                    prompt=user_prompt,
                    system_prompt=TRIAGE_SYSTEM_PROMPT,
                    response_model=TriageResponse
                )

                log_workflow_event(
                    workflow_name="Emergency Triage",
                    step_number=2,
                    step_name="Completed AI Triage Reasoning",
                    details={"category": response.category, "urgency": response.urgency, "specialty": response.required_specialty}
                )

                steps.append(
                    WorkflowStepLog(
                        step_number=2,
                        step_name="Completed AI Triage Reasoning",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="completed",
                        details={"urgency": response.urgency, "category": response.category, "model": featherless_client.model}
                    )
                )
                response.data_used = [{"model": featherless_client.model, "symptoms": request.symptoms, "ai_reasoning": True}]
                response.workflow_steps = steps
                return response

            except Exception as e:
                logger.warning(f"Featherless Triage call failed, reverting to heuristic reasoning: {e}")

        # Deterministic Heuristic Fallback (Offline / Mock Mode / API failure)
        return self._heuristic_fallback(request, steps)

    def _heuristic_fallback(self, request: TriageRequest, steps: list) -> TriageResponse:
        """Rule-based heuristic engine when LLM is unconfigured or unavailable."""
        symptoms_lower = request.symptoms.lower()

        if any(w in symptoms_lower for w in ["chest pain", "heart", "cardiac", "heart attack"]):
            category = "CARDIAC_EMERGENCY"
            specialty = "CARDIOLOGY"
            urgency = "HIGH"
            severity = "HIGH"
            rec_action = "IMMEDIATE_AMBULANCE_DISPATCH"
            decision = "High-urgency cardiac emergency detected. Immediate specialized transport required."
            reasoning = "Reported symptoms include acute chest discomfort/pain indicative of potential cardiac distress."
            confidence = 0.92
        elif any(w in symptoms_lower for w in ["breath", "breathing", "suffocating", "asthma", "choking"]):
            category = "RESPIRATORY_DISTRESS"
            specialty = "PULMONOLOGY"
            urgency = "HIGH"
            severity = "HIGH"
            rec_action = "IMMEDIATE_AMBULANCE_DISPATCH"
            decision = "High-urgency respiratory emergency detected."
            reasoning = "Reported symptoms include shortness of breath/respiratory impairment requiring oxygen & emergency care."
            confidence = 0.89
        elif any(w in symptoms_lower for w in ["stroke", "paralysis", "numbness", "seizure", "unconscious", "weakness", "slurred", "speech", "facial"]):
            category = "NEUROLOGICAL_STROKE"
            specialty = "NEUROLOGY"
            urgency = "CRITICAL"
            severity = "CRITICAL"
            rec_action = "IMMEDIATE_AMBULANCE_DISPATCH"
            decision = "Critical neurological emergency detected."
            reasoning = "Symptoms suggest acute neurological deficit requiring rapid stroke/neuro-critical evaluation."
            confidence = 0.94
        elif any(w in symptoms_lower for w in ["bleed", "trauma", "accident", "fracture", "fall"]):
            category = "TRAUMA_BLEEDING"
            specialty = "TRAUMA_CARE"
            urgency = "HIGH"
            severity = "HIGH"
            rec_action = "IMMEDIATE_AMBULANCE_DISPATCH"
            decision = "Trauma emergency requiring immediate stabilization."
            reasoning = "Symptoms suggest acute physical trauma requiring emergency wound/fracture stabilization."
            confidence = 0.88
        else:
            category = "GENERAL_EMERGENCY"
            specialty = "GENERAL_EMERGENCY"
            urgency = "MEDIUM"
            severity = "MODERATE"
            rec_action = "URGENT_HOSPITAL_COORDINATION"
            decision = "General acute distress requiring hospital emergency department evaluation."
            reasoning = "Symptoms require physical clinical evaluation by an emergency physician."
            confidence = 0.75

        log_workflow_event(
            workflow_name="Emergency Triage",
            step_number=2,
            step_name="Completed Heuristic Triage Fallback",
            details={"category": category, "urgency": urgency}
        )

        steps.append(
            WorkflowStepLog(
                step_number=2,
                step_name="Completed Heuristic Triage Reasoning",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"urgency": urgency, "category": category}
            )
        )

        return TriageResponse(
            decision=decision,
            reasoning=reasoning,
            confidence=confidence,
            next_action="HOSPITAL_MATCHING",
            data_used=[{"symptoms": request.symptoms, "heuristic": True}],
            workflow_steps=steps,
            urgency=urgency,
            severity=severity,
            category=category,
            required_specialty=specialty,
            recommended_action=rec_action
        )


# Singleton agent instance
triage_agent = TriageAgent()
