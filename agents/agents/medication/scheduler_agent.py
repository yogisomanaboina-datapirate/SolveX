from datetime import datetime, timezone
from typing import Any, Dict, List
from core.featherless import featherless_client
from core.logging import logger, log_workflow_event
from core.schemas import WorkflowStepLog
from tools.medication_tools import detect_medication_schedule_conflicts, generate_deterministic_reminder_times
from agents.medication.schemas import (
    MedicationScheduleRequest,
    MedicationScheduleResponse,
    ScheduleConflict,
    ScheduledReminder,
)

MEDICATION_SCHEDULER_SYSTEM_PROMPT = """You are LifeLink AI Medication & Tablet Scheduler Agent.

YOUR MANDATE:
1. Review the generated medication reminder schedule and conflict analysis.
2. Explain the schedule clearly and concisely for the patient.
3. Output ONLY a valid JSON object matching these exact keys:
{
  "decision": "Summary of generated medication schedule",
  "reasoning": "Clear explanation of reminder timing, meal alignment, and conflict adjustments",
  "next_action": "SCHEDULE_BACKEND_NOTIFICATIONS",
  "recommended_action": "SCHEDULE_BACKEND_NOTIFICATIONS",
  "confidence": 0.95
}

CRITICAL SAFETY RULES:
- Do NOT invent medication names, dosages, or new prescriptions.
- Do NOT alter doctor-prescribed dosages.
"""


class MedicationSchedulerAgent:
    """
    AI Agent responsible for organizing prescription schedules and generating reminder notifications.
    Safety constraint: Only schedules supplied doctor prescriptions; does not prescribe.
    """

    def generate_schedule(self, request: MedicationScheduleRequest) -> MedicationScheduleResponse:
        """
        Generate medication reminder plan from supplied prescription items.
        """
        logger.info(f"MedicationSchedulerAgent scheduling {len(request.medications)} prescribed medication(s)")
        log_workflow_event(
            workflow_name="Medication Scheduler",
            step_number=1,
            step_name="Received Prescription Input",
            details={"medication_count": len(request.medications)}
        )

        steps = [
            WorkflowStepLog(
                step_number=1,
                step_name="Received Prescription Input",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"medication_names": [m.medication_name for m in request.medications]}
            )
        ]

        # STEP 1: Deterministic Tool — Generate reminder times per medication
        all_reminders: List[ScheduledReminder] = []
        for med in request.medications:
            med_rems = generate_deterministic_reminder_times(
                medication=med,
                wake_time_str=request.user_wake_time,
                sleep_time_str=request.user_sleep_time,
                meal_times=request.user_meal_times
            )
            all_reminders.extend(med_rems)

        # Sort reminders chronologically by time
        all_reminders.sort(key=lambda r: r.scheduled_time)

        steps.append(
            WorkflowStepLog(
                step_number=2,
                step_name="Generated Reminder Timing Schedule",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"total_reminders": len(all_reminders)}
            )
        )

        # STEP 2: Deterministic Tool — Conflict Detection
        conflicts = detect_medication_schedule_conflicts(
            scheduled_reminders=all_reminders,
            wake_time_str=request.user_wake_time,
            sleep_time_str=request.user_sleep_time
        )
        has_conflicts = len(conflicts) > 0

        steps.append(
            WorkflowStepLog(
                step_number=3,
                step_name="Completed Conflict Detection Inspection",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="completed",
                details={"conflicts_found": len(conflicts)}
            )
        )

        # STEP 3: Generate Notification Payloads for Backend Scheduler
        notification_payloads: List[Dict[str, Any]] = []
        for rem in all_reminders:
            notification_payloads.append({
                "reminder_id": rem.reminder_id,
                "title": f"Medication Reminder: {rem.medication_name}",
                "body": f"Time to take {rem.dosage} of {rem.medication_name}. ({rem.meal_relation_note})",
                "scheduled_time_hhmm": rem.scheduled_time,
                "medication_name": rem.medication_name,
                "dosage": rem.dosage
            })

        # STEP 4: AI Reasoning over tool results
        med_names = ", ".join([m.medication_name for m in request.medications])
        decision = f"Generated {len(all_reminders)} reminder notifications for {med_names}."
        reasoning = (
            f"Reminders scheduled based on doctor prescription frequencies aligned with user wake time ({request.user_wake_time}) "
            f"and sleep time ({request.user_sleep_time}). {'Conflicts detected requiring spacing adjustments.' if has_conflicts else 'No timing conflicts found.'}"
        )
        confidence = 0.95

        if featherless_client.is_available:
            try:
                rems_summary = "\n".join([
                    f"- [{r.scheduled_time}] {r.medication_name} ({r.dosage}): {r.meal_relation_note}"
                    for r in all_reminders
                ])
                conflicts_summary = "\n".join([
                    f"- Conflict: {c.description} -> {c.resolution_recommendation}"
                    for c in conflicts
                ]) if conflicts else "None"

                prompt = (
                    f"Prescribed Medications: {med_names}\n"
                    f"User Schedule: Wake = {request.user_wake_time}, Sleep = {request.user_sleep_time}\n"
                    f"Generated Reminders:\n{rems_summary}\n\n"
                    f"Conflicts Identified:\n{conflicts_summary}\n"
                    "Explain this schedule concisely and provide helpful reminder guidance."
                )

                ai_res = featherless_client.generate_structured_json(
                    prompt=prompt,
                    system_prompt=MEDICATION_SCHEDULER_SYSTEM_PROMPT,
                    response_model=MedicationScheduleResponse
                )

                decision = ai_res.decision
                reasoning = ai_res.reasoning
                confidence = ai_res.confidence

                steps.append(
                    WorkflowStepLog(
                        step_number=4,
                        step_name="Completed Featherless AI Schedule Reasoning",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="completed",
                        details={"model": featherless_client.model}
                    )
                )

            except Exception as e:
                logger.warning(f"Featherless AI scheduler call failed, using rule-based reasoning: {e}")
                steps.append(
                    WorkflowStepLog(
                        step_number=4,
                        step_name="Completed Rule-Based Schedule Reasoning",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        status="completed",
                        details={"rule_based": True}
                    )
                )
        else:
            steps.append(
                WorkflowStepLog(
                    step_number=4,
                    step_name="Completed Rule-Based Schedule Reasoning",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    status="completed",
                    details={"rule_based": True}
                )
            )

        log_workflow_event("Medication Scheduler", 5, "Schedule Plan Generation Finalized", {"reminders_count": len(all_reminders)})

        return MedicationScheduleResponse(
            decision=decision,
            reasoning=reasoning,
            confidence=confidence,
            next_action="SCHEDULE_BACKEND_NOTIFICATIONS",
            scheduled_reminders=all_reminders,
            conflicts_detected=conflicts,
            has_conflicts=has_conflicts,
            notification_payloads=notification_payloads,
            data_used=[
                {"medications_count": len(request.medications)},
                {"scheduled_reminders_count": len(all_reminders)},
                {"conflicts_count": len(conflicts)}
            ],
            workflow_steps=steps
        )


medication_scheduler_agent = MedicationSchedulerAgent()
