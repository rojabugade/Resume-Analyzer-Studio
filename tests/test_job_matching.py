from resume_analyzer.models import JobProfile
from resume_analyzer.tools.job_matcher import JobMatcher


def test_job_matching_scoring() -> None:
    """Test job matching score calculation."""
    resume_skills = [
        {"name": "Python", "proficiency": "expert"},
        {"name": "AWS", "proficiency": "intermediate"},
    ]
    required_skills = [
        {"name": "Python", "proficiency": "intermediate"},
        {"name": "AWS", "proficiency": "intermediate"},
    ]
    job: JobProfile = {
        "id": "job_test",
        "title": "Senior Engineer",
        "required_skills": required_skills,
        "required_experience_years": 5,
    }

    match = JobMatcher.match_resume_to_job(
        resume_skills=resume_skills,
        resume_experience_years=5,
        job_profile=job,
    )

    assert match.get("match_score", 0) > 0.7
    assert match.get("required_match", 0) == 1.0


def test_skill_gap_identification() -> None:
    """Test skill gap detection."""
    resume_skills = [{"name": "Python", "proficiency": "expert"}]
    required_skills = [
        {"name": "Python", "proficiency": "intermediate"},
        {"name": "Kubernetes", "proficiency": "intermediate"},
        {"name": "ML", "proficiency": "beginner"},
    ]
    job: JobProfile = {
        "id": "job_test",
        "title": "ML Engineer",
        "required_skills": required_skills,
        "required_experience_years": 3,
    }

    match = JobMatcher.match_resume_to_job(
        resume_skills=resume_skills,
        resume_experience_years=3,
        job_profile=job,
    )

    gaps = match.get("gaps", [])
    assert len(gaps) == 2  # Kubernetes and ML are missing
    assert any(g["name"] == "Kubernetes" for g in gaps)
