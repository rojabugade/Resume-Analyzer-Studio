from resume_analyzer.models import JobMatch, JobProfile, Skill, SkillGap


class JobMatcher:
    """Score and match resume against job descriptions."""

    @staticmethod
    def match_resume_to_job(
        resume_skills: list[Skill],
        resume_experience_years: int,
        job_profile: JobProfile,
    ) -> JobMatch:
        """Calculate match score between resume and job."""
        required_list: list[Skill] = []
        if "required_skills" in job_profile:
            req = job_profile["required_skills"]
            required_list = req if isinstance(req, list) else []  # type: ignore

        required_score = JobMatcher._score_skills(resume_skills, required_list)
        experience_score = JobMatcher._score_experience(
            resume_experience_years,
            job_profile.get("required_experience_years", 0),
        )

        overall_score = required_score * 0.6 + experience_score * 0.4
        gaps = JobMatcher._identify_gaps(resume_skills, required_list)

        return {
            "job_id": job_profile.get("id", ""),
            "resume_id": "",
            "match_score": min(1.0, max(0.0, overall_score)),
            "required_match": required_score,
            "nice_to_have_match": 0.0,
            "experience_fit": experience_score,
            "gaps": gaps,
            "recommendations": JobMatcher._generate_recommendations(gaps),
            "confidence": min(0.95, overall_score + 0.1),
            "reasoning": f"Strong match on core skills ({required_score:.0%}).",
        }

    @staticmethod
    def _score_skills(resume_skills: list[Skill], required_skills: list[Skill]) -> float:
        """Score skill overlap."""
        if not required_skills:
            return 1.0
        resume_skill_names = {s.get("name", "").lower() for s in resume_skills}
        matches = sum(
            1 for s in required_skills if s.get("name", "").lower() in resume_skill_names
        )
        return float(matches / len(required_skills))

    @staticmethod
    def _score_experience(resume_years: int, required_years: int) -> float:
        """Score years of experience alignment."""
        if resume_years >= required_years:
            return 1.0
        return float(max(0.5, resume_years / max(1, required_years)))

    @staticmethod
    def _identify_gaps(resume_skills: list[Skill], required_skills: list[Skill]) -> list[SkillGap]:
        """Identify skill gaps."""
        resume_names = {s.get("name", "").lower() for s in resume_skills}
        gaps: list[SkillGap] = []
        for req_skill in required_skills:
            if req_skill.get("name", "").lower() not in resume_names:
                gaps.append({
                    "gap_type": "skill",
                    "name": req_skill.get("name", ""),
                    "importance": "required",
                    "priority": "high",
                })
        return gaps

    @staticmethod
    def _generate_recommendations(gaps: list[SkillGap]) -> list[str]:
        """Generate resume improvement recommendations."""
        recs = []
        for gap in gaps[:3]:
            recs.append(f"Add {gap['name']} to skills or projects")
        return recs
