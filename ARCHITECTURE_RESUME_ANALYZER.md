# AI-Powered Resume Analyzer & Job Matcher – Architecture Design

## 1. Problem Understanding

**Use Case Goals:**
- Analyze resumes to extract structured information (skills, experience, education, projects)
- Match resumes against job descriptions and rank job fit
- Identify skill gaps, keywords, and ATS optimization opportunities
- Provide personalized resume improvement recommendations
- Recommend relevant jobs based on user profile and experience
- Support multi-step reasoning and explainable decisions

**Key Challenges:**
- Resumes have unstructured, variable formats (PDF, DOCX, plain text)
- Job descriptions vary widely in structure and terminology
- Skill matching requires semantic understanding (synonyms, related skills)
- Recommendations must be fair, unbiased, and not fabricate opportunities
- State management (session vs. user vs. application history)

---

## 2. Architecture Design

### High-Level System Flow

```
User Input (Resume + Job Preferences)
    ↓
Router Agent (intent classification: analyze, match, recommend, optimize)
    ├─→ Resume Analysis Path
    │   ├─ Resume Parser → Extract text/structure
    │   ├─ RAG Retriever → Fetch skill knowledge base
    │   ├─ Analyzer Agent → Extract skills, experience, education, projects
    │   ├─ Skill Extractor Tool → Canonical skill normalization
    │   └─ Storage → Save structured resume to user memory
    │
    ├─→ Job Matching Path
    │   ├─ Job Description Parser → Extract requirements
    │   ├─ RAG Retriever → Similar job profiles, role trends
    │   ├─ Matcher Agent → Score resume against job description
    │   ├─ Gap Analyzer Tool → Identify missing skills/experience
    │   └─ Return ranked matches + explanations
    │
    ├─→ Optimization Path
    │   ├─ Resume Analyzer → Current state review
    │   ├─ ATS Optimizer Tool → Keyword recommendations
    │   ├─ Recommendation Agent → Suggest improvements
    │   └─ Human-in-Loop Review → User approval before saving
    │
    └─→ Recommendation Path
        ├─ Retriever → Fetch jobs matching user profile
        ├─ Ranker Agent → Score and rank recommendations
        └─ Return curated job list with explanations

Safety/Guardrails Layer (runs on all paths):
├─ Input validation: resume format, size, content filters
├─ Output validation: realistic matches, no fabricated data, bias checks
├─ Confidence thresholds: only suggest if match score > threshold
└─ Human-in-loop for sensitive decisions

Memory Management:
├─ Session Memory: Current conversation, intermediate results, user preferences
├─ User Memory: Saved resumes, job preferences, application history
├─ Knowledge Memory: Skills taxonomy, job market trends, company profiles

Observability:
├─ Request tracing (unique IDs for full flow)
├─ Agent decision logging
├─ Tool usage tracking (what tools called, latency)
├─ Confidence/quality metrics
```

---

## 3. Components Breakdown

### A. Agents and Responsibilities

| Agent | Responsibility | Inputs | Outputs |
|-------|---|---|---|
| **Router** | Classify user intent (analyze, match, recommend, optimize) | User message | Intent, extracted entities |
| **Resume Analyzer** | Extract structured data from resumes | Resume text/PDF | Skills, experience, education, projects |
| **Job Matcher** | Score resume against job description | Resume profile, job description | Scores, gaps, ranked matches |
| **Skill Extractor** | Normalize skills to canonical taxonomy | Raw skill mentions | Standardized skills, proficiency levels |
| **Gap Analyzer** | Identify missing experience, skills, keywords | Resume profile, job requirements | Gap report, priority-ranked missing items |
| **Recommendation Agent** | Suggest resume improvements and optimization | Current resume, target role | Improvement suggestions with priorities |
| **Retrieval Agent** | Fetch knowledge base (skills, jobs, trends) | Query | Top-k relevant documents |
| **Job Recommender** | Discover jobs matching user profile | User profile, preferences | Ranked job recommendations |
| **Safety Agent** | Validate inputs, check for bias/fairness | Any input/output | Pass/fail, confidence adjustments |
| **Human Loop Coordinator** | Manage approvals, edits, decisions | Suggestions/changes | Approved changes, audit trail |

### B. Data Models

**Resume Profile (Structured):**
```python
{
  "id": "resume_v1",
  "user_id": "user123",
  "title": "Senior Software Engineer",
  "summary": "...",
  "skills": [
    {"name": "Python", "proficiency": "expert", "years": 7},
    {"name": "AWS", "proficiency": "intermediate", "years": 3}
  ],
  "experience": [
    {
      "company": "TechCorp",
      "role": "Senior Engineer",
      "duration": "2020-2024",
      "responsibilities": ["Led team", "Designed..."]
    }
  ],
  "education": [
    {"school": "MIT", "degree": "BS Computer Science", "year": 2015}
  ],
  "projects": [{"title": "...", "description": "..."}],
  "ats_score": 0.85,
  "extracted_keywords": ["leadership", "microservices", "..."],
  "created_at": "2024-01-15"
}
```

