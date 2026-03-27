import re

from resume_analyzer.models import ResumeProfile, Skill


class ResumeParser:
    @staticmethod
    def parse_text(text: str) -> ResumeProfile:
        """Parse resume text and extract structured data."""
        profile: ResumeProfile = {
            "id": "",
            "user_id": "",
            "title": ResumeParser._extract_title(text),
            "summary": ResumeParser._extract_summary(text),
            "skills": ResumeParser._extract_skills(text),
            "experience": ResumeParser._extract_experience(text),
            "education": ResumeParser._extract_education(text),
            "projects": ResumeParser._extract_projects(text),
            "ats_score": 0.0,
            "extracted_keywords": [],
            "created_at": "",
            "updated_at": "",
            "parsed_text": text,
        }
        return profile

    @staticmethod
    def _extract_title(text: str) -> str:
        """Extract job title from resume."""
        lines = text.split("\n")[:5]
        for line in lines:
            if len(line.strip()) > 3 and len(line.strip()) < 100:
                return line.strip()
        return "Unknown"

    @staticmethod
    def _extract_summary(text: str) -> str:
        """Extract summary/objective from resume."""
        patterns = [
            (
                r"(?is)(professional summary|objective|about me)\s*:?(.*?)"
                r"(?=\n\s*(experience|skills|education|projects)\s*:|\Z)"
            )
        ]
        match = re.search(patterns[0], text, re.DOTALL)
        return match.group(2).strip() if match else ""

    @staticmethod
    def _extract_skills(text: str) -> list[Skill]:
        """Extract skills from resume text."""
        patterns = [
            (
                r"(?is)(?:skills?|technical skills?|competencies?)\s*:?(.*?)"
                r"(?=\n\s*(experience|education|projects)\s*:|\Z)"
            )
        ]
        match = re.search(patterns[0], text, re.DOTALL)
        if not match:
            return []

        skills_section = match.group(1)
        skills_text = re.split(r"[,|•\n]", skills_section)
        skills: list[Skill] = []
        for skill_text in skills_text:
            clean = skill_text.strip()
            if len(clean) > 2:
                skills.append({"name": clean, "proficiency": "intermediate"})
        return skills

    @staticmethod
    def _extract_experience(text: str) -> list:
        """Extract work experience from resume."""
        return []  # Stub for now

    @staticmethod
    def _extract_education(text: str) -> list:
        """Extract education from resume."""
        return []  # Stub for now

    @staticmethod
    def _extract_projects(text: str) -> list:
        """Extract projects from resume."""
        return []  # Stub for now
