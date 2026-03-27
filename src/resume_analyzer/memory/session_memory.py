from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class SessionContext:
    turns: list[dict[str, str]] = field(default_factory=list)


class SessionMemory:
    """Short-term memory scoped to a single user session."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionContext] = defaultdict(SessionContext)

    def add_turn(self, session_id: str, role: str, content: str) -> None:
        self._sessions[session_id].turns.append({"role": role, "content": content})

    def get_turns(self, session_id: str, limit: int = 10) -> list[dict[str, str]]:
        return self._sessions.get(session_id, SessionContext()).turns[-limit:]


session_memory = SessionMemory()
