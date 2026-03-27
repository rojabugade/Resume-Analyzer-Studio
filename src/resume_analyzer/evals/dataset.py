from __future__ import annotations

from typing import TypedDict

from resume_analyzer.models import JobProfile


class EvalExpectation(TypedDict, total=False):
    expected_title_contains: str
    expected_skills: list[str]
    expected_top_job_id: str | None
    expected_relevant_jobs: list[str]
    expected_missing_skills: list[str]
    min_match_score: float
    max_match_score: float
    min_ats_score: float
    expect_completion: bool


class EvalCase(TypedDict, total=False):
    case_id: str
    scenario: str
    description: str
    user_id: str
    query: str
    resume_text: str
    job_overrides: list[JobProfile]
    expectation: EvalExpectation


EVAL_CASES: list[EvalCase] = [
    {
        "case_id": "C01_strong_backend_match",
        "scenario": "strong match",
        "description": "Backend-heavy resume should strongly match Senior Software Engineer role.",
        "user_id": "eval_user_01",
        "query": "Match my resume to backend roles",
        "resume_text": (
            "Senior Backend Engineer\n"
            "Professional Summary: Built Python APIs on AWS for 6 years.\n"
            "Skills: Python, AWS, Docker, SQL, FastAPI\n"
            "Experience: Led backend modernization."
        ),
        "expectation": {
            "expected_title_contains": "Backend",
            "expected_skills": ["python", "aws", "docker", "sql"],
            "expected_top_job_id": "job_001",
            "expected_relevant_jobs": ["job_001"],
            "expected_missing_skills": [],
            "min_match_score": 0.75,
            "expect_completion": True,
        },
    },
    {
        "case_id": "C02_weak_frontend_match",
        "scenario": "weak match",
        "description": "Frontend profile should weakly match available backend and ML jobs.",
        "user_id": "eval_user_02",
        "query": "Find matches",
        "resume_text": (
            "Frontend Engineer\n"
            "Summary: 4 years in React and CSS architecture.\n"
            "Skills: React, TypeScript, CSS, Figma\n"
            "Experience: Built design systems."
        ),
        "expectation": {
            "expected_skills": ["react", "typescript", "css", "figma"],
            "max_match_score": 0.55,
            "expect_completion": True,
        },
    },
    {
        "case_id": "C03_missing_ml_skill",
        "scenario": "missing skills",
        "description": (
            "General python candidate should show ML-specific "
            "missing skills for ML role."
        ),
        "user_id": "eval_user_03",
        "query": "Optimize resume for machine learning jobs",
        "resume_text": (
            "Software Engineer\n"
            "Summary: Built data pipelines in Python.\n"
            "Skills: Python, AWS, SQL\n"
            "Experience: 3 years in analytics engineering."
        ),
        "expectation": {
            "expected_top_job_id": "job_002",
            "expected_relevant_jobs": ["job_002"],
            "expected_missing_skills": ["machine learning"],
            "expect_completion": True,
        },
    },
    {
        "case_id": "C04_incomplete_resume",
        "scenario": "incomplete resume",
        "description": (
            "Sparse resume should still complete task with lower "
            "confidence and useful guidance."
        ),
        "user_id": "eval_user_04",
        "query": "Analyze and match",
        "resume_text": "Student\nSkills: Python",
        "expectation": {
            "expected_skills": ["python"],
            "max_match_score": 0.65,
            "expect_completion": True,
        },
    },
    {
        "case_id": "C05_ambiguous_job_description",
        "scenario": "ambiguous job description",
        "description": "Ambiguous role text should avoid overconfident match scores.",
        "user_id": "eval_user_05",
        "query": "Find matching jobs for this profile",
        "resume_text": (
            "Platform Engineer\n"
            "Summary: Works across cloud and data tools.\n"
            "Skills: Python, SQL, Docker\n"
            "Experience: Built internal platforms."
        ),
        "job_overrides": [
            {
                "id": "job_ambiguous_001",
                "title": "AI/Platform/Innovation Engineer",
                "company": "AmbiguousCorp",
                "raw_description": "Need someone technical, adaptable, and collaborative.",
                "required_skills": [{"name": "Python", "proficiency": "intermediate"}],
                "required_experience_years": 2,
            }
        ],
        "expectation": {
            "expected_relevant_jobs": ["job_ambiguous_001"],
            "max_match_score": 0.90,
            "expect_completion": True,
        },
    },
    {
        "case_id": "C06_ats_keyword_mismatch",
        "scenario": "ATS keyword mismatch",
        "description": (
            "High-level resume without concrete keywords should "
            "have reduced ATS quality."
        ),
        "user_id": "eval_user_06",
        "query": "Analyze resume quality",
        "resume_text": (
            "Engineering Leader\n"
            "Summary: Led many initiatives with strong outcomes.\n"
            "Experience: Managed teams and strategy."
        ),
        "expectation": {
            "min_ats_score": 30.0,
            "expect_completion": True,
        },
    },
    {
        "case_id": "C07_ml_strong_match",
        "scenario": "strong match",
        "description": "ML profile should rank machine learning role first.",
        "user_id": "eval_user_07",
        "query": "Match me to ML jobs",
        "resume_text": (
            "Machine Learning Engineer\n"
            "Summary: Built recommendation models in PyTorch.\n"
            "Skills: Python, machine learning, SQL, PyTorch\n"
            "Experience: 4 years in ML engineering."
        ),
        "expectation": {
            "expected_top_job_id": "job_002",
            "expected_relevant_jobs": ["job_002"],
            "min_match_score": 0.75,
            "expect_completion": True,
        },
    },
    {
        "case_id": "C08_missing_sql_gap",
        "scenario": "missing skills",
        "description": "Candidate lacking SQL should get SQL as explicit skill gap for ML role.",
        "user_id": "eval_user_08",
        "query": "Recommend improvements for ML jobs",
        "resume_text": (
            "ML Engineer\n"
            "Summary: Works on model training and serving.\n"
            "Skills: Python, machine learning, Docker\n"
            "Experience: Built production inference services."
        ),
        "expectation": {
            "expected_missing_skills": ["SQL"],
            "expect_completion": True,
        },
    },
    {
        "case_id": "C09_noisy_resume_format",
        "scenario": "parsing robustness",
        "description": "Noisy punctuation should still parse key skills.",
        "user_id": "eval_user_09",
        "query": "Analyze resume",
        "resume_text": (
            "Principal Engineer!!!\n"
            "Skills:: Python | AWS | Docker | SQL\n"
            "Professional Summary: APIs, cloud, reliability." 
        ),
        "expectation": {
            "expected_skills": ["python", "aws", "docker", "sql"],
            "expect_completion": True,
        },
    },
    {
        "case_id": "C10_conflicting_profile",
        "scenario": "weak match",
        "description": "Conflicting narrative should keep confidence moderate.",
        "user_id": "eval_user_10",
        "query": "Find best job",
        "resume_text": (
            "Data Scientist and Frontend Artist\n"
            "Summary: Equal focus on visual design and deep learning.\n"
            "Skills: Figma, React, Python\n"
            "Experience: Worked across marketing and analytics."
        ),
        "expectation": {
            "max_match_score": 0.70,
            "expect_completion": True,
        },
    },
    {
        "case_id": "C11_empty_project_history",
        "scenario": "incomplete resume",
        "description": "Resume without projects should still complete with useful recommendations.",
        "user_id": "eval_user_11",
        "query": "Optimize for software engineer jobs",
        "resume_text": (
            "Software Engineer\n"
            "Skills: Python, AWS\n"
            "Experience: Worked at startup."
        ),
        "expectation": {
            "expected_relevant_jobs": ["job_001"],
            "expect_completion": True,
        },
    },
    {
        "case_id": "C12_keyword_stuffing",
        "scenario": "ATS keyword mismatch",
        "description": "Keyword-stuffed resume should not produce artificially high confidence.",
        "user_id": "eval_user_12",
        "query": "Analyze and match",
        "resume_text": (
            "Engineer\n"
            "Skills: leadership leadership leadership project project metric impact driven\n"
            "Summary: leadership project achievement metric driven impact."
        ),
        "expectation": {
            "max_match_score": 0.65,
            "expect_completion": True,
        },
    },
]
