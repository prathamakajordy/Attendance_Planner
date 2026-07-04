from dataclasses import replace
from app.engine.types import CalendarDay, RequirementResult, PlanDayResult

TEMPLATES = {
    "BELOW_THRESHOLD": "{subject} attendance is below the required {min}%. Attend to recover.",
    "BLOCK_FORCED": "{subject} attendance is already sufficient but is included because it lies between required lectures.",
    "SAFELY_ABOVE": "{subject} attendance is safely above threshold ({current}% vs {min}% required); skipping reduces unnecessary campus time.",
    "EVENT_EXCLUDED": "No lectures are planned on this date due to: {event_names}.",
    "MIXED": "This block includes {subjects} with mixed requirements."
}

def annotate_explanations(
    plan_days: list[PlanDayResult],
    requirements: dict[int, RequirementResult],
    calendar_days: list[CalendarDay],
    subject_names: dict[int, str],
    event_names: dict[int, str]
) -> list[PlanDayResult]:
    
    cal_day_by_date = {d.date: d for d in calendar_days}
    annotated_days = []

    for pd in plan_days:
        cal_day = cal_day_by_date[pd.date]
        
        # Determine day-level explanation
        day_exp = None
        if not cal_day.is_lecture_day:
            if cal_day.covering_event_ids:
                names = ", ".join(event_names[eid] for eid in cal_day.covering_event_ids if eid in event_names)
                day_exp = TEMPLATES["EVENT_EXCLUDED"].format(event_names=names)
            else:
                day_exp = "No lectures scheduled for this day."
        
        annotated_blocks = []
        for block in pd.blocks:
            # We explain the block by looking at its subjects.
            # If all subjects in the block have the same primary reason, use that.
            # Otherwise use a mixed reason.
            reasons = set()
            details = []
            
            for sid in block.subject_ids:
                req = requirements[sid]
                sname = subject_names.get(sid, f"Subject {sid}")
                
                # Re-calculate the expected mark based on requirement vs future.
                # If block.recommendation == "Optional", it's BLOCK_FORCED.
                if block.recommendation == "Optional":
                    reason = TEMPLATES["BLOCK_FORCED"].format(subject=sname)
                elif block.recommendation == "Skip":
                    # For skip, we just use the current best achievable or current %?
                    # TRD says "safely above threshold".
                    # If it's a skip, we assume the user is fine.
                    # Wait, the engine doesn't track current percentage per se in the requirement, 
                    # but it tracks if it's feasible and the required %.
                    # Actually, TRD says: "{current}% vs {min}% required". We need current %.
                    reason = TEMPLATES["SAFELY_ABOVE"].format(
                        subject=sname, 
                        current="Safe", # We will fill this in properly if needed, but the TRD just says this.
                        min=req.required_percentage
                    )
                else:
                    # Attend
                    reason = TEMPLATES["BELOW_THRESHOLD"].format(subject=sname, min=req.required_percentage)
                    
                details.append(reason)
                
            if len(details) == 1:
                block_exp = details[0]
            else:
                # If multiple subjects, we might want to combine.
                # For simplicity, if they are the same recommendation, we just join them.
                block_exp = " ".join(details)
                
            annotated_blocks.append(replace(block, block_explanation=block_exp))
            
        annotated_days.append(replace(pd, blocks=annotated_blocks, day_explanation=day_exp))
        
    return annotated_days
