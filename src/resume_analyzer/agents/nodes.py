from __future__ import annotations

import json
from typing import Any, cast
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from ai_agent_system.config import settings
from resume_analyzer.agents.state import ResumeWorkflowState
from resume_analyzer.guardrails.confidence import apply_confidence_adjustments
from resume_analyzer.guardrails.fairness import FairnessChecker
from resume_analyzer.guardrails.fallbacks import low_confidence_fallback
from resume_analyzer.guardrails.grounding import GroundingGuardrails
from resume_analyzer.guardrails.input_quality import (
    assess_job_description_quality,
    assess_resume_quality,
)
from resume_analyzer.guardrails.language_policy import LanguagePolicyGuardrails
from resume_analyzer.guardrails.reliability import ReliabilityGuardrails
from resume_analyzer.guardrails.sensitive_advice import detect_sensitive_career_advice
from resume_analyzer.memory.resume_store import resume_memory
from resume_analyzer.memory.session_memory import session_memory
from resume_analyzer.rag.knowledge_base import knowledge_base
from resume_analyzer.tools.job_matcher import JobMatcher
from resume_analyzer.tools.langchain_tools import (
    ingest_jobs_tool,
    keyword_extractor_tool,
    optional_job_search_tool,
    resume_parser_tool,
    retrieve_similar_jobs_tool,
    similarity_scoring_tool,
)
from resume_analyzer.tools.skill_extractor import SkillExtractor


def _append_agent_path(state: ResumeWorkflowState, agent_name: str) -> None:
    path = state.get("agent_path", [])
    path.append(agent_name)
    state["agent_path"] = path


def _record_tool_call(state: ResumeWorkflowState, tool_name: str) -> None:
    calls = state.get("tool_calls", [])
    calls.append(tool_name)
    state["tool_calls"] = calls


def _get_llm() -> ChatOpenAI | None:
    key = settings.openai_api_key.strip()
    if not key or key.lower() in {"replace-me", "changeme", "your-key-here"}:
        return None
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=SecretStr(key),
        temperature=0.2,
    )


def _classify_route(query: str) -> str:
    query_lower = query.lower()
    if "match" in query_lower or "job" in query_lower:
        return "job_match"
    if "improve" in query_lower or "optimize" in query_lower or "recommend" in query_lower:
        return "recommend"
    return "analyze"


def router_agent(state: ResumeWorkflowState) -> ResumeWorkflowState:
    _append_agent_path(state, "router_agent")
    trace_id = state.get("trace_id", str(uuid4()))
    query = state.get("query", "")
    route = _classify_route(query)
    state["trace_id"] = trace_id
    state["route"] = route
    if state.get("session_id"):
        session_memory.add_turn(state["session_id"], "user", query)
    return state


def resume_analyzer_agent(state: ResumeWorkflowState) -> ResumeWorkflowState:
    _append_agent_path(state, "resume_analyzer_agent")
    resume_text = state.get("resume_text", "")
    if not resume_text:
        return state

    _record_tool_call(state, "resume_parser_tool")
    profile = resume_parser_tool.invoke({"resume_text": resume_text})
    skills = [s.get("name", "") for s in profile.get("skills", [])]
    normalized = SkillExtractor.extract_and_normalize(skills)
    profile["skills"] = normalized

    user_id = state.get("user_id", "anonymous")
    resume_id = resume_memory.save_resume(user_id, profile)

    _record_tool_call(state, "keyword_extractor_tool")
    extracted_keywords = keyword_extractor_tool.invoke({"text": resume_text})
    profile["extracted_keywords"] = extracted_keywords

    state["resume_profile"] = profile
    state["resume_id"] = resume_id
    return state


def job_matcher_agent(state: ResumeWorkflowState) -> ResumeWorkflowState:
    _append_agent_path(state, "job_matcher_agent")
    _record_tool_call(state, "ingest_jobs_tool")
    ingest_jobs_tool.invoke({})

    profile = state.get("resume_profile", {})
    resume_id = state.get("resume_id", "")
    user_id = state.get("user_id", "anonymous")

    query = " ".join(profile.get("extracted_keywords", [])[:8]) or profile.get("title", "")
    _record_tool_call(state, "retrieve_similar_jobs_tool")
    vector_hits = retrieve_similar_jobs_tool.invoke({"query": query, "limit": 5})

    jobs = []
    for hit in vector_hits:
        job_id = str(hit.get("job_id", ""))
        if job_id and job_id in knowledge_base._jobs:
            jobs.append(knowledge_base._jobs[job_id])

    if not jobs:
        jobs = list(knowledge_base._jobs.values())[:5]

    _record_tool_call(state, "optional_job_search_tool")
    external_jobs = optional_job_search_tool.invoke({"query": query, "limit": 2})
    if external_jobs:
        jobs.extend(external_jobs)

    matches = []
    resume_skills = profile.get("skills", [])
    resume_exp_years = len(profile.get("experience", []))

    for job in jobs:
        match = JobMatcher.match_resume_to_job(
            resume_skills=resume_skills,
            resume_experience_years=resume_exp_years,
            job_profile=job,
        )
        match["resume_id"] = resume_id
        job_id = match.get("job_id", "")
        if job_id:
            lexical = similarity_scoring_tool.invoke(
                {"resume_id": resume_id, "user_id": user_id, "job_id": job_id}
            )
            _record_tool_call(state, "similarity_scoring_tool")
            match["match_score"] = float((match.get("match_score", 0.0) + lexical) / 2)
        matches.append(match)

    matches.sort(key=lambda item: float(item.get("match_score", 0.0)), reverse=True)
    guardrail_notes = ReliabilityGuardrails.validate_matches(matches)

    job_quality_flags: list[str] = []
    for job in jobs:
        quality = assess_job_description_quality(dict(job))
        flags = cast(list[str], quality.get("flags", []))
        job_quality_flags.extend(flags)
    if job_quality_flags:
        guardrail_notes.append(
            "Low-quality job descriptions detected: "
            + ", ".join(sorted(set(job_quality_flags)))
        )

    state["jobs"] = jobs
    state["matches"] = matches
    state["guardrail_notes"] = guardrail_notes
    state["job_quality_flags"] = sorted(set(job_quality_flags))
    return state


