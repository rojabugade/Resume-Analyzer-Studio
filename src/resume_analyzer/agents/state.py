from typing import TypedDict

from resume_analyzer.models import JobMatch, JobProfile, ResumeProfile


class ResumeWorkflowState(TypedDict, total=False):
    session_id: str
    user_id: str
    route: str
    query: str
    resume_text: str
    resume_id: str
    target_job_id: str
    resume_profile: ResumeProfile
    jobs: list[JobProfile]
    matches: list[JobMatch]
    recommendations: list[str]
    confidence: float
    guardrail_notes: list[str]
    trace_id: str
    agent_path: list[str]
    tool_calls: list[str]
    support_ratio: float
    fallback_used: bool
    blocked_phrases: list[str]
    job_quality_flags: list[str]
