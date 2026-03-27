CONFIDENCE_THRESHOLDS = {
    "match_recommendation": 0.70,
    "skill_gap_critical": 0.50,
    "ats_optimization": 0.60,
}

MAX_CONFIDENCE_ADJUSTMENTS = {
    "fairness_issue": -0.10,
    "low_data_quality": -0.15,
    "conflicting_signals": -0.05,
}


def should_flag_for_review(confidence: float, decision_type: str) -> bool:
    """Check if decision should be escalated to human review."""
    threshold = CONFIDENCE_THRESHOLDS.get(decision_type, 0.75)
    return confidence < threshold


def apply_confidence_adjustments(base_confidence: float, factors: dict) -> float:
    """Apply adjustments to confidence score."""
    adjusted = base_confidence
    for penalty in factors.values():
        adjusted += penalty
    return min(1.0, max(0.0, adjusted))
