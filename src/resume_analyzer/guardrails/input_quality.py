from __future__ import annotations


def assess_resume_quality(profile: dict, resume_text: str) -> dict[str, object]:
    skills = profile.get("skills", [])
    experience = profile.get("experience", [])
    has_summary = bool(profile.get("summary", "").strip())

    flags: list[str] = []
    if len(resume_text.strip()) < 120:
        flags.append("resume_too_short")
    if not skills:
        flags.append("missing_skills_section")
    if not experience:
        flags.append("missing_experience_section")
    if not has_summary:
        flags.append("missing_summary")

    score = max(0.0, 1.0 - (0.2 * len(flags)))
    return {
        "quality_score": score,
        "flags": flags,
        "is_incomplete": len(flags) > 0,
    }


def assess_job_description_quality(job: dict) -> dict[str, object]:
    description = str(job.get("raw_description", ""))
    required = job.get("required_skills", [])

    flags: list[str] = []
    if len(description.strip()) < 80:
        flags.append("job_description_too_short")
    if not required:
        flags.append("missing_required_skills")

    score = max(0.0, 1.0 - (0.35 * len(flags)))
    return {
        "quality_score": score,
        "flags": flags,
        "is_low_quality": len(flags) > 0,
    }
