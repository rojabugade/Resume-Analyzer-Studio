from typing import TypedDict


class Skill(TypedDict, total=False):
    name: str
    proficiency: str  # "beginner", "intermediate", "expert"
    years: float
    last_used: str | None


class Experience(TypedDict, total=False):
    company: str
    role: str
    start_date: str
    end_date: str | None
    duration_months: int
    responsibilities: list[str]


class Education(TypedDict, total=False):
    school: str
    degree: str
    field: str
    graduation_year: int


class Project(TypedDict, total=False):
    title: str
    description: str
    skills_used: list[str]
    url: str | None


class ResumeProfile(TypedDict, total=False):
    id: str
    user_id: str
    title: str
    summary: str
    skills: list[Skill]
    experience: list[Experience]
    education: list[Education]
    projects: list[Project]
    ats_score: float
    extracted_keywords: list[str]
    created_at: str
    updated_at: str
    parsed_text: str


class JobProfile(TypedDict, total=False):
    id: str
    title: str
    company: str
    raw_description: str
    required_skills: list[Skill]
    nice_to_have_skills: list[str]
    required_experience_years: int
    location: str
    salary_min: float | None
    salary_max: float | None
    source: str  # "api", "web_scrape", "import"
    posted_at: str


class SkillGap(TypedDict, total=False):
    gap_type: str  # "skill", "experience", "education"
    name: str
    importance: str  # "required", "nice_to_have"
    priority: str  # "high", "medium", "low"


class JobMatch(TypedDict, total=False):
    job_id: str
    resume_id: str
    match_score: float  # 0-1
    required_match: float  # How well required skills match
    nice_to_have_match: float  # Nice-to-have alignment
    experience_fit: float  # Years of experience alignment
    education_fit: float  # Education fit
    gaps: list[SkillGap]
    recommendations: list[str]
    confidence: float
    reasoning: str
