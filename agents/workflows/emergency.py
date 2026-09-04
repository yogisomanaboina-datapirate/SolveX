from datetime import datetime, timezone
from typing import List
from core.logging import logger, log_workflow_event
from core.schemas import WorkflowStepLog
from tools.ambulance_tools import evaluate_available_ambulances
from tools.hospital_tools import discover_nearby_hospitals, evaluate_hospital_suitability
from agents.ambulance.ambulance_agent import ambulance_selection_agent
from agents.ambulance.hospital_agent import hospital_matching_agent
from agents.ambulance.schemas import (
    AmbulanceInfo,
    EmergencyWorkflowRequest,
    EmergencyWorkflowResponse,
    HospitalInfo,
    NearbyHospitalInfo,
    NearbyHospitalsRequest,
    TriageRequest,
    TriageResponse,
)
from agents.ambulance.triage import triage_agent

# Default static dataset for Hospitals (used when Backend doesn't supply candidate list)
DEFAULT_HOSPITALS = [
    HospitalInfo(
        id="HOSP-01",
        name="Apollo Emergency Hospital Jubilee Hills",
        location={"lat": 17.4325, "lng": 78.4071, "address": "Jubilee Hills, Hyderabad"},
        specialties=["CARDIOLOGY", "NEUROLOGY", "TRAUMA_CARE", "GENERAL_EMERGENCY"],
        icu_beds_available=4,
        er_beds_available=8
    ),
    HospitalInfo(
        id="HOSP-02",
        name="KIMS Trauma & Heart Institute Secunderabad",
        location={"lat": 17.4436, "lng": 78.4842, "address": "Minister Road, Secunderabad"},
        specialties=["CARDIOLOGY", "PULMONOLOGY", "TRAUMA_CARE", "GENERAL_EMERGENCY"],
        icu_beds_available=2,
        er_beds_available=5
    ),
    HospitalInfo(
        id="HOSP-03",
        name="Yashoda Care Hospital Gachibowli",
        location={"lat": 17.4401, "lng": 78.3489, "address": "Gachibowli, Hyderabad"},
        specialties=["NEUROLOGY", "PULMONOLOGY", "GENERAL_EMERGENCY"],
        icu_beds_available=0,
        er_beds_available=3
    )
]

# Default static dataset for Ambulances (used when Backend doesn't supply ambulance list)
DEFAULT_AMBULANCES = [
    AmbulanceInfo(
        id="AMB-101",
        vehicle_number="TS-09-AMB-1001",
        type="ALS",
        status="AVAILABLE",
        current_location={"lat": 17.4450, "lng": 78.3880, "address": "Madhapur Hub"}
    ),
    AmbulanceInfo(
        id="AMB-102",
        vehicle_number="TS-09-AMB-1002",
        type="BLS",
        status="AVAILABLE",
        current_location={"lat": 17.4520, "lng": 78.3950, "address": "Kondapur Station"}
    ),
    AmbulanceInfo(
        id="AMB-103",
        vehicle_number="TS-09-AMB-1003",
        type="CRITICAL_CARE",
        status="BUSY",
        current_location={"lat": 17.4300, "lng": 78.4000, "address": "On Route"}
    )
]


def run_triage_workflow(request: TriageRequest) -> TriageResponse:
    """
    Execute standalone Triage workflow step.
    """
    logger.info("Executing Emergency Triage Workflow...")
    response = triage_agent.evaluate_triage(request)
    logger.info(f"Triage Workflow Completed -> Urgency: {response.urgency}, Specialty: {response.required_specialty}")
    return response


def run_nearby_hospitals_workflow(request: NearbyHospitalsRequest) -> List[NearbyHospitalInfo]:
    """
    Standalone non-LLM workflow to discover nearby hospitals around user GPS coordinates.
    """
    hospitals_input = [
        h.model_dump() for h in (request.candidate_hospitals or DEFAULT_HOSPITALS)
    ]
    return discover_nearby_hospitals(
        user_lat=request.user_location.lat,
        user_lng=request.user_location.lng,
        radius_km=request.radius_km,
        candidate_hospitals=hospitals_input
    )


