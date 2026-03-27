

class ATSScorer:
    """Score resume for ATS (Applicant Tracking System) compatibility."""

    KEYWORDS_WEIGHT = {
        "leadership": 2,
        "project": 2,
        "achievement": 2,
        "impact": 1,
        "metric": 1,
        "driven": 1,
    }

    @staticmethod
    def score_ats(resume_text: str) -> dict:
        """Calculate ATS score 0-100."""
        score = 100.0
        checks: dict[str, object] = {}

        checks["has_contact"] = ATSScorer._check_contact(resume_text)
        if not checks["has_contact"]:
            score -= 15.0

        keyword_score = ATSScorer._score_keywords(resume_text)
        checks["keyword_density"] = keyword_score
        score -= (5.0 - keyword_score)

        checks["formatting"] = ATSScorer._check_formatting(resume_text)
        if not checks["formatting"]:
            score -= 10.0

        return {
            "ats_score": min(100.0, max(0.0, score)),
            "checks": checks,
        }

    @staticmethod
    def _check_contact(text: str) -> bool:
        """Check if resume has contact info."""
        return "@" in text and any(c in text for c in ["phone", "linkedin", "github"])

    @staticmethod
    def _score_keywords(text: str) -> float:
        """Score keyword presence."""
        text_lower = text.lower()
        count = sum(text_lower.count(kw) for kw in ATSScorer.KEYWORDS_WEIGHT)
        return float(min(5, count // 2))

    @staticmethod
    def _check_formatting(text: str) -> bool:
        """Check basic formatting."""
        return len(text) > 200 and "\n" in text