def recommendation_agent(state: ResumeWorkflowState) -> ResumeWorkflowState:
    _append_agent_path(state, "recommendation_agent")
    matches = state.get("matches", [])
    if not matches:
        state["recommendations"] = low_confidence_fallback("general_low_confidence")
        state["confidence"] = 0.3
        state["fallback_used"] = True
        return state

    top_match = matches[0]
    base_recs = top_match.get("recommendations", [])

    llm = _get_llm()
    if llm:
        prompt = {
            "match": top_match,
            "guardrails": "Do not fabricate claims. Only use supplied data.",
        }
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are a resume recommendation agent. Provide concise, "
                        "factual improvements "
                        "based only on the input and avoid unverifiable claims."
                    )
                ),
                HumanMessage(content=json.dumps(prompt)),
            ]
        )
        content = (
            response.content
            if isinstance(response.content, str)
            else json.dumps(response.content)
        )
        generated = [line.strip("- ") for line in content.split("\n") if line.strip()]
        recommendations = generated[:6] if generated else base_recs
    else:
        recommendations = base_recs

    policy = LanguagePolicyGuardrails.sanitize_recommendations(recommendations)
    recommendations = cast(list[str], policy.get("sanitized", recommendations))

    fairness = FairnessChecker.check_recommendation_fairness(
        recommendation=" ".join(recommendations),
        candidate_profile=dict(state.get("resume_profile", {})),
    )

    support_corpus = " ".join(
        [
            state.get("resume_text", ""),
            top_match.get("reasoning", ""),
            json.dumps(top_match.get("gaps", [])),
            json.dumps(state.get("resume_profile", {})),
        ]
    )
    grounding = GroundingGuardrails.validate_supported_claims(recommendations, support_corpus)
    sensitive = detect_sensitive_career_advice(recommendations)
    resume_quality = assess_resume_quality(
        dict(state.get("resume_profile", {})),
        state.get("resume_text", ""),
    )

    notes = state.get("guardrail_notes", [])
    fairness_issues = cast(list[str], fairness.get("issues", []))
    notes.extend(fairness_issues)
    blocked_phrases = cast(list[str], policy.get("blocked_phrases", []))
    if blocked_phrases:
        notes.append("Rewrote risky language: " + ", ".join(blocked_phrases))
    unsupported_claims = cast(list[str], grounding.get("unsupported_claims", []))
    if unsupported_claims:
        notes.append("Unsupported claims removed: " + ", ".join(unsupported_claims))
    sensitive_hits = cast(list[str], sensitive.get("hits", []))
    if bool(sensitive.get("is_sensitive", False)):
        notes.append("Sensitive advice topic detected: " + ", ".join(sensitive_hits))
    resume_flags = cast(list[str], resume_quality.get("flags", []))
    if bool(resume_quality.get("is_incomplete", False)):
        notes.append("Incomplete resume detected: " + ", ".join(resume_flags))

    confidence_factors: dict[str, float] = {}
    if fairness_issues:
        confidence_factors["fairness_issue"] = float(fairness.get("confidence_adjustment", -0.1))
    job_quality_flags = cast(list[str], state.get("job_quality_flags", []))
    if bool(resume_quality.get("is_incomplete", False)) or job_quality_flags:
        confidence_factors["low_data_quality"] = -0.15
    support_ratio = float(cast(Any, grounding.get("support_ratio", 1.0)))
    if support_ratio < 0.8:
        confidence_factors["unsupported_claims"] = -0.2
    if bool(sensitive.get("is_sensitive", False)):
        confidence_factors["sensitive_topic"] = -0.1

    base_confidence = float(top_match.get("confidence", 0.5))
    adjusted_confidence = apply_confidence_adjustments(
        base_confidence=base_confidence,
        factors=confidence_factors,
    )

    fallback_reason: str | None = None
    if unsupported_claims:
        fallback_reason = "unsupported_claims"
    elif bool(resume_quality.get("is_incomplete", False)):
        fallback_reason = "incomplete_resume"
    elif job_quality_flags:
        fallback_reason = "low_quality_job_description"
    elif adjusted_confidence < 0.55:
        fallback_reason = "general_low_confidence"

    if fallback_reason:
        recommendations = low_confidence_fallback(fallback_reason)
        notes.append("Fallback response triggered: " + fallback_reason)

    state["recommendations"] = recommendations
    state["confidence"] = adjusted_confidence
    state["guardrail_notes"] = notes
    state["support_ratio"] = support_ratio
    state["fallback_used"] = fallback_reason is not None
    state["blocked_phrases"] = blocked_phrases

    if state.get("session_id"):
        session_memory.add_turn(state["session_id"], "assistant", "\n".join(recommendations))

    return state
