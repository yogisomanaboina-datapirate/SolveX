from typing import Any, Dict, List, Tuple
from agents.beds.schemas import BedInventory, HospitalBedAllocation


def get_bed_counts(inv: BedInventory, bed_type: str) -> Tuple[int, int]:
    """Get (total_beds, occupied_beds) for a specific bed type."""
    bt = bed_type.upper()
    if bt == "ICU":
        return inv.icu_beds_total, inv.icu_beds_occupied
    elif bt == "ER":
        return inv.er_beds_total, inv.er_beds_occupied
    elif bt == "PEDIATRIC":
        return inv.pediatric_beds_total, inv.pediatric_beds_occupied
    elif bt == "SURGICAL":
        return inv.surgical_beds_total, inv.surgical_beds_occupied
    else:  # GENERAL
        return inv.general_beds_total, inv.general_beds_occupied


def evaluate_and_rank_bed_allocations(
    inventories: List[BedInventory],
    required_bed_type: str,
    required_specialty: str,
    patient_urgency: str,
    surge_factor: float = 1.0
) -> List[HospitalBedAllocation]:
    """
    Deterministic Tool: Mathematically evaluate and rank hospital bed allocations
    based on real-time availability, specialty alignment, and predictive surge impact.
    """
    allocations: List[HospitalBedAllocation] = []

    for inv in inventories:
        total_beds, occupied_beds = get_bed_counts(inv, required_bed_type)
        available_beds = max(total_beds - occupied_beds, 0)

        # Predictive surge projection
        surged_occupied = min(total_beds, round(occupied_beds * surge_factor))
        post_allocation_occupied = min(total_beds, surged_occupied + 1)
        projected_occupancy_pct = (
            round((post_allocation_occupied / total_beds) * 100.0, 1)
            if total_beds > 0 else 100.0
        )

        # Specialty match evaluation
        specialties = [s.upper() for s in inv.specialties]
        specialty_matched = (required_specialty.upper() in specialties) or ("GENERAL_EMERGENCY" in specialties)

        # Optimization Score Calculation (0 - 100)
        score = 100.0

        if available_beds == 0:
            score -= 60.0  # Major penalty for no available beds of requested type
        else:
            score += min(available_beds * 5.0, 25.0)

        if not specialty_matched:
            score -= 35.0

        # Occupancy health penalty (prefer hospitals with lower occupancy %)
        score -= (projected_occupancy_pct * 0.3)

        # Urgency adjustment
        if patient_urgency in ["CRITICAL", "HIGH"] and available_beds > 0:
            score += 15.0

        score = max(round(score, 1), 0.0)

        rationale = (
            f"Facility has {available_beds} {required_bed_type} beds available (Occupancy: {projected_occupancy_pct}%). "
            f"Specialty match: {'YES' if specialty_matched else 'PARTIAL'}. Optimization score: {score}/100."
        )

        allocations.append(
            HospitalBedAllocation(
                recommended_hospital_id=inv.hospital_id,
                recommended_hospital_name=inv.hospital_name,
                allocated_bed_type=required_bed_type,
                beds_available_before_allocation=available_beds,
                projected_occupancy_after_allocation_pct=projected_occupancy_pct,
                allocation_score=score,
                allocation_rationale=rationale
            )
        )

    # Sort allocations descending by optimization score
    allocations.sort(key=lambda a: a.allocation_score, reverse=True)
    return allocations
