from resume_analyzer.models import Skill


class SimilarityScorer:
    """Simple lexical similarity fallback used alongside vector relevance."""

    @staticmethod
    def score_skill_overlap(resume_skills: list[Skill], job_skill_names: list[str]) -> float:
        if not job_skill_names:
            return 1.0
        resume = {s.get("name", "").lower() for s in resume_skills}
        job = {skill.lower() for skill in job_skill_names}
        return float(len(resume.intersection(job)) / max(1, len(job)))
