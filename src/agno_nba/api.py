"""AgentOS FastAPI app with `/chat` returning conversational markdown plus citations."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

load_dotenv()

from agno.db.postgres import PostgresDb
from agno.os import AgentOS

from agno_nba.agent import build_agent
from agno_nba.schemas_api import ChatRequest, ChatResponse, extract_http_urls


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable {name}. Copy .env.example and export values.",
        )
    return value


_postgres_db = PostgresDb(db_url=_require_env("DATABASE_URL"))
_nba_agent = build_agent(_postgres_db)

agent_os = AgentOS(
    id="agno-nba-os",
    name="Agno NBA",
    description="NBA player performance and injury research assistant",
    db=_postgres_db,
    agents=[_nba_agent],
    telemetry=False,
)

app = agent_os.get_app()

_router = APIRouter(tags=["chat"])


@_router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    session_id = body.session_id
    try:
        run_output = _nba_agent.run(
            body.message,
            user_id=body.user_id,
            session_id=session_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    content = run_output.content
    if isinstance(content, str):
        message = content.strip()
    else:
        message = str(content).strip()

    if not message:
        raise HTTPException(status_code=500, detail="Agent returned an empty response")

    return ChatResponse(
        run_id=run_output.run_id,
        session_id=run_output.session_id or session_id,
        message=message,
        citations=extract_http_urls(message),
    )


app.include_router(_router)
