import os


def get_service_api_key() -> str:
    """Return the SERVICE_API_KEY env var, or an empty string if unset."""
    return os.environ.get("SERVICE_API_KEY", "")
