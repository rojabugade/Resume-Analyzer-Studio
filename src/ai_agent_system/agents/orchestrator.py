from typing import TypedDict

from ai_agent_system.agents.nodes import action_node, researcher_node, router_node, synthesis_node
from ai_agent_system.agents.state import AgentState


class OrchestratorResult(TypedDict):
    answer: str
    route: str
    used_tools: list[str]
    citations: list[str]


def run_agent_graph(user_id: str, session_id: str, message: str) -> OrchestratorResult:
    state: AgentState = {
        "user_id": user_id,
        "session_id": session_id,
        "message": message,
        "route": "",
        "retrieved_context": [],
        "used_tools": [],
        "citations": [],
        "answer": "",
    }

    state = router_node(state)

    if state["route"] == "research":
        state = researcher_node(state)
    elif state["route"] == "action":
        state = action_node(state)

    state = synthesis_node(state)
    return {
        "answer": state["answer"],
        "route": state["route"],
        "used_tools": state["used_tools"],
        "citations": state["citations"],
    }
