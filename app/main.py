import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.classifier import classify_ticket
from app.config import get_service_api_key
from app.schemas import TriageRequest, TriageResponse

VERSION = "0.1.0"

app = FastAPI(title="Ticket Triage API", version=VERSION)
bearer_scheme = HTTPBearer()


def check_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> None:
    """Raise 401 unless the Bearer token equals SERVICE_API_KEY."""
    expected_key = get_service_api_key()
    if not expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    if not secrets.compare_digest(credentials.credentials.encode(), expected_key.encode()):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the service is running."""
    return {"status": "ok", "version": VERSION}


@app.post("/triage", dependencies=[Depends(check_api_key)])
def triage(request: TriageRequest) -> TriageResponse:
    """Classify one ticket and return the triage result."""
    return classify_ticket(request)
