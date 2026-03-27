# Resume Analyzer & Job Matcher - Implementation Guide

## Project Overview

This AI agent system analyzes resumes, extracts structured information, matches them against job descriptions, identifies skill gaps, and provides personalized recommendations for improvement.

## Key Features

### 1. Resume Analysis
- Extract structured information: skills, experience, education, projects
- Normalize skills to canonical taxonomy
- Calculate ATS (Applicant Tracking System) compatibility score
- Parse multiple formats (text, PDF, DOCX)

### 2. Job Matching
- Score resume against job descriptions (0-1 scale)
- Identify required vs. nice-to-have skill alignment
- Calculate experience fit
- Surface specific gaps with priorities

### 3. Resume Optimization
- Generate tailored improvement suggestions
- Keyword optimization recommendations
- ATS compliance feedback
- Human-in-loop review for sensitive recommendations

### 4. Job Recommendations
- Find jobs matching user profile
- Rank by match score and confidence
- Provide explanations for each match
- Suggest related job titles

## Architecture

### Agent Layers

```
Router Agent (Intent Classification)
    ├─ Resume Analysis Path
    │   ├─ Resume Parser → Extract text structure
    │   ├─ Skill Extractor → Normalize to canonical form
    │   └─ ATS Scorer → Calculate compatibility
    │
    ├─ Job Matching Path
    │   ├─ Job Parser → Extract requirements
    │   ├─ Skill Matcher → Score alignment
    │   ├─ Gap Analyzer → Identify missing items
    │   └─ Recommender → Suggest improvements
    │
    └─ Job Search Path
        ├─ Knowledge Base Retriever
        ├─ Ranker
        └─ Fairness Checker
```

### Data Flow

1. **Input** → Resume text + Job search criteria
2. **Parse** → Extract structured data
3. **Normalize** → Map to canonical forms
4. **Match** → Calculate alignment scores
5. **Analyze** → Identify gaps
6. **Recommend** → Generate suggestions
7. **Validate** → Check fairness and confidence
8. **Output** → Return results with explanations

## Core Modules

### Tools
- `resume_parser.py` - Extract text from resumes
- `skill_extractor.py` - Normalize skills to taxonomy
- `job_matcher.py` - Score resume-to-job alignment
- `ats_scorer.py` - Calculate ATS compatibility

### Agents
- `orchestrator.py` - Main workflow coordinator

### Memory
- `resume_store.py` - User resumes and preferences

### RAG (Retrieval Augmented Generation)
- `knowledge_base.py` - Skills and job lookup

### Guardrails
- `fairness.py` - Bias detection
- `confidence.py` - Threshold management

## API Endpoints

### Resume Analysis
```bash
POST /v1/resume/analyze
{
  "user_id": "user123",
  "resume_text": "Senior Software Engineer..."
}
```

### Job Matching
```bash
POST /v1/resume/match
{
  "user_id": "user123",
  "resume_id": "resume_1",
  "limit": 5
}
```

### Resume Optimization
```bash
POST /v1/resume/optimize
{
  "user_id": "user123",
  "resume_id": "resume_1",
  "job_id": "job_001"
}
```

## Testing

Run tests:
```bash
make test
# or
pytest tests/ -v
```

Tests cover:
- Resume parsing and skill extraction
- Job matching algorithms
- ATS scoring
- Orchestration workflow
- API endpoints

## Development

### Setup
```bash
pip install -e .[dev]
```

### Run API
```bash
make dev
# or
uvicorn ai_agent_system.main:app --reload
```

### Quality Checks
```bash
make lint    # ruff check
make type    # mypy
make test    # pytest
```

## Production Roadmap

### Phase 1 (MVP - Current)
- Basic resume parsing (text extraction)
- Simple skill matching (string similarity)
- Job database (hardcoded samples)
- In-memory storage

### Phase 2 (Scaling)
- PDF/DOCX parsing (pypdf, python-docx)
- Vector embeddings for skill matching (OpenAI)
- PostgreSQL + pgvector for job storage
- Redis for session caching
- Async job processing

### Phase 3 (Advanced)
- Real-time job API integration (Indeed, LinkedIn)
- Candidate skill gap learning models
- Personalized learning path recommendations
- Career trajectory forecasting
- Budget-aware recommendations (salary negotiation)

### Phase 4 (Enterprise)
- Multi-tenancy (white-label)
- Analytics dashboard (hiring trends)
- Integrations (ATS systems, HR platforms)
- Compliance (GDPR, fair hiring practices)
- Custom skill taxonomies per industry

## Safety & Fairness

### Guardrails
- Input validation (file size, format, PII)
- Confidence thresholds before recommendations
- Bias detection in matching
- No fabricated job matches
- Human review for sensitive decisions

### Fairness Checks
- Diverse job recommendations
- Avoid discriminatory language
- Equal opportunity principles
- Explainable decisions

## Known Limitations

- Resume extraction is basic (text-only for now)
- Job matching uses string similarity (no semantic embeddings yet)
- Small job database (sample data only)
- No user authentication
- In-memory storage (non-persistent)
- Limited NLP capabilities (no advanced parsing)

## Future Enhancements

1. **LLM Integration** - Use GPT-4 for reasoning and extraction
2. **Vector Search** - Semantic matching with embeddings
3. **Skill Gap Learning** - Recommend courses/certifications
4. **Interview Prep** - Generate interview questions based on resume+job
5. **Salary Insights** - Negotiate based on market data
6. **Team Matching** - Find complementary team members
7. **Career Coaching** - Personalized paths based on goals
8. **Accessibility** - Support more languages and formats

## Deployment

### Docker
```bash
docker build -t resume-analyzer .
docker-compose up
```

### Cloud Platforms
- AWS ECS (container orchestration)
- AWS RDS (PostgreSQL database)
- AWS ElastiCache (Redis)
- AWS S3 (file storage)

## Evaluation Metrics

- **Resume Extraction Accuracy** > 90% on golden dataset
- **Job Match Precision** > 85% (user satisfaction > 4/5)
- **Skill Gap Recall** > 80% (agree with resume experts)
- **ATS Improvement** > 10-20 point boost
- **Latency** < 5s resume analysis, < 10s for 5 job matches
- **Fairness** Recommendations diverse across demographics

## Contributing

1. Add tests for new features
2. Pass lint/type checks
3. Update documentation
4. Request review before merge

## Support

For issues, feature requests, or questions, open a GitHub issue or contact the team.

---

**Status**: MVP Ready for Portfolio Showcase  
**Last Updated**: March 2026
