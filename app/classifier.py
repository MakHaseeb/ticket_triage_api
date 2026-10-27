from app.schemas import TriageRequest, TriageResponse


def classify_ticket(request: TriageRequest) -> TriageResponse:
    """Return a fixed valid result. M2 replaces this with the Gemini call."""
    return TriageResponse(
        category="other",
        priority="normal",
        summary=request.subject,
        needs_human=False,
        reason="Fake classifier result for testing.",
        fallback=False,
        model="fake",
        prompt_version="v1",
        latency_ms=0,
    )
