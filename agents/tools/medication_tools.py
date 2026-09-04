from datetime import datetime, time, timedelta
import uuid
from typing import Any, Dict, List, Optional, Tuple
from agents.medication.schemas import MedicationItem, ScheduleConflict, ScheduledReminder


def parse_hhmm(time_str: str) -> time:
    """Parse HH:MM time string into datetime.time object."""
    try:
        parts = time_str.strip().split(":")
        return time(hour=int(parts[0]), minute=int(parts[1]))
    except Exception:
        return time(hour=8, minute=0)


def format_hhmm(t: time) -> str:
    """Format time object into HH:MM string."""
    return f"{t.hour:02d}:{t.minute:02d}"


def add_minutes_to_time(t: time, minutes: int) -> time:
    """Add minutes to a time object wrapping around 24 hours."""
    dt = datetime(2026, 1, 1, t.hour, t.minute) + timedelta(minutes=minutes)
    return dt.time()


def generate_deterministic_reminder_times(
    medication: MedicationItem,
    wake_time_str: str = "08:00",
    sleep_time_str: str = "22:00",
    meal_times: Optional[Dict[str, str]] = None
) -> List[ScheduledReminder]:
    """
    Deterministic Tool: Calculate exact intake reminder times (HH:MM)
    from prescribed frequency, meal relationship, and user daily schedule.
    """
    meals = meal_times or {"breakfast": "08:30", "lunch": "13:00", "dinner": "20:00"}
    bf_time = parse_hhmm(meals.get("breakfast", "08:30"))
    lunch_time = parse_hhmm(meals.get("lunch", "13:00"))
    dinner_time = parse_hhmm(meals.get("dinner", "20:00"))

    freq_lower = medication.prescribed_frequency.lower()
    meal_rel = (medication.meal_relationship or "AFTER_MEAL").upper()

    times: List[Tuple[time, str]] = []

    # Frequency breakdown
    if "once" in freq_lower or "1" in freq_lower or "24 hours" in freq_lower:
        base_t = bf_time
        note = "Take after breakfast"
        if "before" in meal_rel:
            base_t = add_minutes_to_time(bf_time, -30)
            note = "Take 30 mins before breakfast"
        elif "after" in meal_rel:
            base_t = add_minutes_to_time(bf_time, 30)
            note = "Take 30 mins after breakfast"
        times.append((base_t, note))

    elif "twice" in freq_lower or "2" in freq_lower or "12 hours" in freq_lower:
        t1 = add_minutes_to_time(bf_time, 30 if "after" in meal_rel.lower() else 0)
        t2 = add_minutes_to_time(dinner_time, 30 if "after" in meal_rel.lower() else 0)
        times.append((t1, "Morning intake (after breakfast)" if "after" in meal_rel.lower() else "Morning intake"))
        times.append((t2, "Evening intake (after dinner)" if "after" in meal_rel.lower() else "Evening intake"))

    elif "three" in freq_lower or "3" in freq_lower or "8 hours" in freq_lower:
        t1 = add_minutes_to_time(bf_time, 30)
        t2 = add_minutes_to_time(lunch_time, 30)
        t3 = add_minutes_to_time(dinner_time, 30)
        times.append((t1, "Morning intake (after breakfast)"))
        times.append((t2, "Afternoon intake (after lunch)"))
        times.append((t3, "Night intake (after dinner)"))

    elif "four" in freq_lower or "4" in freq_lower or "6 hours" in freq_lower:
        times.append((parse_hhmm("08:30"), "Morning intake"))
        times.append((parse_hhmm("13:00"), "Afternoon intake"))
        times.append((parse_hhmm("17:30"), "Evening intake"))
        times.append((parse_hhmm("21:30"), "Night intake"))

    else:
        # Default fallback: twice daily
        times.append((add_minutes_to_time(bf_time, 30), "Morning intake"))
        times.append((add_minutes_to_time(dinner_time, 30), "Evening intake"))

    reminders: List[ScheduledReminder] = []
    for t_obj, note in times:
        rem_id = f"REM-{uuid.uuid4().hex[:6].upper()}"
        reminders.append(
            ScheduledReminder(
                reminder_id=rem_id,
                medication_name=medication.medication_name,
                dosage=medication.prescribed_dosage,
                scheduled_time=format_hhmm(t_obj),
                meal_relation_note=note,
                instructions=f"Take {medication.prescribed_dosage} of {medication.medication_name}. {note}."
            )
        )

    return reminders


def detect_medication_schedule_conflicts(
    scheduled_reminders: List[ScheduledReminder],
    wake_time_str: str = "08:00",
    sleep_time_str: str = "22:00"
) -> List[ScheduleConflict]:
    """
    Deterministic Tool: Inspect scheduled reminder times for overlaps or timing conflicts.
    """
    conflicts: List[ScheduleConflict] = []
    wake_t = parse_hhmm(wake_time_str)
    sleep_t = parse_hhmm(sleep_time_str)

    # Sort reminders by scheduled_time
    sorted_rems = sorted(scheduled_reminders, key=lambda r: r.scheduled_time)

    for i in range(len(sorted_rems)):
        rem1 = sorted_rems[i]
        t1 = parse_hhmm(rem1.scheduled_time)

        # 1. Check if reminder falls outside active wake hours
        if sleep_t > wake_t:
            outside_wake = not (wake_t <= t1 <= sleep_t)
        else:
            outside_wake = (sleep_t < t1 < wake_t)

        if outside_wake:
            conflicts.append(
                ScheduleConflict(
                    conflict_type="OUTSIDE_WAKE_HOURS",
                    medication_a=rem1.medication_name,
                    description=f"Reminder for {rem1.medication_name} at {rem1.scheduled_time} falls during sleep hours ({sleep_time_str} - {wake_time_str}).",
                    resolution_recommendation=f"Adjust {rem1.medication_name} reminder to active wake hours."
                )
            )

        # 2. Check for close timing overlaps (< 15 mins) between different medications
        for j in range(i + 1, len(sorted_rems)):
            rem2 = sorted_rems[j]
            if rem1.medication_name.lower() == rem2.medication_name.lower():
                continue

            t2 = parse_hhmm(rem2.scheduled_time)
            dt_mins = abs((t2.hour * 60 + t2.minute) - (t1.hour * 60 + t1.minute))

            if dt_mins < 15:
                conflicts.append(
                    ScheduleConflict(
                        conflict_type="CLOSE_TIMING",
                        medication_a=rem1.medication_name,
                        medication_b=rem2.medication_name,
                        description=f"{rem1.medication_name} ({rem1.scheduled_time}) and {rem2.medication_name} ({rem2.scheduled_time}) are scheduled within {dt_mins} mins.",
                        resolution_recommendation=f"Space intake of {rem1.medication_name} and {rem2.medication_name} at least 30 minutes apart."
                    )
                )

    return conflicts
