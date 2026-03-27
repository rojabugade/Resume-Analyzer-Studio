from datetime import datetime


class ResumeMemory:
    """Storage for user resumes and preferences."""

    def __init__(self) -> None:
        self._resumes: dict[str, list] = {}
        self._user_preferences: dict[str, dict] = {}

    def save_resume(self, user_id: str, resume_data: dict) -> str:
        """Save a resume version."""
        if user_id not in self._resumes:
            self._resumes[user_id] = []
        resume_id = f"resume_{len(self._resumes[user_id]) + 1}"
        resume_data["id"] = resume_id
        resume_data["created_at"] = datetime.utcnow().isoformat()
        self._resumes[user_id].append(resume_data)
        return resume_id

    def get_resume(self, user_id: str, resume_id: str | None = None) -> dict | None:
        """Fetch a resume by ID or latest."""
        if user_id not in self._resumes:
            return None
        if resume_id:
            for r in self._resumes[user_id]:
                if r.get("id") == resume_id:
                    return r
            return None
        return self._resumes[user_id][-1] if self._resumes[user_id] else None

    def list_resumes(self, user_id: str) -> list[dict]:
        """List all resumes for a user."""
        return self._resumes.get(user_id, [])

    def save_preferences(self, user_id: str, preferences: dict) -> None:
        """Save user preferences (target roles, skills to learn, etc.)."""
        self._user_preferences[user_id] = preferences

    def get_preferences(self, user_id: str) -> dict:
        """Get user preferences."""
        return self._user_preferences.get(user_id, {})


resume_memory = ResumeMemory()
