from typing import TypedDict


class AgentState(TypedDict):
    user_id: str
    session_id: str
    message: str
    route: str
    retrieved_context: list[str]
    used_tools: list[str]
    citations: list[str]
    answer: str
