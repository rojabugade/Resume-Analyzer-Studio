from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class CaseMetrics:
    parse_f1: float
    job_match_quality: float
    missing_skill_f1: float
    recommendation_usefulness: float
    hallucination_rate: float
    latency_ms: float
    task_completion_success: float


def f1_from_sets(predicted: set[str], expected: set[str]) -> float:
    if not predicted and not expected:
        return 1.0
    if not predicted or not expected:
        return 0.0
    tp = len(predicted.intersection(expected))
    precision = tp / len(predicted)
    recall = tp / len(expected)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def reciprocal_rank(ranked_ids: list[str], relevant_ids: set[str]) -> float:
    if not relevant_ids:
        return 1.0
    for idx, item in enumerate(ranked_ids, start=1):
        if item in relevant_ids:
            return 1.0 / idx
    return 0.0


def hallucination_rate(recommendations: list[str], support_corpus: str) -> float:
    if not recommendations:
        return 0.0
    support = support_corpus.lower()
    total_claims = 0
    unsupported_claims = 0

    for rec in recommendations:
        # Evaluate claims in imperative suggestions like "Add Kubernetes..."
        matches = re.findall(r"(?:add|include|highlight)\s+([a-zA-Z0-9+# .-]{2,40})", rec.lower())
        for claim in matches:
            total_claims += 1
            claim_text = claim.strip()
            claim_tokens = [t for t in re.findall(r"[a-zA-Z0-9+#.-]+", claim_text) if len(t) > 2]
            is_supported = any(token in support for token in claim_tokens)
            if claim_text and not is_supported:
                unsupported_claims += 1

    if total_claims == 0:
        return 0.0
    return unsupported_claims / total_claims