def run_full_emergency_workflow(request: EmergencyWorkflowRequest) -> EmergencyWorkflowResponse:
    """
    Execute complete end-to-end multi-agent emergency workflow:
    Triage -> Hospital Tool -> Hospital Agent -> Ambulance Tool -> Ambulance Agent -> Dispatch -> Nearby Real Hospitals.
    """
    logger.info("Executing Full Multi-Agent Emergency Response Workflow...")
    log_workflow_event("Emergency Workflow", 1, "Workflow Initiated", {"symptoms": request.symptoms})

    steps: List[WorkflowStepLog] = [
        WorkflowStepLog(
            step_number=1,
            step_name="Workflow Initiated",
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="completed",
            details={"symptoms": request.symptoms, "location": request.patient_location.model_dump()}
        )
    ]

    # STEP 1: AI Triage Assessment
    triage_req = TriageRequest(
        symptoms=request.symptoms,
        patient_age=request.patient_age,
        patient_gender=request.patient_gender,
        vital_signs=request.vital_signs,
        location=request.patient_location
    )
    triage_res = triage_agent.evaluate_triage(triage_req)
    steps.append(
        WorkflowStepLog(
            step_number=2,
            step_name="AI Triage Assessment Completed",
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="completed",
            details={
                "urgency": triage_res.urgency,
                "category": triage_res.category,
                "required_specialty": triage_res.required_specialty
            }
        )
    )

    # STEP 2: Hospital Evaluation Tool
    hospitals_input = [
        h.model_dump() for h in (request.candidate_hospitals or DEFAULT_HOSPITALS)
    ]
    patient_lat = request.patient_location.lat
    patient_lng = request.patient_location.lng

    evaluated_hospitals = evaluate_hospital_suitability(
        hospitals=hospitals_input,
        required_specialty=triage_res.required_specialty,
        urgency=triage_res.urgency,
        patient_lat=patient_lat,
        patient_lng=patient_lng
    )

    # STEP 3: Hospital Matching Agent
    selected_hospital = hospital_matching_agent.select_best_hospital(
        evaluated_hospitals=evaluated_hospitals,
        triage=triage_res
    )
    steps.append(
        WorkflowStepLog(
            step_number=3,
            step_name="Hospital Matching Completed",
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="completed",
            details={
                "selected_hospital": selected_hospital.hospital_name,
                "distance_km": selected_hospital.distance_km,
                "eta_minutes": selected_hospital.estimated_eta_minutes
            }
        )
    )

    # STEP 4: Ambulance Evaluation Tool
    ambulances_input = [
        a.model_dump() for a in (request.available_ambulances or DEFAULT_AMBULANCES)
    ]
    available_ambulances = evaluate_available_ambulances(
        ambulances=ambulances_input,
        patient_lat=patient_lat,
        patient_lng=patient_lng
    )

    # STEP 5: Ambulance Selection & Dispatch Agent
    dispatch, notification = ambulance_selection_agent.select_and_dispatch(
        available_ambulances=available_ambulances,
        selected_hospital=selected_hospital,
        triage=triage_res,
        patient_symptoms=request.symptoms
    )
    steps.append(
        WorkflowStepLog(
            step_number=4,
            step_name="Ambulance Selected & Simulated Dispatch Created",
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="completed",
            details={
                "dispatch_id": dispatch.dispatch_id,
                "vehicle_number": dispatch.vehicle_number,
                "eta_minutes": dispatch.estimated_patient_eta_minutes
            }
        )
    )
    steps.append(
        WorkflowStepLog(
            step_number=5,
            step_name="Hospital ER Alert Notification Payload Generated",
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="completed",
            details={
                "notification_id": notification.notification_id,
                "target_hospital": notification.target_hospital_name
            }
        )
    )

    # STEP 6: Nearby Real Hospitals Discovery (Non-LLM Tool)
    nearby_hospitals = discover_nearby_hospitals(
        user_lat=patient_lat,
        user_lng=patient_lng,
        radius_km=request.nearby_radius_km,
        candidate_hospitals=hospitals_input
    )

    steps.append(
        WorkflowStepLog(
            step_number=6,
            step_name="Nearby Real Hospitals Discovered",
            timestamp=datetime.now(timezone.utc).isoformat(),
            status="completed",
            details={
                "nearby_count": len(nearby_hospitals),
                "closest_hospital": nearby_hospitals[0].name if nearby_hospitals else "None in radius"
            }
        )
    )

    # Assemble Final Structured Response
    decision_summary = (
        f"Autonomous Emergency Response Orchestrated: [{triage_res.urgency}] {triage_res.category} triaged -> "
        f"{selected_hospital.hospital_name} selected -> Ambulance {dispatch.vehicle_number} dispatch created."
    )
    overall_reasoning = (
        f"1. Triage classified patient symptoms as {triage_res.category} requiring {triage_res.required_specialty}.\n"
        f"2. Hospital Matching evaluated facility options and selected {selected_hospital.hospital_name} ({selected_hospital.suitability_reason}).\n"
        f"3. Ambulance Dispatch assigned vehicle {dispatch.vehicle_number} (ETA ~{dispatch.estimated_patient_eta_minutes} mins).\n"
        f"4. Discovered {len(nearby_hospitals)} nearby hospital(s) around user coordinates ({patient_lat}, {patient_lng}) for direct travel option."
    )

    log_workflow_event("Emergency Workflow", 6, "Workflow Execution Completed Successfully")

    return EmergencyWorkflowResponse(
        decision=decision_summary,
        reasoning=overall_reasoning,
        confidence=triage_res.confidence,
        next_action="EXECUTE_BACKEND_FIREBASE_DISPATCH_AND_PUSH_NOTIFICATION",
        data_used=[
            {"triage": triage_res.category, "specialty": triage_res.required_specialty},
            {"evaluated_hospitals_count": len(evaluated_hospitals), "selected": selected_hospital.hospital_name},
            {"evaluated_ambulances_count": len(available_ambulances), "selected_unit": dispatch.vehicle_number},
            {"nearby_hospitals_count": len(nearby_hospitals)}
        ],
        workflow_steps=steps,
        triage=triage_res,
        selected_hospital=selected_hospital,
        assigned_ambulance=dispatch,
        hospital_notification=notification,
        nearby_hospitals=nearby_hospitals,
        direct_travel_disclaimer="Nearby hospitals are shown for direct access if feasible. For serious or life-threatening emergencies, follow appropriate emergency medical guidance and await ambulance response."
    )
