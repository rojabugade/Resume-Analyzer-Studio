from resume_analyzer.models import JobMatch


class ReliabilityGuardrails:
    """Guardrails to prevent over-claiming and unreliable output."""

    @staticmethod
    def validate_matches(matches: list[JobMatch]) -> list[str]:
        notes: list[str] = []
        for match in matches:
            score = float(match.get("match_score", 0.0))
            if score > 0.98:
                job_id = match.get("job_id", "unknown")
                notes.append(
                    f"Capped unusually high score for job {job_id} "
                    "to avoid fabricated certainty."
                )
                match["match_score"] = 0.98
            if not match.get("reasoning"):
                notes.append(f"Missing reasoning for job {match.get('job_id', 'unknown')}.")
        return notes
