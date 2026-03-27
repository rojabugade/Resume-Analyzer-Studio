from resume_analyzer.tools.resume_parser import ResumeParser
from resume_analyzer.tools.skill_extractor import SkillExtractor


def test_resume_parser() -> None:
    """Test resume text parsing."""
    resume_text = "Senior Software Engineer\n\nSkills: Python, JavaScript, AWS\n\nExperience: 5 years at TechCorp"
    profile = ResumeParser.parse_text(resume_text)
    assert "Senior" in profile.get("title", "")
    assert len(profile.get("skills", [])) > 0


def test_skill_extraction() -> None:
    """Test skill normalization."""
    skills = ["Python", "python3", "python 3.11", "AWS EC2", "aws", "Kubernetes", "k8s"]
    normalized = SkillExtractor.extract_and_normalize(skills)
    names = [s.get("name", "") for s in normalized]
    # Should collapse variants to canonical forms
    assert len(names) <= len(skills)
    assert any("python" in n.lower() for n in names)
    assert any("aws" in n.lower() for n in names)
