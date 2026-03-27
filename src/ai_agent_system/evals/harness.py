from ai_agent_system.agents.orchestrator import run_agent_graph
from resume_analyzer.evals.harness import run_resume_eval


def run_smoke_eval() -> dict[str, bool]:
    cases = [
        "Explain RAG architecture",
        "Run tool for calculation",
    ]
    passed = True
    for case in cases:
        result = run_agent_graph("eval-user", "eval-session", case)
        if not result.get("answer"):
            passed = False
    return {"smoke_eval_passed": passed}


def run_full_resume_eval() -> dict[str, object]:
    """Run the complete resume analyzer evaluation suite."""
    return run_resume_eval()
