"""Tests for Authentication, Role-Based Access Control, and Dashboards (CA-03, CA-04, CA-05)."""


def test_login_page_renders(client):
    """Verify that the login page renders with HTTP 200."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign in to your academic account" in response.data
    assert b"Demo Accounts" in response.data


def test_admin_login_success(client):
    """Verify admin login redirects to dashboard and sets session."""
    response = client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Administrator Overview" in response.data
    assert b"admin" in response.data


def test_faculty_login_success(client):
    """Verify faculty login redirects to faculty portal and sets session."""
    response = client.post(
        "/login",
        data={"username": "prof_smith", "password": "faculty123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Faculty Portal" in response.data
    assert b"prof_smith" in response.data


def test_student_login_success(client):
    """Verify student login redirects to personal student dashboard."""
    response = client.post(
        "/login",
        data={"username": "alice", "password": "student123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"My Attendance Dashboard" in response.data
    assert b"CS-001" in response.data


def test_invalid_credentials_rejected(client):
    """Verify that bad credentials display generic error message without account enumeration."""
    response = client.post(
        "/login",
        data={"username": "admin", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data

    # Non-existent user
    response = client.post(
        "/login",
        data={"username": "nonexistent_user", "password": "somepassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data


def test_logout_clears_session(client):
    """Verify that logging out clears session and redirects to login."""
    # Log in first
    client.post("/login", data={"username": "admin", "password": "admin123"})

    # Log out
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been signed out successfully." in response.data

    # Accessing dashboard should now redirect to login
    protected_resp = client.get("/dashboard")
    assert protected_resp.status_code == 302
    assert "/login" in protected_resp.headers["Location"]


def test_unauthenticated_protected_route_redirect(client):
    """Verify unauthenticated user cannot access protected dashboard."""
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_student_forbidden_from_admin_route(client):
    """Verify that a student role receives HTTP 403 when requesting admin routes."""
    # Login as student
    client.post("/login", data={"username": "alice", "password": "student123"})

    # Attempt to access admin audit route
    response = client.get("/audit")
    assert response.status_code == 403
    assert b"403" in response.data


def test_faculty_forbidden_from_admin_route(client):
    """Verify that a faculty member receives HTTP 403 when requesting admin audit route."""
    # Login as faculty
    client.post("/login", data={"username": "prof_smith", "password": "faculty123"})

    # Attempt to access admin audit route
    response = client.get("/audit")
    assert response.status_code == 403


def test_student_data_isolation(client):
    """Verify student only sees their own data (CA-10 privacy requirement)."""
    # Login as Alice
    client.post("/login", data={"username": "alice", "password": "student123"})
    alice_resp = client.get("/student/dashboard")
    assert alice_resp.status_code == 200
    assert b"CS-001" in alice_resp.data
    assert b"CS-002" not in alice_resp.data

    # Switch to Bob
    client.get("/logout")
    client.post("/login", data={"username": "bob", "password": "student123"})
    bob_resp = client.get("/student/dashboard")
    assert bob_resp.status_code == 200
    assert b"CS-002" in bob_resp.data
    assert b"CS-001" not in bob_resp.data

