from typing import Any, Dict, List, Optional
from pydantic import AliasChoices, BaseModel, Field
from core.schemas import BaseDecisionResponse, WorkflowStepLog


class ChatMessage(BaseModel):
    """Single chat message in conversation history."""
    role: str = Field(description="Role of message sender: 'user', 'assistant', or 'system'", examples=["user"])
    content: str = Field(description="Text content of message", examples=["What are normal hemoglobin levels?"])


class PatientContextProfile(BaseModel):
    """Optional patient profile context provided by Backend to personalize responses."""
    patient_name: Optional[str] = Field(default=None, description="Patient full name")
    patient_age: Optional[int] = Field(default=None, description="Patient age")
    patient_gender: Optional[str] = Field(default=None, description="Patient gender")
    active_conditions: List[str] = Field(default_factory=list, description="Known medical diagnoses e.g. Hypertension, Asthma")
    current_medications: List[str] = Field(default_factory=list, description="List of active prescribed medications")
    latest_lab_results: Dict[str, Any] = Field(default_factory=dict, description="Recent lab parameters e.g. {'Hemoglobin': '11.2 g/dL'}")
    insurance_policy: Optional[str] = Field(default=None, description="Active insurance plan name")


class ChatbotRequest(BaseModel):
    """Payload for user chatbot message received from Backend/Frontend."""
    message: str = Field(
        description="User query or message text",
        examples=["What should I do if I feel mild shortness of breath?"]
    )
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Optional recent messages for multi-turn chat memory"
    )
    patient_profile: Optional[PatientContextProfile] = Field(
        default=None,
        description="Optional patient profile context passed by Backend"
    )


class ChatbotResponse(BaseDecisionResponse):
    """Structured response output from LifeLink AI Chatbot."""
    message: str = Field(
        description="Conversational response message from LifeLink AI Health Assistant",
        validation_alias=AliasChoices("message", "response_text", "reply")
    )
    intent: str = Field(
        default="GENERAL_HEALTH_QUERY",
        description="Classified user query intent: GENERAL_HEALTH_QUERY, PERSONALIZED_PATIENT_QUERY, MEDICATION_INQUIRY, EMERGENCY_GUIDANCE, INSURANCE_QUERY",
        examples=["GENERAL_HEALTH_QUERY"]
    )
    personalized_data_used: bool = Field(
        default=False,
        description="True if user-specific patient profile context was incorporated in the response"
    )
    suggested_quick_actions: List[str] = Field(
        default_factory=list,
        description="Recommended action chips for user UI e.g. ['View Medication Reminders', 'Check Emergency Hospitals']"
    )
    disclaimer: str = Field(
        default="LifeLink AI Assistant provides health information and coordination guidance. It is not a medical diagnosis or treatment. In an emergency, seek immediate medical attention.",
        description="Safety disclaimer for conversational health queries"
    )
