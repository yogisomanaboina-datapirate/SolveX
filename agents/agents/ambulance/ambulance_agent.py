from typing import Any, Dict, List, Tuple
from core.logging import logger, log_workflow_event
from tools.ambulance_tools import create_simulated_dispatch_event, generate_hospital_notification_payload
from agents.ambulance.schemas import (
    HospitalNotificationPayload,
    HospitalSelection,
    SimulatedAmbulanceDispatch,
    TriageResponse,
)


class AmbulanceSelectionAgent:
    """
    AI Agent responsible for evaluating available ambulances and orchestrating simulated emergency dispatch.
    """

    def select_and_dispatch(
        self,
        available_ambulances: List[Dict[str, Any]],
        selected_hospital: HospitalSelection,
        triage: TriageResponse,
        patient_symptoms: str
    ) -> Tuple[SimulatedAmbulanceDispatch, HospitalNotificationPayload]:
        """
        Select optimal available ambulance unit, create simulated dispatch record,
        and generate hospital emergency alert notification payload.
        """
        if not available_ambulances:
            # Fallback if no available ambulances in dataset
            selected_amb = {
                "ambulance_id": "AMB-FALLBACK",
                "vehicle_number": "TS-09-EMERGENCY-01",
                "type": "ALS",
                "estimated_eta_minutes": 10
            }
        else:
            selected_amb = available_ambulances[0]

        log_workflow_event(
            workflow_name="Emergency Ambulance Dispatch",
            step_number=4,
            step_name="Selected Ambulance Unit",
            details={
                "vehicle_number": selected_amb["vehicle_number"],
                "type": selected_amb["type"],
                "eta_minutes": selected_amb["estimated_eta_minutes"]
            }
        )

        # 1. Create simulated dispatch record
        hospital_dict = {
            "hospital_id": selected_hospital.hospital_id,
            "hospital_name": selected_hospital.hospital_name
        }
        raw_dispatch = create_simulated_dispatch_event(
            ambulance=selected_amb,
            hospital=hospital_dict,
            patient_symptoms=patient_symptoms,
            urgency=triage.urgency
        )

        dispatch_model = SimulatedAmbulanceDispatch(
            dispatch_id=raw_dispatch["dispatch_id"],
            ambulance_id=raw_dispatch["ambulance_id"],
            vehicle_number=raw_dispatch["vehicle_number"],
            ambulance_type=raw_dispatch["ambulance_type"],
            hospital_id=raw_dispatch["hospital_id"],
            hospital_name=raw_dispatch["hospital_name"],
            estimated_patient_eta_minutes=raw_dispatch["estimated_patient_eta_minutes"],
            dispatch_status=raw_dispatch["dispatch_status"],
            timestamp=raw_dispatch["timestamp"]
        )

        # 2. Generate hospital notification payload
        raw_notif = generate_hospital_notification_payload(
            hospital=hospital_dict,
            ambulance_dispatch=raw_dispatch,
            triage_category=triage.category,
            urgency=triage.urgency,
            required_specialty=triage.required_specialty
        )

        notification_model = HospitalNotificationPayload(
            notification_id=raw_notif["notification_id"],
            target_hospital_id=raw_notif["target_hospital_id"],
            target_hospital_name=raw_notif["target_hospital_name"],
            patient_triage_category=raw_notif["patient_triage_category"],
            patient_urgency=raw_notif["patient_urgency"],
            required_specialty=raw_notif["required_specialty"],
            assigned_ambulance_id=raw_notif["assigned_ambulance_id"],
            estimated_arrival_minutes=raw_notif["estimated_arrival_minutes"],
            alert_message=raw_notif["alert_message"],
            timestamp=raw_notif["timestamp"]
        )

        log_workflow_event(
            workflow_name="Emergency Notification",
            step_number=5,
            step_name="Generated Hospital ER Alert Notification",
            details={"target_hospital": selected_hospital.hospital_name, "alert": raw_notif["alert_message"]}
        )

        return dispatch_model, notification_model


ambulance_selection_agent = AmbulanceSelectionAgent()
