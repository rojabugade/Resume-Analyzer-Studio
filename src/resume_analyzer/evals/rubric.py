from __future__ import annotations

import re


def usefulness_rubric_score(
    recommendations: list[str],
    expected_missing_skills: list[str],
) -> tuple[float, dict[str, float]]:
    """Return a normalized 0-1 usefulness score and component breakdown."""

    if not recommendations:
        return 0.0, {
            "actionability": 0.0,
            "specificity": 0.0,
            "coverage": 0.0,
            "clarity": 0.0,
            "safety": 0.0,
        }

    joined = " ".join(recommendations).lower()
    actionable_terms = ["add", "highlight", "quantify", "include", "demonstrate"]
    actionability = 1.0 if any(term in joined for term in actionable_terms) else 0.5

    # Specificity increases when recommendations mention concrete terms rather than generic advice.
    token_count = len(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{2,}", joined))
    specificity = min(1.0, token_count / 25.0)

    expected = {item.lower() for item in expected_missing_skills}
    if expected:
        coverage_hits = sum(1 for item in expected if item in joined)
        coverage = coverage_hits / len(expected)
    else:
        coverage = 1.0

    avg_len = sum(len(item.split()) for item in recommendations) / max(1, len(recommendations))
    clarity = 1.0 if 4 <= avg_len <= 18 else 0.6

    unsafe_terms = ["guaranteed", "perfect", "always hired", "certainly selected"]
    safety = 0.0 if any(term in joined for term in unsafe_terms) else 1.0

    components = {
        "actionability": actionability,
        "specificity": specificity,
        "coverage": coverage,
        "clarity": clarity,
        "safety": safety,
    }
    total = sum(components.values()) / len(components)
    return total, components
