from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_agent_system.agents.orchestrator import run_agent_graph

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    answer: str
    route: str
    used_tools: list[str]
    citations: list[str]


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    if len(payload.message) > 4000:
        raise HTTPException(status_code=400, detail="Message too long")

    result = run_agent_graph(
        user_id=payload.user_id,
        session_id=payload.session_id,
        message=payload.message,
    )

    return ChatResponse(**result)
