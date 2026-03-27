from ai_agent_system.agents.orchestrator import run_agent_graph


def test_orchestrator_research_route() -> None:
    result = run_agent_graph("u1", "s1", "Explain RAG")
    assert result["route"] in {"research", "direct", "action"}
    assert isinstance(result["answer"], str)


def test_orchestrator_action_route() -> None:
    result = run_agent_graph("u1", "s1", "run tool now")
    assert isinstance(result["used_tools"], list)
