from typing import Literal, Optional

from pydantic import BaseModel, Field

Verdict = Literal["allow", "flag", "block"]


class ScreenRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    context: Optional[str] = None


class ScreenResponse(BaseModel):
    verdict: Verdict
    risk_score: float
    categories: list[str]
    reasons: list[str]
