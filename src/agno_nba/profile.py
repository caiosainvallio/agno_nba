"""Extended learning profile for NBA fan preferences (structured fields)."""

from dataclasses import dataclass, field
from typing import Optional

from agno.learn.schemas import UserProfile


@dataclass
class NbaFanProfile(UserProfile):
    favorite_nba_teams: Optional[str] = field(
        default=None,
        metadata={
            "description": "User favorite NBA team(s); comma-separated names or abbreviations they prefer.",
        },
    )
    favorite_nba_players: Optional[str] = field(
        default=None,
        metadata={
            "description": "Favorite player names to prioritize for stats and injury checks.",
        },
    )
    analysis_preferences: Optional[str] = field(
        default=None,
        metadata={
            "description": (
                "What they care about in analysis (minutes, usage, matchups, trends); "
                "do not give betting or wagering guidance."
            ),
        },
    )
