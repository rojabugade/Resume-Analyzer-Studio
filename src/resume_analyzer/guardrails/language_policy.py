from __future__ import annotations


class LanguagePolicyGuardrails:
    """Enforce safe language for career guidance outputs."""

    GUARANTEE_PHRASES = [
        "guaranteed interview",
        "guaranteed job",
        "certain offer",
        "100 percent chance",
        "will definitely get hired",
    ]

    SENSITIVE_ADVICE_PHRASES = [
        "immigration status",
        "visa strategy",
        "legal advice",
        "medical condition",
        "financial guarantee",
    ]

    @staticmethod
    def sanitize_recommendations(recommendations: list[str]) -> dict[str, object]:
        sanitized: list[str] = []
        blocked: list[str] = []

        for rec in recommendations:
            updated = rec
            lower = rec.lower()

            for phrase in LanguagePolicyGuardrails.GUARANTEE_PHRASES:
                if phrase in lower:
                    blocked.append(phrase)
                    updated = updated.replace(
                        phrase,
                        "may improve your chances",
                    )

            for phrase in LanguagePolicyGuardrails.SENSITIVE_ADVICE_PHRASES:
                if phrase in lower:
                    blocked.append(phrase)
                    updated = (
                        "I cannot provide definitive legal, medical, or financial advice. "
                        "Please consult a qualified professional for that topic."
                    )
                    break

            sanitized.append(updated)

        return {
            "sanitized": sanitized,
            "blocked_phrases": sorted(set(blocked)),
            "policy_violations": len(blocked),
        }
