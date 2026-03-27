from ai_agent_system.agents.state import AgentState
from ai_agent_system.guardrails.policy import check_input_policy, check_output_policy
from ai_agent_system.memory.store import memory_store
from ai_agent_system.rag.retriever import retrieve_context
from ai_agent_system.tools.registry import call_tool


def router_node(state: AgentState) -> AgentState:
    msg = state["message"].lower()
    if any(k in msg for k in ["search", "what", "explain", "why"]):
        state["route"] = "research"
    elif any(k in msg for k in ["calculate", "tool", "run"]):
        state["route"] = "action"
    else:
        state["route"] = "direct"
    return state


def researcher_node(state: AgentState) -> AgentState:
    state["retrieved_context"] = retrieve_context(state["message"])
    state["citations"] = (
        ["kb://sample-doc-1", "kb://sample-doc-2"]
        if state["retrieved_context"]
        else []
    )
    return state


def action_node(state: AgentState) -> AgentState:
    tool_result = call_tool("calculator", {"expression": "2+2"})
    state["used_tools"].append("calculator")
    state["retrieved_context"].append(f"Tool result: {tool_result}")
    return state


def synthesis_node(state: AgentState) -> AgentState:
    check_input_policy(state["message"])
    context = (
        "\n".join(state["retrieved_context"])
        if state["retrieved_context"]
        else "No extra context"
    )
    state["answer"] = f"Route={state['route']} | Answer based on context: {context}"
    check_output_policy(state["answer"])
    memory_store.add_turn(state["user_id"], state["session_id"], state["message"], state["answer"])
    return state
