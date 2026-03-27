from __future__ import annotations

import re


class GroundingGuardrails:
    """Validate recommendation claims against available evidence."""

    @staticmethod
    def extract_claims(recommendations: list[str]) -> list[str]:
        claims: list[str] = []
        for rec in recommendations:
            matches = re.findall(
                r"(?:add|include|highlight|quantify|demonstrate)\s+([a-zA-Z0-9+# .-]{2,40})",
                rec.lower(),
            )
            claims.extend(match.strip() for match in matches if match.strip())
        return claims

    @staticmethod
    def validate_supported_claims(
        recommendations: list[str],
        support_corpus: str,
    ) -> dict[str, object]:
        claims = GroundingGuardrails.extract_claims(recommendations)
        support = support_corpus.lower()
        unsupported: list[str] = []

        for claim in claims:
            claim_tokens = [
                token
                for token in re.findall(r"[a-zA-Z0-9+#.-]+", claim)
                if len(token) > 2
            ]
            if claim_tokens and not any(token in support for token in claim_tokens):
                unsupported.append(claim)

        total = len(claims)
        supported = total - len(unsupported)
        support_ratio = 1.0 if total == 0 else supported / total

        return {
            "claims": claims,
            "unsupported_claims": unsupported,
            "support_ratio": support_ratio,
            "is_grounded": len(unsupported) == 0,
        }
