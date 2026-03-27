from typing import Any

from langgraph.graph import END, START, StateGraph

from resume_analyzer.agents.nodes import (
    job_matcher_agent,
    recommendation_agent,
    resume_analyzer_agent,
    router_agent,
)
from resume_analyzer.agents.state import ResumeWorkflowState


def build_resume_workflow() -> Any:
    graph = StateGraph(ResumeWorkflowState)

    graph.add_node("router", router_agent)
    graph.add_node("resume_analyzer", resume_analyzer_agent)
    graph.add_node("job_matcher", job_matcher_agent)
    graph.add_node("recommendation", recommendation_agent)

    graph.add_edge(START, "router")
    graph.add_edge("router", "resume_analyzer")
    graph.add_edge("resume_analyzer", "job_matcher")
    graph.add_edge("job_matcher", "recommendation")
    graph.add_edge("recommendation", END)

    return graph.compile()


resume_workflow_graph = build_resume_workflow()
