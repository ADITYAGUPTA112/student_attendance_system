"""Initial test suite for AttendX (CA-01)."""


def test_health_check(client):
    """Verify that the /health route returns 200 OK and expected JSON structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data.get("status") == "healthy"
    assert data.get("service") == "AttendX"
    assert data.get("version") == "1.0.0"


def test_app_config(app):
    """Verify application test configuration."""
    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "test-secret-key"


def test_attendx_branding_and_local_logos(client):
    """Verify AttendX branding and local uploaded icon/wordmark logos appear across portals."""
    login_res = client.get("/login")
    assert login_res.status_code == 200
    assert b"AttendX" in login_res.data
    assert b"attendx-icon.jpg" in login_res.data
    assert b"attendx-wordmark.jpg" in login_res.data
    assert b"lh3.googleusercontent.com" not in login_res.data
    assert b"Academic Portal v2.4" not in login_res.data

    client.post("/login", data={"username": "admin", "password": "admin123"})
    dash_res = client.get("/dashboard")
    assert dash_res.status_code == 200
    assert b"AttendX" in dash_res.data
    assert b"attendx-icon.jpg" in dash_res.data
    assert b"attendx-wordmark.jpg" in dash_res.data
    assert b"lh3.googleusercontent.com" not in dash_res.data


def test_login_3d_motion_controls_compact_in_footer(client):
    """Verify 3D motion controls live as a compact toolbar in footer rather than header."""
    res = client.get("/login")
    assert res.status_code == 200
    html = res.data.decode("utf-8")

    assert "Move cursor &amp; click to randomize 3D neon flow" not in html
    header_part, footer_split = html.split("</header>", 1)
    assert 'id="motion-toolbar"' not in header_part
    assert "<footer" in footer_split
    _, footer_part = footer_split.split("<footer", 1)
    assert 'id="motion-toolbar"' in footer_part
    assert 'role="toolbar"' in footer_part
    assert 'focusgroup="toolbar wrap"' in footer_part
    assert 'id="toggle-motion-btn"' in footer_part
    assert 'aria-pressed="false"' in footer_part

