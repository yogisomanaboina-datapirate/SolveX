from typing import Any, Dict, List, Optional
from pydantic import AliasChoices, BaseModel, Field
from core.schemas import BaseDecisionResponse, WorkflowStepLog


class MedicationItem(BaseModel):
    """Single doctor-prescribed medication item."""
    medication_name: str = Field(description="Name of prescribed medication", examples=["Amoxicillin"])
    prescribed_dosage: str = Field(description="Prescribed dosage per intake", examples=["500mg"])
    prescribed_frequency: str = Field(
        description="Prescribed frequency e.g. Once daily, Twice daily, Every 8 hours",
        examples=["Twice daily"]
    )
    meal_relationship: Optional[str] = Field(
        default="AFTER_MEAL",
        description="Relationship to meals: AFTER_MEAL, BEFORE_MEAL, WITH_FOOD, ANYTIME",
        examples=["AFTER_MEAL"]
    )
    prescribed_duration_days: Optional[int] = Field(default=7, description="Number of treatment days")
    special_instructions: Optional[str] = Field(default=None, description="Doctor special instructions")


class MedicationScheduleRequest(BaseModel):
    """Medication schedule generation request payload."""
    patient_id: Optional[str] = Field(default=None, description="Patient reference ID")
    medications: List[MedicationItem] = Field(
        description="List of doctor-prescribed medications to schedule"
    )
    user_wake_time: str = Field(default="08:00", description="User typical wake time (HH:MM format)")
    user_sleep_time: str = Field(default="22:00", description="User typical sleep time (HH:MM format)")
    user_meal_times: Optional[Dict[str, str]] = Field(
        default_factory=lambda: {"breakfast": "08:30", "lunch": "13:00", "dinner": "20:00"},
        description="User daily meal times"
    )
    existing_scheduled_reminders: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Existing scheduled reminders for conflict detection"
    )


class ScheduledReminder(BaseModel):
    """Structured reminder entry for single medication intake."""
    reminder_id: str
    medication_name: str
    dosage: str
    scheduled_time: str = Field(description="Reminder time in HH:MM format", examples=["09:00"])
    meal_relation_note: str
    instructions: str


class ScheduleConflict(BaseModel):
    """Timing conflict or overlap detection entry."""
    conflict_type: str = Field(description="Category: CLOSE_TIMING, OVERLAPPING_MEDICATION, OUTSIDE_WAKE_HOURS")
    medication_a: str
    medication_b: Optional[str] = None
    description: str
    resolution_recommendation: str


class MedicationScheduleResponse(BaseDecisionResponse):
    """Structured Medication Reminder Plan AI Decision Output."""
    decision: str = Field(
        validation_alias=AliasChoices("decision", "summary"),
        description="Summary of generated reminder plan"
    )
    reasoning: str = Field(
        validation_alias=AliasChoices("reasoning", "rationale"),
        description="Explanation of schedule calculation and conflict checks"
    )
    confidence: float = Field(default=0.95, description="Schedule confidence score")
    scheduled_reminders: List[ScheduledReminder] = Field(
        default_factory=list,
        description="Generated chronological medication reminders"
    )
    conflicts_detected: List[ScheduleConflict] = Field(
        default_factory=list,
        description="Detected timing conflicts if any"
    )
    has_conflicts: bool = Field(default=False, description="Flag indicating if conflicts exist")
    notification_payloads: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Structured reminder notification payloads for Backend scheduling"
    )
    disclaimer: str = Field(
        default="LifeLink AI organizes reminder schedules from supplied doctor prescriptions. This AI does not prescribe medications or alter dosages.",
        description="Mandatory medical safety disclaimer"
    )
