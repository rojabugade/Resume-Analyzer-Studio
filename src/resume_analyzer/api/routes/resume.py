from typing import Annotated, Any, cast

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from resume_analyzer.agents.orchestrator import ResumeAnalysisOrchestrator
from resume_analyzer.services.target_match_service import TargetMatchService
from resume_analyzer.tools.file_text_extractor import FileTextExtractor

router = APIRouter()
orchestrator = ResumeAnalysisOrchestrator()


class AnalyzeResumeRequest(BaseModel):
    user_id: str = Field(min_length=1)
    resume_text: str = Field(min_length=10)


class AnalyzeResumeResponse(BaseModel):
    success: bool
    title: str
    skills: list[str]
    message: str


class JobMatchRequest(BaseModel):
    user_id: str = Field(min_length=1)
    resume_id: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class JobMatchResponse(BaseModel):
    success: bool
    matches: list[dict]
    total_found: int


class OptimizeResumeRequest(BaseModel):
    user_id: str = Field(min_length=1)
    resume_id: str = Field(min_length=1)
    job_id: str = Field(min_length=1)


class OptimizeResumeResponse(BaseModel):
    success: bool
    job_id: str
    suggestions: dict
    requires_human_review: bool


class RunWorkflowRequest(BaseModel):
    user_id: str = Field(min_length=1)
    resume_text: str = Field(min_length=10)
    query: str = Field(min_length=3)


class RunWorkflowResponse(BaseModel):
    success: bool
    resume_id: str
    matches: list[dict]
    recommendations: list[str]
    confidence: float
    guardrail_notes: list[str]
    support_ratio: float
    fallback_used: bool
    blocked_phrases: list[str]


class TargetMatchRequest(BaseModel):
    user_id: str = Field(min_length=1)
    resume_text: str = Field(min_length=10)
    job_description: str = Field(min_length=10)
    query: str = Field(default="Match this resume against target job description", min_length=3)


class TargetMatchResponse(BaseModel):
    success: bool
    resume_id: str
    match_score: float
    missing_skills: list[str]
    ats_keyword_gaps: list[str]
    improvement_suggestions: list[str]
    confidence: float
    guardrail_notes: list[str]
    support_ratio: float
    fallback_used: bool
    blocked_phrases: list[str]
    retrieved_context: list[str]
    ats_score: float


@router.post("/analyze", response_model=AnalyzeResumeResponse)
def analyze_resume(payload: AnalyzeResumeRequest) -> AnalyzeResumeResponse:
    """Analyze a resume and extract structured information."""
    if len(payload.resume_text) > 50000:
        raise HTTPException(status_code=400, detail="Resume text too long")

    result = orchestrator.analyze_resume(
        user_id=payload.user_id,
        resume_text=payload.resume_text,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Analysis failed"))

    return AnalyzeResumeResponse(**result)


@router.post("/match", response_model=JobMatchResponse)
def match_jobs(payload: JobMatchRequest) -> JobMatchResponse:
    """Find jobs matching the user's resume."""
    result = orchestrator.find_matching_jobs(
        user_id=payload.user_id,
        resume_id=payload.resume_id,
        limit=payload.limit,
    )

    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Matching failed"))

    return JobMatchResponse(**result)


@router.post("/optimize", response_model=OptimizeResumeResponse)
def optimize_resume(payload: OptimizeResumeRequest) -> OptimizeResumeResponse:
    """Get resume optimization suggestions for a specific job."""
    result = orchestrator.optimize_resume_for_job(
        user_id=payload.user_id,
        resume_id=payload.resume_id,
        job_id=payload.job_id,
    )

    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Optimization failed"))

    return OptimizeResumeResponse(**result)


@router.post("/run", response_model=RunWorkflowResponse)
def run_workflow(payload: RunWorkflowRequest) -> RunWorkflowResponse:
    """Run the full router -> analyzer -> matcher -> recommendation workflow."""
    result = orchestrator.run_workflow(
        user_id=payload.user_id,
        resume_text=payload.resume_text,
        query=payload.query,
    )
    return RunWorkflowResponse(
        success=True,
        resume_id=result.get("resume_id", ""),
        matches=result.get("matches", []),
        recommendations=result.get("recommendations", []),
        confidence=result.get("confidence", 0.0),
        guardrail_notes=result.get("guardrail_notes", []),
        support_ratio=result.get("support_ratio", 1.0),
        fallback_used=result.get("fallback_used", False),
        blocked_phrases=result.get("blocked_phrases", []),
    )


@router.post("/run-target", response_model=TargetMatchResponse)
def run_target_match(payload: TargetMatchRequest) -> TargetMatchResponse:
    """Match a resume against a user-provided target job description."""
    try:
        result = TargetMatchService.run(
            user_id=payload.user_id,
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            query=payload.query,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Target matching failed") from exc

    return TargetMatchResponse(**cast(dict[str, Any], result))


@router.post("/run-upload", response_model=TargetMatchResponse)
async def run_target_match_upload(
    user_id: Annotated[str, Form(...)],
    query: Annotated[str, Form()] = "Match this resume against target job description",
    resume_text: Annotated[str | None, Form()] = None,
    job_description: Annotated[str | None, Form()] = None,
    resume_file: Annotated[UploadFile | None, File()] = None,
    job_file: Annotated[UploadFile | None, File()] = None,
) -> TargetMatchResponse:
    """Match with upload support (PDF/DOCX/TXT) for resume and optional JD file."""
    resolved_resume = (resume_text or "").strip()
    resolved_job = (job_description or "").strip()

    try:
        if not resolved_resume and resume_file:
            resolved_resume = await FileTextExtractor.extract_text_from_upload(resume_file)
        if not resolved_job and job_file:
            resolved_job = await FileTextExtractor.extract_text_from_upload(job_file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not resolved_resume:
        raise HTTPException(status_code=400, detail="Resume text or file is required")
    if not resolved_job:
        raise HTTPException(status_code=400, detail="Job description text or file is required")

    try:
        result = TargetMatchService.run(
            user_id=user_id,
            resume_text=resolved_resume,
            job_description=resolved_job,
            query=query,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Upload matching failed") from exc

    return TargetMatchResponse(**cast(dict[str, Any], result))
