"""NBA-focused Agno agent: web search + learning-backed preferences."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.learn import LearningMachine
from agno.learn.config import LearningMode, UserMemoryConfig, UserProfileConfig
from agno.models.groq import Groq
from agno.tools.websearch import WebSearchTools

from agno_nba.profile import NbaFanProfile


class GroqToolsCompat(Groq):
    """Groq rejects JSON ``response_format`` when tools are enabled; drop it for those requests."""

    def get_request_params(
        self,
        response_format: Optional[Union[Dict[str, Any], Type[BaseModel]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if tools:
            response_format = None
        return super().get_request_params(
            response_format=response_format,
            tools=tools,
            tool_choice=tool_choice,
        )


def _groq_model() -> Groq:
    mid = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    return GroqToolsCompat(id=mid)


def _nba_instructions() -> list[str]:
    return [
        "You help follow NBA player performances and injury/designation updates.",
        "Always search the web when answering questions about current injuries or recent games.",
        "Prefer official NBA sources (nba.com, team sites) when available, and cross-check with reputable "
        "outlets (e.g. ESPN, The Athletic). Note material disagreements briefly.",
        "Use the user's learned profile and memories for favorite teams, players, and analysis preferences.",
        "When listing injuries or statuses, reflect uncertainty when sources conflict.",
        "Do not provide betting, gambling, or wagering advice.",
        "Reply in natural conversational Markdown for a chat UI: short opening answer, then bullets if listing "
        "players or injuries. Never wrap the reply in a JSON object or code block.",
        "When you use web results, end with a **Sources** section as markdown links or bullet URLs.",
    ]


def build_agent(db: PostgresDb) -> Agent:
    model = _groq_model()
    learning = LearningMachine(
        db=db,
        model=model,
        user_profile=UserProfileConfig(
            schema=NbaFanProfile,
            mode=LearningMode.ALWAYS,
            additional_instructions=(
                "Capture favorite NBA teams, favorite players, and how they want performance/injury analysis framed."
            ),
        ),
        user_memory=UserMemoryConfig(
            mode=LearningMode.ALWAYS,
            additional_instructions=(
                "Store durable preferences that do not fit profile fields (e.g. follow specific beat reporters, "
                "which stats they always want)."
            ),
        ),
    )

    return Agent(
        id="nba-research",
        name="NBA Research",
        model=model,
        db=db,
        learning=learning,
        
        tools=[
            WebSearchTools(
                backend="google",
                enable_search=True,
                enable_news=True,
                fixed_max_results=5,
                timeout=15,
            )
        ],
        instructions=_nba_instructions(),
        add_datetime_to_context=True,
        add_history_to_context=True,
        num_history_runs=8,
        tool_call_limit=20,
        markdown=True,
        telemetry=False,
    )
