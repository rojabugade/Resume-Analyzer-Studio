from fastapi import FastAPI

from ai_agent_system.api.routes.chat import router as chat_router
from ai_agent_system.config import settings
from ai_agent_system.observability.tracing import setup_tracing
from resume_analyzer.api.routes.resume import router as resume_router
from resume_analyzer.api.routes.ui import router as ui_router

setup_tracing(enabled=settings.enable_trace, service_name=settings.app_name)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(ui_router, tags=["ui"])
app.include_router(chat_router, prefix="/v1", tags=["chat"])
app.include_router(resume_router, prefix="/v1/resume", tags=["resume"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
