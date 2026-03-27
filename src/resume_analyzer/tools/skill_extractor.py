from resume_analyzer.models import Skill


class SkillExtractor:
    """Extract and normalize skills to canonical taxonomy."""

    SKILLS_TAXONOMY = {
        "python": ["python", "py"],
        "javascript": ["javascript", "js", "node", "node.js"],
        "aws": ["aws", "amazon web services", "ec2", "s3", "dynamodb"],
        "kubernetes": ["kubernetes", "k8s"],
        "docker": ["docker", "containers"],
        "sql": ["sql", "postgres", "postgresql", "mysql", "oracle"],
        "machine learning": ["ml", "machine learning", "deep learning", "tensorflow", "pytorch"],
        "leadership": ["leadership", "team lead", "manager", "director"],
        "project management": ["project management", "agile", "scrum"],
    }

    @staticmethod
    def extract_and_normalize(skill_mentions: list[str]) -> list[Skill]:
        """Normalize raw skill mentions to canonical skills."""
        normalized: dict[str, Skill] = {}
        for mention in skill_mentions:
            canonical = SkillExtractor._find_canonical(mention)
            if canonical:
                if canonical not in normalized:
                    normalized[canonical] = {
                        "name": canonical,
                        "proficiency": "intermediate",
                    }
        return list(normalized.values())

    @staticmethod
    def _find_canonical(mention: str) -> str | None:
        """Map skill mention to canonical taxonomy."""
        mention_lower = mention.lower().strip()
        for canonical, aliases in SkillExtractor.SKILLS_TAXONOMY.items():
            if mention_lower in aliases or any(alias in mention_lower for alias in aliases):
                return canonical
        if len(mention_lower) > 2:
            return mention_lower
        return None
