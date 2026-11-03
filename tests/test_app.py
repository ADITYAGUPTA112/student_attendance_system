"""Initial test suite for CloudAttend (CA-01)."""


def test_health_check(client):
    """Verify that the /health route returns 200 OK and expected JSON structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data.get("status") == "healthy"
    assert data.get("service") == "CloudAttend"
    assert data.get("version") == "1.0.0"


def test_app_config(app):
    """Verify application test configuration."""
    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "test-secret-key"

