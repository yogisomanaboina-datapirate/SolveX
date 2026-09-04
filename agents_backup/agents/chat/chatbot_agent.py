from datetime import datetime, timezone
from typing import List, Optional
from core.featherless import featherless_client
from core.logging import logger, log_workflow_event
from core.schemas import WorkflowStepLog
from agents.chat.schemas import (
    ChatMessage,
    ChatbotRequest,
    ChatbotResponse,
    PatientContextProfile,
)

CHATBOT_SYSTEM_PROMPT = """You are LifeLink AI Health Assistant, an intelligent, empathetic healthcare coordination and medical information AI assistant.

YOUR MANDATE:
1. Provide helpful, clear, patient-friendly answers to health questions, medical queries, and system guidance.
2. If patient context profile (conditions, medications, lab values) is supplied, personalize your response safely while acknowledging their background.
3. Categorize user intent into ONE of:
   - GENERAL_HEALTH_QUERY
   - PERSONALIZED_PATIENT_QUERY
   - MEDICATION_INQUIRY
   - EMERGENCY_GUIDANCE
   - INSURANCE_QUERY
4. Suggest 2-3 actionable quick-action chips for the user interface.
5. Output ONLY a valid JSON object matching these exact keys:
{
  "message": "Empathetic, clear conversational response text for the user",
  "intent": "GENERAL_HEALTH_QUERY" | "PERSONALIZED_PATIENT_QUERY" | "MEDICATION_INQUIRY" | "EMERGENCY_GUIDANCE" | "INSURANCE_QUERY",
  "personalized_data_used": true/false,
  "suggested_quick_actions": ["Action 1", "Action 2"],
  "decision": "Brief summary decision of chatbot answer",
  "reasoning": "Rationale explaining how response was formed",
  "next_action": "CONTINUE_CONVERSATION" or "TRIGGER_EMERGENCY_WORKFLOW",
  "confidence": 0.95,
  "disclaimer": "LifeLink AI Assistant provides health information and coordination guidance. It is not a medical diagnosis or treatment. In an emergency, seek immediate medical attention."
}

SAFETY RULES:
- Do NOT make definitive medical diagnoses or prescribe medications.
- If the user reports emergency symptoms (chest pain, severe breathlessness, sudden weakness), advise them to seek emergency care immediately and suggest triggering Emergency Ambulance Response.
- Always remain supportive and medically safe.
"""


