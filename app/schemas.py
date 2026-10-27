from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["billing", "bug", "how_to", "account_access", "feature_request", "other"]
Priority = Literal["urgent", "high", "normal", "low"]


class TriageRequest(BaseModel):
    """One support ticket sent to POST /triage."""

    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=5000)


class TriageResponse(BaseModel):
    """The triage result returned by POST /triage."""

    category: Category
    priority: Priority
    summary: str
    needs_human: bool
    reason: str
    fallback: bool
    model: str
    prompt_version: str
    latency_ms: int
