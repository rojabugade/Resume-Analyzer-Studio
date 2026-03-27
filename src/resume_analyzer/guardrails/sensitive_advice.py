from __future__ import annotations


def detect_sensitive_career_advice(recommendations: list[str]) -> dict[str, object]:
    sensitive_terms = [
        "immigration",
        "visa",
        "legal",
        "medical",
        "financial",
        "tax",
    ]
    joined = " ".join(recommendations).lower()
    hits = [term for term in sensitive_terms if term in joined]
    return {
        "is_sensitive": len(hits) > 0,
        "hits": hits,
    }