**Job Profile (Structured):**
```python
{
  "id": "job_abc123",
  "title": "Senior Software Engineer",
  "company": "TechCorp",
  "required_skills": [
    {"name": "Python", "proficiency": "intermediate"},
    {"name": "AWS", "proficiency": "intermediate"}
  ],
  "required_experience_years": 5,
  "nice_to_have": ["Kubernetes", "Go"],
  "location": "Remote",
  "salary_range": "$150k-$200k",
  "raw_description": "..."
}
```

**Match Result:**
```python
{
  "job_id": "job_abc123",
  "resume_id": "resume_v1",
  "match_score": 0.82,  # 0-1
  "required_match": 0.90,  # Skills required for role
  "nice_to_have_match": 0.60,
  "experience_fit": 0.85,
  "gaps": [
    {"type": "skill", "name": "Kubernetes", "priority": "medium"}
  ],
  "recommendations": [
    "Add Kubernetes project to resume",
    "Emphasize distributed systems experience"
  ],
  "confidence": 0.88,
  "reasoning": "Strong match on core skills; minor gap on containerization..."
}
```

### C. Tools Registry

| Tool | Purpose | Integration |
|------|---------|---|
| `parse_resume` | Extract text from PDF/DOCX | pypdf, python-docx |
| `extract_skills` | Normalize and extract skills | Custom NLP + skills taxonomy |
| `parse_job_description` | Extract structure from job text | NLP + job template matching |
| `search_job_db` | Query job database | API/SQL |
| `skill_similarity` | Semantic skill matching | Vector embeddings (e.g., OpenAI) |
| `ats_score` | Calculate ATS compatibility | Keyword and format analysis |
| `keyword_analysis` | Identify optimization opportunities | Frequency analysis + trends |
| `fairness_check` | Detect bias in recommendations | Diverse candidate profiles |

### D. Memory Architecture

**Session Memory (In-Memory / Cache):**
- Current conversation turns
- Extracted partial data
- User selections/preferences
- TTL: 1 hour

**User Memory (PostgreSQL):**
- Saved resumes and versions
- Job preferences and search history
- Application logs (applied where, when, outcome)
- Feedback on recommendations
- Saved job favorites

**Knowledge Memory (Vector DB):**
- Skills taxonomy (embeddings)
- Job descriptions (embeddings)
- Resume examples for each industry
- Market trends (skills demand, salary ranges)
- Company profiles and culture fit

### E. Guardrails & Safety

**Input Validation:**
- Resume file size < 10MB
- No malicious content (PDFs that execute)
- PII redaction (if needed for logging)
- Supported formats: PDF, DOCX, TXT

**Output Validation:**
- Match scores only if confidence > threshold (e.g., 0.70)
- No hallucinated job matches (only DB results)
- Bias check: diverse candidate profiles in recommendations
- Fairness: don't exclude based on age, gender, race
- Confidence labels: exact, likely, uncertain

**Decision Thresholds:**
- Match score > 0.80: Confident recommendation
- Match score 0.60-0.80: Partial fit, review gaps
- Match score < 0.60: Poor fit, don't recommend
- Confidence < 0.70: Flag for human review

**Human-in-Loop:**
- Resume edits: user approves before saving
- Significant improvements: explain reasoning
- Sensitive feedback: human review before sending
- Failed confidence checks: escalate to reviewer

---

## 4. Tech Stack Suggestions

| Layer | Technology | Rationale |
|-------|---|---|
| **API** | FastAPI + Uvicorn | Async, type-safe, fast startup |
| **Orchestration** | LangGraph | State graphs for multi-agent flows |
| **LLM** | OpenAI API (GPT-4 mini for cost) | Reliable, good for reasoning |
| **Embeddings** | OpenAI (text-embedding-3-small) | Semantic matching, cost-effective |
| **Document Parsing** | pypdf, python-docx | Resume extraction |
| **Vector DB** | PostgreSQL + pgvector | Self-hosted, ACID, cost-effective |
| **Memory** | Redis (optional, cached) + Postgres | Session + durable |
| **Search** | SQL + vector similarity | Job and resume search |
| **Logging/Tracing** | OpenTelemetry + Langfuse | Observability, debugging |
| **Testing** | Pytest + synthetic golden data | Quality gates |
| **Containerization** | Docker + Compose | Reproducible deployment |
| **Deployment** | AWS ECS or Railway | Portfolio-friendly |

**Alternative Options:**
- Vector DB: Qdrant (managed) or Pinecone (serverless)
- LLM: Anthropic Claude or open-source (Llama via Ollama)
- Job DB: Indeed API (paid) or custom job crawler
- Embedding: Hugging Face (self-hosted) or Cohere

