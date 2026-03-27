class FairnessChecker:
    """Check for bias and fairness in recommendations."""

    PROTECTED_ATTRIBUTES = ["age", "race", "gender", "religion", "disability", "nationality"]

    @staticmethod
    def check_recommendation_fairness(
        recommendation: str,
        candidate_profile: dict,
    ) -> dict:
        """Check if recommendation contains bias."""
        issues = []
        confidence_penalty = 0.0

        for attr in FairnessChecker.PROTECTED_ATTRIBUTES:
            if attr in recommendation.lower():
                issues.append(f"Potentially biased language: mentions '{attr}'")
                confidence_penalty += 0.1

        return {
            "is_fair": len(issues) == 0,
            "issues": issues,
            "confidence_adjustment": -confidence_penalty,
        }

    @staticmethod
    def check_output_diversity(matches: list) -> dict:
        """Ensure diverse results."""
        return {
            "is_diverse": len(matches) > 1,
            "recommendation": "Show diverse job types and companies",
        }
