from __future__ import annotations


def low_confidence_fallback(reason: str) -> list[str]:
    templates = {
        "incomplete_resume": (
            "I cannot provide high-confidence matching yet. "
            "Please add recent projects, measurable outcomes, and a fuller skills section."
        ),
        "low_quality_job_description": (
            "This job description is too vague for reliable matching. "
            "Please provide required skills, responsibilities, and expected seniority."
        ),
        "unsupported_claims": (
            "I removed unsupported recommendations. "
            "Please share more resume detail so I can provide evidence-backed guidance."
        ),
        "general_low_confidence": (
            "I need more detail to provide reliable recommendations. "
            "Share your recent role scope, projects, and metrics for a stronger match."
        ),
    }
    return [templates.get(reason, templates["general_low_confidence"])]
