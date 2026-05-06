"""HTTP/API pydantic models (separate from learning dataclass schemas)."""

import re
from typing import List, Optional

from pydantic import BaseModel, Field

_URL_IN_TEXT = re.compile(r"https?://[^\s>)\]}\"']+")


def extract_http_urls(text: str) -> List[str]:
    """Collect unique http(s) URLs from agent markdown for API `citations`."""
    seen: dict[str, None] = {}
    for raw in _URL_IN_TEXT.findall(text):
        u = raw.rstrip(".,;:!?)>")
        if u not in seen:
            seen[u] = None
    return list(seen.keys())


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Stable user key for memory and profile isolation.")
    message: str
    session_id: Optional[str] = Field(
        None,
        description="Optional session id for conversation threading.",
    )


class ChatResponse(BaseModel):
    run_id: Optional[str] = None
    session_id: Optional[str] = None
    message: str = Field(..., description="Markdown reply intended for chat UI bubbles.")
    citations: List[str] = Field(default_factory=list, description="URLs cited for source chips or footnotes.")
