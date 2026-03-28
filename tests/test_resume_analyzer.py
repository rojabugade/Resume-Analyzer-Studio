from fastapi.testclient import TestClient

from ai_agent_system.main import app

client = TestClient(app)


def test_resume_analysis() -> None:
    """Test resume analysis endpoint."""
    response = client.post(
        "/v1/resume/analyze",
        json={
            "user_id": "user123",
            "resume_text": "Senior Software Engineer\n\nSkills: Python, AWS, Docker\n\nExperience: Senior Engineer at TechCorp 2020-2024",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert "Senior" in data["title"]
    assert len(data["skills"]) > 0


def test_job_matching() -> None:
    """Test job matching endpoint."""
    # First analyze a resume
    client.post(
        "/v1/resume/analyze",
        json={
            "user_id": "user456",
            "resume_text": "Senior Software Engineer\n\nSkills: Python, AWS\n\nExperience: 5 years",
        },
    )

    # Then match jobs
    response = client.post(
        "/v1/resume/match",
        json={
            "user_id": "user456",
            "resume_id": "resume_1",
            "limit": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["total_found"] >= 0


def test_resume_optimization() -> None:
    """Test resume optimization endpoint."""
    # First analyze a resume
    client.post(
        "/v1/resume/analyze",
        json={
            "user_id": "user789",
            "resume_text": "Software Engineer\n\nSkills: Python\n\nExperience: 3 years",
        },
    )

    # Then optimize for a job
    response = client.post(
        "/v1/resume/optimize",
        json={
            "user_id": "user789",
            "resume_id": "resume_1",
            "job_id": "job_001",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert "suggestions" in data


def test_target_match_text_flow() -> None:
    """Test direct resume-vs-target-job flow with pasted text."""
    response = client.post(
        "/v1/resume/run-target",
        json={
            "user_id": "target_user_001",
            "resume_text": (
                "Backend Engineer\n"
                "Skills: Python, AWS, Docker\n"
                "Experience: Built APIs and platform services."
            ),
            "job_description": (
                "We need a backend engineer with Python, SQL, and AWS experience. "
                "Responsibilities include API design and reliability improvements."
            ),
            "query": "Match my resume to this JD",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert "match_score" in data
    assert "missing_skills" in data
    assert "ats_keyword_gaps" in data
    assert "improvement_suggestions" in data
    assert "guardrail_notes" in data


def test_target_match_upload_flow() -> None:
    """Test multipart upload flow with plain text files."""
    files = {
        "resume_file": (
            "resume.txt",
            b"Software Engineer\nSkills: Python, AWS\nExperience: Built APIs.",
            "text/plain",
        ),
        "job_file": (
            "job.txt",
            b"Looking for Python, SQL, and AWS engineer for backend APIs.",
            "text/plain",
        ),
    }
    data = {
        "user_id": "target_user_002",
        "query": "Match uploaded resume with uploaded JD",
    }

    response = client.post("/v1/resume/run-upload", data=data, files=files)
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"]
    assert isinstance(payload["confidence"], float)
    assert isinstance(payload["improvement_suggestions"], list)


def test_target_match_upload_invalid_pdf_returns_400() -> None:
    """Invalid PDF bytes should return a user-facing 400 error."""
    files = {
        "resume_file": (
            "resume.pdf",
            b"%PDF-not-a-valid-pdf",
            "application/pdf",
        ),
    }
    data = {
        "user_id": "target_user_003",
        "job_description": "Need Python backend engineer with API and SQL experience.",
        "query": "Match uploaded resume with typed JD",
    }

    response = client.post("/v1/resume/run-upload", data=data, files=files)
    assert response.status_code == 400
    detail = response.json().get("detail", "")
    assert "Unable to parse PDF" in detail
