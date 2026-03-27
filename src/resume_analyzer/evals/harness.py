from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass

from resume_analyzer.agents.orchestrator import ResumeAnalysisOrchestrator
from resume_analyzer.evals.dataset import EVAL_CASES, EvalCase
from resume_analyzer.evals.metrics import (
    CaseMetrics,
    f1_from_sets,
    hallucination_rate,
    reciprocal_rank,
)
from resume_analyzer.evals.rubric import usefulness_rubric_score
from resume_analyzer.rag.knowledge_base import knowledge_base
from resume_analyzer.tools.ats_scorer import ATSScorer


@dataclass
class CaseResult:
    case_id: str
    scenario: str
    metrics: CaseMetrics
    passed: bool
    notes: list[str]
    agent_path: list[str]
    tool_calls: list[str]


def _ensure_override_jobs(case: EvalCase) -> None:
    for job in case.get("job_overrides", []):
        knowledge_base.add_job(job)


def _expected_set(items: list[str]) -> set[str]:
    return {item.lower() for item in items}


def _predict_skill_set(state: dict) -> set[str]:
    profile = state.get("resume_profile", {})
    return {s.get("name", "").lower() for s in profile.get("skills", []) if s.get("name")}


def _top_match(state: dict) -> dict:
    matches = state.get("matches", [])
    return matches[0] if matches else {}


def _extract_missing_skills(match: dict) -> set[str]:
    gaps = match.get("gaps", [])
    return {gap.get("name", "").lower() for gap in gaps if gap.get("name")}


def _is_task_complete(state: dict) -> bool:
    return bool(state.get("resume_id")) and bool(state.get("matches") is not None)


def evaluate_case(orchestrator: ResumeAnalysisOrchestrator, case: EvalCase) -> CaseResult:
    _ensure_override_jobs(case)

    started = time.perf_counter()
    state = orchestrator.run_workflow(
        user_id=case["user_id"],
        resume_text=case["resume_text"],
        query=case["query"],
    )
    latency_ms = (time.perf_counter() - started) * 1000.0

    expectation = case.get("expectation", {})
    notes: list[str] = []

    predicted_skills = _predict_skill_set(state)
    expected_skills = _expected_set(expectation.get("expected_skills", []))
    parse_f1 = f1_from_sets(predicted_skills, expected_skills) if expected_skills else 1.0

    matches = state.get("matches", [])
    ranked_ids = [m.get("job_id", "") for m in matches if m.get("job_id")]
    relevant_ids = set(expectation.get("expected_relevant_jobs", []))
    job_match_quality = reciprocal_rank(ranked_ids, relevant_ids)

    top = _top_match(state)
    expected_missing = _expected_set(expectation.get("expected_missing_skills", []))
    predicted_missing = _extract_missing_skills(top)
    if expected_missing:
        missing_skill_f1 = f1_from_sets(predicted_missing, expected_missing)
    else:
        missing_skill_f1 = 1.0

    recommendations = state.get("recommendations", [])
    recommendation_usefulness, rubric_breakdown = usefulness_rubric_score(
        recommendations,
        expectation.get("expected_missing_skills", []),
    )

    support_text = " ".join([
        case["resume_text"],
        top.get("reasoning", ""),
        json.dumps(top.get("gaps", [])),
    ])
    hallucination = hallucination_rate(recommendations, support_text)

    task_success = 1.0 if _is_task_complete(state) else 0.0

    ats_score = ATSScorer.score_ats(case["resume_text"]).get("ats_score", 0.0)

    if expectation.get("expected_top_job_id") and ranked_ids:
        if ranked_ids[0] != expectation["expected_top_job_id"]:
            notes.append(
                "Top job mismatch: expected "
                f"{expectation['expected_top_job_id']}, got {ranked_ids[0]}"
            )

    if "min_match_score" in expectation and float(top.get("match_score", 0.0)) < float(
        expectation["min_match_score"]
    ):
        notes.append("Top match score below minimum expected threshold.")

    if "max_match_score" in expectation and float(top.get("match_score", 0.0)) > float(
        expectation["max_match_score"]
    ):
        notes.append("Top match score above maximum expected threshold.")

    if "min_ats_score" in expectation and ats_score < float(expectation["min_ats_score"]):
        notes.append("ATS score below expected threshold.")

    if hallucination > 0.20:
        notes.append("Hallucination rate exceeded 20%.")

    has_expected_gaps = bool(expectation.get("expected_missing_skills", []))
    if has_expected_gaps and recommendation_usefulness < 0.50:
        notes.append("Recommendation usefulness below rubric threshold.")

    if expectation.get("expect_completion", True) and task_success < 1.0:
        notes.append("Task did not complete successfully.")

    metrics = CaseMetrics(
        parse_f1=parse_f1,
        job_match_quality=job_match_quality,
        missing_skill_f1=missing_skill_f1,
        recommendation_usefulness=recommendation_usefulness,
        hallucination_rate=hallucination,
        latency_ms=latency_ms,
        task_completion_success=task_success,
    )

    notes.append(f"Rubric breakdown: {rubric_breakdown}")

    return CaseResult(
        case_id=case["case_id"],
        scenario=case["scenario"],
        metrics=metrics,
        passed=(
            len(
                [
                    n
                    for n in notes
                    if "below" in n or "exceeded" in n or "mismatch" in n
                ]
            )
            == 0
        ),
        notes=notes,
        agent_path=state.get("agent_path", []),
        tool_calls=state.get("tool_calls", []),
    )


def run_resume_eval() -> dict[str, object]:
    orchestrator = ResumeAnalysisOrchestrator()
    results = [evaluate_case(orchestrator, case) for case in EVAL_CASES]

    total = len(results)
    passed = sum(1 for r in results if r.passed)

    avg_parse_f1 = sum(r.metrics.parse_f1 for r in results) / max(1, total)
    avg_match_quality = sum(r.metrics.job_match_quality for r in results) / max(1, total)
    avg_gap_f1 = sum(r.metrics.missing_skill_f1 for r in results) / max(1, total)
    avg_reco = sum(r.metrics.recommendation_usefulness for r in results) / max(1, total)
    avg_hallucination = sum(r.metrics.hallucination_rate for r in results) / max(1, total)
    avg_latency = sum(r.metrics.latency_ms for r in results) / max(1, total)
    success_rate = sum(r.metrics.task_completion_success for r in results) / max(1, total)

    if total > 1:
        p95_latency = sorted(r.metrics.latency_ms for r in results)[
            int(0.95 * (total - 1))
        ]
    else:
        p95_latency = avg_latency

    return {
        "summary": {
            "cases_total": total,
            "cases_passed": passed,
            "pass_rate": passed / max(1, total),
            "avg_parse_f1": avg_parse_f1,
            "avg_job_match_quality": avg_match_quality,
            "avg_missing_skill_f1": avg_gap_f1,
            "avg_recommendation_usefulness": avg_reco,
            "avg_hallucination_rate": avg_hallucination,
            "avg_latency_ms": avg_latency,
            "p95_latency_ms": p95_latency,
            "task_completion_success": success_rate,
        },
        "cases": [
            {
                "case_id": result.case_id,
                "scenario": result.scenario,
                "metrics": asdict(result.metrics),
                "passed": result.passed,
                "notes": result.notes,
                "agent_path": result.agent_path,
                "tool_calls": result.tool_calls,
            }
            for result in results
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run_resume_eval(), indent=2))
