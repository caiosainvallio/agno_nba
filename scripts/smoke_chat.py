"""Smoke test: app imports, OpenAPI exposes `/chat`, optional live agent call."""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("SKIP: DATABASE_URL not set")
        return 0

    from fastapi.testclient import TestClient

    from agno_nba.api import app

    with TestClient(app) as client:
        spec = client.get("/openapi.json")
        if spec.status_code != 200:
            print("openapi failed", spec.status_code, spec.text)
            return 1
        paths = spec.json().get("paths") or {}
        if "/chat" not in paths:
            print("missing /chat in OpenAPI paths:", list(paths.keys())[:20])
            return 1
        print("openapi_ok /chat")

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("SKIP live agent: GROQ_API_KEY not set")
        return 0

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "user_id": "smoke-user",
                "message": (
                    "Say hello briefly and confirm you can search the web for NBA injury news; "
                    "use tools only if needed."
                ),
                "session_id": "smoke-session",
            },
        )
        print("chat_status", response.status_code)
        if response.status_code != 200:
            print(response.text)
            return 1
        payload = response.json()
        assert "message" in payload
        msg = payload.get("message") or ""
        print("chat_ok", msg[:160])
    return 0


if __name__ == "__main__":
    sys.exit(main())