---

## 5. Folder Structure

```
resume-analyzer/
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/  (CI/CD)
├── src/
│   └── resume_analyzer/
│       ├── __init__.py
│       ├── main.py (FastAPI app)
│       ├── config.py (settings, env)
│       │
│       ├── api/
│       │   └── routes/
│       │       ├── resume.py (upload, analyze, list, delete)
│       │       ├── jobs.py (search, match, recommend)
│       │       ├── users.py (profile, preferences)
│       │       └── admin.py (human review, audit trail)
│       │
│       ├── agents/
│       │   ├── router.py (intent classification)
│       │   ├── analyzer.py (resume extraction)
│       │   ├── matcher.py (job matching)
│       │   ├── recommender.py (job recommendations)
│       │   └── orchestrator.py (LangGraph workflow)
│       │
│       ├── rag/
│       │   ├── retriever.py (vector search)
│       │   ├── ingester.py (skill taxonomy, job examples)
│       │   └── embedder.py (embedding generation)
│       │
│       ├── tools/
│       │   ├── registry.py (tool definitions)
│       │   ├── resume_parser.py
│       │   ├── skill_extractor.py
│       │   ├── job_parser.py
│       │   ├── job_search.py
│       │   ├── ats_scorer.py
│       │   ├── skill_matcher.py
│       │   └── fairness_check.py
│       │
│       ├── memory/
│       │   ├── session.py (in-memory turns)
│       │   ├── user_store.py (postgres)
│       │   ├── knowledge_store.py (vector db)
│       │   └── models.py (Resume, Job, etc.)
│       │
│       ├── guardrails/
│       │   ├── policy.py (validation rules)
│       │   ├── fairness.py (bias detection)
│       │   └── confidence.py (thresholds)
│       │
│       ├── observability/
│       │   ├── tracing.py (OpenTelemetry)
│       │   ├── logging.py (structured logs)
│       │   └── metrics.py (tool usage, latency)
│       │
│       └── evals/
│           ├── harness.py (test runner)
│           ├── golden_data.py (test cases)
│           └── scorecards.py (quality metrics)
│
├── tests/
│   ├── test_resume_parser.py
│   ├── test_skill_extraction.py
│   ├── test_job_matching.py
│   ├── test_orchestrator.py
│   ├── test_guardrails.py
│   └── test_api.py
│
├── data/
│   ├── skills_taxonomy.json (skills hierarchy)
│   ├── sample_resumes/ (for testing)
│   └── sample_jobs.json (job examples)
│
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── README.md
├── .env.example
└── .gitignore
```

---

## 6. Data Flow Example: "Analyze Resume & Find Matching Jobs"

```
1. User uploads resume + specifies role interest
   ↓
2. Router Agent: Intent = "match"
   ↓
3. Resume Parser: Extract text from PDF
   ↓
4. Analyzer Agent: 
   - Extract skills (with proficiency)
   - Extract experience (roles, duration, achievements)
   - Extract education
   - Build structured resume profile
   ↓
5. Store in User Memory (Postgres)
   ↓
6. Job Search Tool: Query DB for matching roles
   ↓
7. RAG Retriever: Fetch knowledge about similar roles, trends
   ↓
8. Matcher Agent (parallel over top-5 jobs):
   - Parse job description
   - Score resume skills vs. job requirements
   - Identify gaps
   - Generate recommendations
   ↓
9. Fairness Check: Verify no bias in ranking
   ↓
10. Human-in-Loop (if confidence < threshold):
    - Request clarification or expert review
    ↓
11. Return to user:
    - Ranked matches with scores
    - Gap analysis per job
    - Resume improvement suggestions
    - Confidence levels & explanations
```

---

## 7. Scaling & Optimization Ideas

**For Portfolio/Interview:**
- Start with 1-2 agents + RAG, scale to full multi-agent
- Use mock job DB initially (500 sample jobs)
- Simple fairness checks first (diverse profiles)
- Local PostgreSQL + pgvector

**For Production:**
- Parallel tool execution (match 50 jobs at once)
- Caching layer (Redis) for embeddings + matches
- Async job ingestion pipeline (nightly)
- A/B test skill extraction models
- Cost controls: model routing (small for simple, large for reasoning)
- Rate limiting by user and API
- Circuit breakers for job DB outages
- User telemetry: which recommendations accepted, applied, resulted in interview

---

## 8. Success Metrics

- Resume extraction accuracy: > 90% on golden dataset
- Job matching precision: No nonsensical matches (user satisfaction > 4/5)
- Skill gap identification: Agree with resume experts > 80%
- ATS optimization: Resume improvements boost ATS score 10-20pts
- Latency: Resume analysis < 5s, matching 5 jobs < 10s
- Fairness: Recommendations diverse across demographics (optional proxy)
