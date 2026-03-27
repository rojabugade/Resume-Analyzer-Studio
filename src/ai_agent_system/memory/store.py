class MemoryStore:
    def __init__(self) -> None:
        self._turns: dict[str, list[dict[str, str]]] = {}

    def _key(self, user_id: str, session_id: str) -> str:
        return f"{user_id}:{session_id}"

    def add_turn(self, user_id: str, session_id: str, message: str, answer: str) -> None:
        key = self._key(user_id, session_id)
        self._turns.setdefault(key, []).append({"message": message, "answer": answer})

    def history(self, user_id: str, session_id: str) -> list[dict[str, str]]:
        return self._turns.get(self._key(user_id, session_id), [])


memory_store = MemoryStore()
