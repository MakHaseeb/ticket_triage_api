import pytest
from fastapi.testclient import TestClient

from app.main import app

TEST_KEY = "test-service-key"
VALID_TICKET = {"subject": "Cannot export report", "body": "The export button does nothing."}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Return a test client with a fake SERVICE_API_KEY set."""
    monkeypatch.setenv("SERVICE_API_KEY", TEST_KEY)
    return TestClient(app)


def auth_header(key: str = TEST_KEY) -> dict[str, str]:
    """Build an Authorization header for the given key."""
    return {"Authorization": f"Bearer {key}"}


def test_health_returns_ok(client: TestClient) -> None:
    """GET /health returns 200 and the status JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_triage_without_key_returns_401(client: TestClient) -> None:
    """POST /triage with no Authorization header returns 401."""
    response = client.post("/triage", json=VALID_TICKET)
    assert response.status_code == 401


def test_triage_with_wrong_key_returns_401(client: TestClient) -> None:
    """POST /triage with a wrong key returns 401."""
    response = client.post("/triage", json=VALID_TICKET, headers=auth_header("wrong-key"))
    assert response.status_code == 401


def test_triage_empty_subject_returns_422(client: TestClient) -> None:
    """An empty subject fails validation with 422."""
    ticket = {"subject": "", "body": "Some text."}
    response = client.post("/triage", json=ticket, headers=auth_header())
    assert response.status_code == 422


def test_triage_body_too_long_returns_422(client: TestClient) -> None:
    """A body over 5000 characters fails validation with 422."""
    ticket = {"subject": "Long ticket", "body": "a" * 5001}
    response = client.post("/triage", json=ticket, headers=auth_header())
    assert response.status_code == 422


def test_triage_valid_request_returns_all_fields(client: TestClient) -> None:
    """A valid request returns 200 with every field from the spec."""
    response = client.post("/triage", json=VALID_TICKET, headers=auth_header())
    assert response.status_code == 200
    data = response.json()
    expected_fields = {
        "category", "priority", "summary", "needs_human", "reason",
        "fallback", "model", "prompt_version", "latency_ms",
    }
    assert set(data) == expected_fields
    assert data["category"] in {"billing", "bug", "how_to", "account_access", "feature_request", "other"}
    assert data["priority"] in {"urgent", "high", "normal", "low"}
    assert data["fallback"] is False