class HealthChatbotAgent:
    """
    Autonomous AI Chatbot Agent for patient interaction, medical Q&A, and health coordination.
    """

    def _classify_intent_heuristically(self, text: str, profile: Optional[PatientContextProfile]) -> str:
        t = text.lower()
        if any(w in t for w in ["chest pain", "breathless", "bleeding", "stroke", "faint", "emergency", "ambulance"]):
            return "EMERGENCY_GUIDANCE"
        elif any(w in t for w in ["pill", "tablet", "dose", "medication", "side effect", "prescription", "take"]):
            return "MEDICATION_INQUIRY"
        elif any(w in t for w in ["claim", "insurance", "copay", "deductible", "policy", "coverage"]):
            return "INSURANCE_QUERY"
        elif profile and (profile.active_conditions or profile.current_medications or profile.latest_lab_results):
            return "PERSONALIZED_PATIENT_QUERY"
        else:
            return "GENERAL_HEALTH_QUERY"

    def chat(self, request: ChatbotRequest) -> ChatbotResponse:
        """
        Process incoming chat query with optional context & multi-turn memory.
        """
        user_msg = request.message.strip()
        profile = request.patient_profile
        history = request.conversation_history or []

        logger.info(f"HealthChatbotAgent processing message: '{user_msg[:60]}...'")
        log_workflow_event("Health Chatbot Agent", 1, "Chat Request Received")

        steps: List[WorkflowStepLog] = [
            WorkflowStepLog(
                step_number=1,
                step_name="Chat Request Received",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"message_length": len(user_msg), "has_patient_profile": profile is not None}
            )
        ]

        # STEP 2: Intent Classification & Context Preparation
        intent = self._classify_intent_heuristically(user_msg, profile)
        personalized_used = False

        profile_text = ""
        if profile:
            parts = []
            if profile.patient_name:
                parts.append(f"Name: {profile.patient_name}")
            if profile.patient_age:
                parts.append(f"Age: {profile.patient_age}")
            if profile.active_conditions:
                parts.append(f"Active Conditions: {', '.join(profile.active_conditions)}")
            if profile.current_medications:
                parts.append(f"Medications: {', '.join(profile.current_medications)}")
            if profile.latest_lab_results:
                parts.append(f"Recent Labs: {profile.latest_lab_results}")
            if profile.insurance_policy:
                parts.append(f"Insurance: {profile.insurance_policy}")

            if parts:
                profile_text = "\n[Patient Profile Context Provided by Backend]:\n" + "\n".join(parts)
                personalized_used = True

        steps.append(
            WorkflowStepLog(
                step_number=2,
                step_name="Context Prepared & Intent Classified",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"intent": intent, "personalized_data_used": personalized_used}
            )
        )

        # Fallback responses
        if intent == "EMERGENCY_GUIDANCE":
            reply = (
                "If you or someone nearby is experiencing severe symptoms like chest pain, sudden breathlessness, "
                "or severe trauma, please seek immediate emergency care. You can use the LifeLink Emergency "
                "button above to dispatch a simulated ambulance and locate nearby hospitals right away."
            )
            actions = ["Trigger Emergency Ambulance", "Find Nearby Hospitals"]
        elif intent == "MEDICATION_INQUIRY":
            reply = (
                "For medication schedules and intake guidelines, always follow your doctor's explicit prescription instructions. "
                "You can use the LifeLink Medication Scheduler to set daily intake reminders and check for conflicts."
            )
            actions = ["Open Medication Scheduler", "View Active Medications"]
        elif intent == "INSURANCE_QUERY":
            reply = (
                "LifeLink Insurance Assistance can help check your policy coverage, estimate co-pays, and verify claims. "
                "Would you like to analyze an insurance claim or query policy eligibility?"
            )
            actions = ["Check Insurance Coverage", "Analyze Claim File"]
        elif personalized_used and profile:
            cond_str = ", ".join(profile.active_conditions) if profile.active_conditions else "general wellness"
            reply = (
                f"Hello{f' {profile.patient_name}' if profile.patient_name else ''}! "
                f"Based on your profile context ({cond_str}), I am here to help answer your questions about your health, "
                "medications, and lab reports."
            )
            actions = ["Analyze Medical Report", "Check Medication Reminders"]
        else:
            reply = (
                "Hello! I am your LifeLink AI Health Assistant. How can I help you today with your health queries, "
                "emergency guidance, or medical report analysis?"
            )
            actions = ["Analyze Medical Report", "Check Emergency Services", "Medication Reminders"]

        decision = f"Responded to user query classified under '{intent}'."
        reasoning = f"Evaluated query text and patient profile context (personalized: {personalized_used})."
        next_action = "TRIGGER_EMERGENCY_WORKFLOW" if intent == "EMERGENCY_GUIDANCE" else "CONTINUE_CONVERSATION"
        confidence = 0.95
        disclaimer = "LifeLink AI Assistant provides health information and coordination guidance. It is not a medical diagnosis or treatment. In an emergency, seek immediate medical attention."

        # STEP 3: Featherless AI / HuggingFace Model Generation
        if featherless_client.is_available:
            try:
                hist_str = ""
                if history:
                    hist_str = "\n[Recent Chat History]:\n" + "\n".join([f"{m.role}: {m.content}" for m in history[-4:]])

                prompt = f"{user_msg}{profile_text}{hist_str}"

                ai_res = featherless_client.generate_structured_json(
                    prompt=prompt,
                    system_prompt=CHATBOT_SYSTEM_PROMPT,
                    response_model=ChatbotResponse
                )

                reply = ai_res.message or reply
                intent = ai_res.intent or intent
                if ai_res.suggested_quick_actions:
                    actions = ai_res.suggested_quick_actions
                decision = ai_res.decision or decision
                reasoning = ai_res.reasoning or reasoning
                next_action = ai_res.next_action or next_action
                confidence = ai_res.confidence or confidence
                disclaimer = ai_res.disclaimer or disclaimer

                steps.append(
                    WorkflowStepLog(
                        step_number=3,
                        step_name="Featherless AI Conversational Model Response Generated",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="completed",
                        details={"model": featherless_client.model, "intent": intent}
                    )
                )
            except Exception as e:
                logger.warning(f"Featherless AI chatbot generation failed, using rule-based response: {e}")
                steps.append(
                    WorkflowStepLog(
                        step_number=3,
                        step_name="Rule-Based Chatbot Response Generated",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="completed",
                        details={"rule_based": True}
                    )
                )
        else:
            steps.append(
                WorkflowStepLog(
                    step_number=3,
                    step_name="Rule-Based Chatbot Response Generated",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="completed",
                    details={"rule_based": True}
                )
            )

        steps.append(
            WorkflowStepLog(
                step_number=4,
                step_name="Chatbot Response Finalized",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"intent": intent}
            )
        )

        log_workflow_event("Health Chatbot Agent", 4, "Chatbot Response Finalized")

        return ChatbotResponse(
            message=reply,
            intent=intent,
            personalized_data_used=personalized_used,
            suggested_quick_actions=actions,
            decision=decision,
            reasoning=reasoning,
            confidence=confidence,
            next_action=next_action,
            disclaimer=disclaimer,
            data_used=[
                {"intent": intent},
                {"personalized_data_used": personalized_used}
            ],
            workflow_steps=steps
        )


chatbot_agent = HealthChatbotAgent()
