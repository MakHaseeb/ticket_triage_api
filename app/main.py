import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException

from app.classifier import classify_ticket
from app.config import get_service_api_key
from app.schemas import TriageRequest, TriageResponse

VERSION = "0.1.0"

app = FastAPI(title="Ticket Triage API", version=VERSION)


def check_api_key(authorization: Annotated[str | None, Header()] = None) -> None:
    """Raise 401 unless the header is 'Bearer <SERVICE_API_KEY>'."""
    expected_key = get_service_api_key()
    expected_header = f"Bearer {expected_key}"
    if not expected_key or authorization is None:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    if not secrets.compare_digest(authorization, expected_header):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the service is running."""
    return {"status": "ok", "version": VERSION}


@app.post("/triage", dependencies=[Depends(check_api_key)])
def triage(request: TriageRequest) -> TriageResponse:
    """Classify one ticket and return the triage result."""
    return classify_ticket(request)
