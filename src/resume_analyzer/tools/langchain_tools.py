from langchain_core.tools import tool

from resume_analyzer.memory.resume_store import resume_memory
from resume_analyzer.models import JobProfile
from resume_analyzer.rag.knowledge_base import knowledge_base
from resume_analyzer.rag.vector_store import job_vector_store
from resume_analyzer.tools.job_search_api import OptionalJobSearchAPI
from resume_analyzer.tools.keyword_extractor import KeywordExtractor
from resume_analyzer.tools.resume_parser import ResumeParser
from resume_analyzer.tools.similarity import SimilarityScorer


@tool
def resume_parser_tool(resume_text: str) -> dict:
    """Parse raw resume text into structured fields."""
    profile = ResumeParser.parse_text(resume_text)
    return dict(profile)


@tool
def keyword_extractor_tool(text: str) -> list[str]:
    """Extract ranking keywords from any text."""
    return KeywordExtractor.extract(text)


@tool
def similarity_scoring_tool(resume_id: str, user_id: str, job_id: str) -> float:
    """Compute lexical overlap score between a stored resume and job requirements."""
    resume = resume_memory.get_resume(user_id=user_id, resume_id=resume_id)
    job = knowledge_base._jobs.get(job_id)
    if not resume or not job:
        return 0.0

    resume_skills = resume.get("skills", [])
    required = [s.get("name", "") for s in job.get("required_skills", [])]
    return SimilarityScorer.score_skill_overlap(resume_skills, required)


@tool
def optional_job_search_tool(query: str, limit: int = 5) -> list[JobProfile]:
    """Optional external job search integration."""
    return OptionalJobSearchAPI.search_jobs(query=query, limit=limit)


@tool
def ingest_jobs_tool() -> int:
    """Ingest in-memory jobs into Chroma vector store."""
    jobs = list(knowledge_base._jobs.values())
    if jobs:
        job_vector_store.ingest_jobs(jobs)
    return len(jobs)


@tool
def retrieve_similar_jobs_tool(query: str, limit: int = 5) -> list[dict[str, object]]:
    """Retrieve semantically similar jobs from Chroma."""
    return job_vector_store.retrieve(query=query, k=limit)
