from __future__ import annotations

import json
from typing import Any, cast

from resume_analyzer.guardrails.confidence import apply_confidence_adjustments
from resume_analyzer.guardrails.fairness import FairnessChecker
from resume_analyzer.guardrails.fallbacks import low_confidence_fallback
from resume_analyzer.guardrails.grounding import GroundingGuardrails
from resume_analyzer.guardrails.input_quality import (
    assess_job_description_quality,
    assess_resume_quality,
)
from resume_analyzer.guardrails.language_policy import LanguagePolicyGuardrails
from resume_analyzer.guardrails.sensitive_advice import detect_sensitive_career_advice
from resume_analyzer.memory.resume_store import resume_memory
from resume_analyzer.models import JobProfile, Skill
from resume_analyzer.observability.logger import get_structured_logger
from resume_analyzer.tools.ats_scorer import ATSScorer
from resume_analyzer.tools.job_matcher import JobMatcher
from resume_analyzer.tools.langchain_tools import (
    ingest_jobs_tool,
    keyword_extractor_tool,
    resume_parser_tool,
    retrieve_similar_jobs_tool,
)
from resume_analyzer.tools.skill_extractor import SkillExtractor

logger = get_structured_logger("resume_analyzer.target_match_service")


class TargetMatchService:
    """Compare one resume against one target job description."""

    @staticmethod
    def run(user_id: str, resume_text: str, job_description: str, query: str) -> dict[str, object]:
        profile = cast(dict[str, object], resume_parser_tool.invoke({"resume_text": resume_text}))
        raw_skills = [
            str(item.get("name", ""))
            for item in cast(list[dict[str, object]], profile.get("skills", []))
            if isinstance(item, dict)
        ]
        normalized_skills = SkillExtractor.extract_and_normalize(raw_skills)
        profile["skills"] = normalized_skills
        profile["parsed_text"] = resume_text
        profile["user_id"] = user_id

        resume_id = resume_memory.save_resume(user_id, profile)

        jd_keywords = cast(list[str], keyword_extractor_tool.invoke({"text": job_description}))
        required_skills = SkillExtractor.extract_and_normalize(jd_keywords[:15])
        target_job: JobProfile = {
            "id": "target_job",
            "title": "Target Job Description",
            "company": "User Provided",
            "raw_description": job_description,
            "required_skills": cast(list[Skill], required_skills),
            "required_experience_years": 3,
            "source": "import",
        }

        match = JobMatcher.match_resume_to_job(
            resume_skills=cast(list[Skill], normalized_skills),
            resume_experience_years=len(cast(list[object], profile.get("experience", []))),
            job_profile=target_job,
        )
        match["resume_id"] = resume_id

        resume_keywords = set(cast(list[str], keyword_extractor_tool.invoke({"text": resume_text})))
        ats_keyword_gaps = sorted(list(set(jd_keywords) - resume_keywords))[:10]

        ingest_jobs_tool.invoke({})
        rag_query = query.strip() or job_description[:400]
        rag_hits = cast(
            list[dict[str, object]],
            retrieve_similar_jobs_tool.invoke({"query": rag_query, "limit": 3}),
        )
        rag_context = [
            f"{hit.get('title', 'Unknown')} @ {hit.get('company', 'Unknown')}"
            for hit in rag_hits
        ]

        suggestions = list(cast(list[str], match.get("recommendations", [])))
        suggestions.extend([f"Add ATS keyword: {kw}" for kw in ats_keyword_gaps[:5]])

        policy = LanguagePolicyGuardrails.sanitize_recommendations(suggestions)
        suggestions = cast(list[str], policy.get("sanitized", suggestions))

        fairness = FairnessChecker.check_recommendation_fairness(
            recommendation=" ".join(suggestions),
            candidate_profile=profile,
        )
        sensitive = detect_sensitive_career_advice(suggestions)
        resume_quality = assess_resume_quality(profile, resume_text)
        job_quality = assess_job_description_quality(dict(target_job))
        support = GroundingGuardrails.validate_supported_claims(
            suggestions,
            " ".join(
                [
                    resume_text,
                    job_description,
                    json.dumps(match.get("gaps", [])),
                    " ".join(rag_context),
                ]
            ),
        )

        guardrail_notes: list[str] = []
        fairness_issues = cast(list[str], fairness.get("issues", []))
        if fairness_issues:
            guardrail_notes.extend(fairness_issues)
        blocked_phrases = cast(list[str], policy.get("blocked_phrases", []))
        if blocked_phrases:
            guardrail_notes.append("Rewrote risky language: " + ", ".join(blocked_phrases))
        unsupported_claims = cast(list[str], support.get("unsupported_claims", []))
        if unsupported_claims:
            guardrail_notes.append("Unsupported claims removed: " + ", ".join(unsupported_claims))
        if bool(resume_quality.get("is_incomplete", False)):
            flags = cast(list[str], resume_quality.get("flags", []))
            guardrail_notes.append("Incomplete resume detected: " + ", ".join(flags))
        if bool(job_quality.get("is_low_quality", False)):
            flags = cast(list[str], job_quality.get("flags", []))
            guardrail_notes.append("Low-quality job description detected: " + ", ".join(flags))
        if bool(sensitive.get("is_sensitive", False)):
            hits = cast(list[str], sensitive.get("hits", []))
            guardrail_notes.append("Sensitive topic detected: " + ", ".join(hits))

        confidence_factors: dict[str, float] = {}
        if fairness_issues:
            confidence_factors["fairness_issue"] = float(
                fairness.get("confidence_adjustment", -0.1)
            )
        if bool(resume_quality.get("is_incomplete", False)):
            confidence_factors["incomplete_resume"] = -0.15
        if bool(job_quality.get("is_low_quality", False)):
            confidence_factors["low_quality_job"] = -0.15
        support_ratio = float(cast(Any, support.get("support_ratio", 1.0)))
        if support_ratio < 0.8:
            confidence_factors["unsupported_claims"] = -0.2
        if bool(sensitive.get("is_sensitive", False)):
            confidence_factors["sensitive_advice"] = -0.1

        base_confidence = float(match.get("confidence", 0.5))
        final_confidence = apply_confidence_adjustments(base_confidence, confidence_factors)

        fallback_reason: str | None = None
        if unsupported_claims:
            fallback_reason = "unsupported_claims"
        elif bool(resume_quality.get("is_incomplete", False)):
            fallback_reason = "incomplete_resume"
        elif bool(job_quality.get("is_low_quality", False)):
            fallback_reason = "low_quality_job_description"
        elif final_confidence < 0.55:
            fallback_reason = "general_low_confidence"

        if fallback_reason:
            suggestions = low_confidence_fallback(fallback_reason)
            guardrail_notes.append("Fallback response triggered: " + fallback_reason)

        gap_names = [
            str(gap.get("name", ""))
            for gap in cast(list[dict[str, object]], match.get("gaps", []))
            if isinstance(gap, dict)
        ]

        ats_score = ATSScorer.score_ats(resume_text)

        logger.info(
            "target-match-complete",
            extra={
                "user_id": user_id,
            },
        )

        return {
            "success": True,
            "resume_id": resume_id,
            "match_score": float(match.get("match_score", 0.0)),
            "missing_skills": [name for name in gap_names if name],
            "ats_keyword_gaps": ats_keyword_gaps,
            "improvement_suggestions": suggestions,
            "confidence": final_confidence,
            "guardrail_notes": guardrail_notes,
            "support_ratio": support_ratio,
            "fallback_used": fallback_reason is not None,
            "blocked_phrases": blocked_phrases,
            "retrieved_context": rag_context,
            "ats_score": float(ats_score.get("ats_score", 0.0)),
        }
