from resume_analyzer.models import JobProfile


class OptionalJobSearchAPI:
    """Optional external job source adapter.

    Replace this stub with a real provider integration (LinkedIn, Greenhouse, etc.).
    """

    @staticmethod
    def search_jobs(query: str, limit: int = 5) -> list[JobProfile]:
        # Intentionally returns empty by default so local retrieval remains deterministic.
        _ = query
        _ = limit
        return []
