from resume_analyzer.models import JobProfile


class JobKnowledgeBase:
    """In-memory job and skills knowledge base."""

    def __init__(self) -> None:
        self._jobs: dict[str, JobProfile] = {}
        self._skills_index: dict[str, list[str]] = {}

    def add_job(self, job: JobProfile) -> None:
        """Add job to knowledge base."""
        job_id_val = job.get("id", f"job_{len(self._jobs)}")
        job["id"] = job_id_val  # type: ignore
        self._jobs[job_id_val] = job

    def search_jobs(self, query: str, limit: int = 5) -> list[JobProfile]:
        """Search jobs by title or keywords."""
        query_lower = query.lower()
        matches = []
        for job in self._jobs.values():
            if query_lower in job.get("title", "").lower() or query_lower in job.get(
                "raw_description", ""
            ).lower():
                matches.append(job)
        return matches[:limit]

    def get_similar_jobs(self, job_id: str, limit: int = 5) -> list[JobProfile]:
        """Get similar jobs (stub for now)."""
        if job_id in self._jobs:
            return list(self._jobs.values())[:limit]
        return []


knowledge_base = JobKnowledgeBase()

# Seed with sample jobs
SAMPLE_JOBS = [
    {
        "id": "job_001",
        "title": "Senior Software Engineer",
        "company": "TechCorp",
        "raw_description": "We are looking for an experienced software engineer...",
        "required_skills": [
            {"name": "Python", "proficiency": "intermediate"},
            {"name": "AWS", "proficiency": "intermediate"},
        ],
        "required_experience_years": 5,
    },
    {
        "id": "job_002",
        "title": "Machine Learning Engineer",
        "company": "DataAI",
        "raw_description": "Join our ML team to build next-gen AI systems...",
        "required_skills": [
            {"name": "Python", "proficiency": "expert"},
            {"name": "machine learning", "proficiency": "expert"},
            {"name": "SQL", "proficiency": "intermediate"},
        ],
        "required_experience_years": 3,
    },
]

for job in SAMPLE_JOBS:
    knowledge_base.add_job(job)  # type: ignore
