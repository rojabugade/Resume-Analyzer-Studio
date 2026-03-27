from uuid import uuid4

from resume_analyzer.agents.langgraph_flow import resume_workflow_graph
from resume_analyzer.memory.resume_store import resume_memory
from resume_analyzer.observability.logger import get_structured_logger

logger = get_structured_logger("resume_analyzer.orchestrator")


class ResumeAnalysisOrchestrator:
    """Orchestrate resume analysis and job matching workflow."""

    def run_workflow(self, user_id: str, resume_text: str, query: str) -> dict:
        return self._run_flow(user_id=user_id, resume_text=resume_text, query=query)

    @staticmethod
    def _run_flow(user_id: str, resume_text: str, query: str) -> dict:
        session_id = str(uuid4())
        state = resume_workflow_graph.invoke(
            {
                "session_id": session_id,
                "user_id": user_id,
                "query": query,
                "resume_text": resume_text,
            }
        )
        logger.info(
            "resume-workflow-complete",
            extra={
                "session_id": session_id,
                "user_id": user_id,
                "trace_id": state.get("trace_id", ""),
            },
        )
        return state

    def analyze_resume(
        self,
        user_id: str,
        resume_text: str,
    ) -> dict:
        """Analyze resume and extract structured profile."""
        state = self._run_flow(
            user_id=user_id,
            resume_text=resume_text,
            query="Analyze this resume",
        )
        profile = state.get("resume_profile", {})
        normalized_skills = profile.get("skills", [])
        return {
            "success": True,
            "title": profile.get("title"),
            "skills": [s.get("name") for s in normalized_skills],
            "message": "Resume analyzed successfully",
        }

    def find_matching_jobs(
        self,
        user_id: str,
        resume_id: str,
        limit: int = 5,
    ) -> dict:
        """Find and rank jobs matching user's resume."""
        resume = resume_memory.get_resume(user_id, resume_id)
        if not resume:
            return {"success": False, "error": "Resume not found"}

        state = self._run_flow(
            user_id=user_id,
            resume_text=resume.get("parsed_text", ""),
            query="Match this resume to jobs",
        )
        matches = state.get("matches", [])
        return {
            "success": True,
            "matches": matches[:limit],
            "total_found": len(matches),
        }

    def optimize_resume_for_job(
        self,
        user_id: str,
        resume_id: str,
        job_id: str,
    ) -> dict:
        """Generate resume optimization suggestions for a specific job."""
        resume = resume_memory.get_resume(user_id, resume_id)
        if not resume:
            return {"success": False, "error": "Resume or job not found"}

        state = self._run_flow(
            user_id=user_id,
            resume_text=resume.get("parsed_text", ""),
            query=f"Recommend resume improvements for job {job_id}",
        )

        matches = [m for m in state.get("matches", []) if m.get("job_id") == job_id]
        match = matches[0] if matches else state.get("matches", [{}])[0]
        recommendations = state.get("recommendations", match.get("recommendations", []))

        suggestions = {
            "overall_fit": {
                "score": match.get("match_score", 0),
                "feedback": f"You are a {match.get('match_score', 0):.0%} match for this role.",
            },
            "skill_gaps": match.get("gaps", []),
            "recommendations": recommendations,
            "improvement_priority": ResumeAnalysisOrchestrator._prioritize_improvements(
                match.get("gaps", [])
            ),
            "guardrail_notes": state.get("guardrail_notes", []),
        }

        return {
            "success": True,
            "job_id": job_id,
            "suggestions": suggestions,
            "requires_human_review": state.get("confidence", match.get("confidence", 0.5)) < 0.70,
        }

    @staticmethod
    def _prioritize_improvements(gaps: list) -> list[str]:
        """Prioritize improvements based on gaps."""
        if not gaps:
            return ["Resume is well-aligned with target role."]
        high_priority = [g for g in gaps if g.get("priority") == "high"]
        return [
            f"Focus on adding {g['name']} to your resume"
            for g in high_priority[:3]
        ]
