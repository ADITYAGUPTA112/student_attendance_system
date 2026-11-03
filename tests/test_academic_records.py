"""Tests for Academic Record Management: Students, Courses, and Enrollments (CA-06, CA-07, CA-08)."""


def test_admin_list_students(client):
    """Verify admin can view student directory."""
    client.post("/login", data={"username": "admin", "password": "admin123"})
    response = client.get("/students")
    assert response.status_code == 200
    assert b"Student Management" in response.data
    assert b"CS-001" in response.data
    assert b"Alice Adams" in response.data


def test_admin_add_student_success(client):
    """Verify admin can add a new student with validation."""
    client.post("/login", data={"username": "admin", "password": "admin123"})
    response = client.post(
        "/students",
        data={
            "roll_no": "CS-005",
            "name": "Edward Evans",
            "email": "edward@example.edu",
            "create_login": "1",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Student &#39;Edward Evans&#39; (CS-005) registered successfully." in response.data or b"Edward Evans" in response.data

    # Verify search finds the new student
    search_resp = client.get("/students?q=Edward")
    assert search_resp.status_code == 200
    assert b"CS-005" in search_resp.data


def test_admin_add_duplicate_roll_no_rejected(client):
    """Verify duplicate roll numbers are rejected with user-friendly error."""
    client.post("/login", data={"username": "admin", "password": "admin123"})
    response = client.post(
        "/students",
        data={
            "roll_no": "CS-001",  # Already exists from seed data
            "name": "Imposter Alice",
            "email": "imposter@example.edu",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"already exists" in response.data


def test_non_admin_cannot_access_students(client):
    """Verify faculty and students are denied access to student management."""
    # Faculty access
    client.post("/login", data={"username": "prof_smith", "password": "faculty123"})
    resp_faculty = client.get("/students")
    assert resp_faculty.status_code == 403

    # Student access
    client.get("/logout")
    client.post("/login", data={"username": "alice", "password": "student123"})
    resp_student = client.get("/students")
    assert resp_student.status_code == 403


def test_courses_view_and_add(client):
    """Verify course catalogue listing and admin course creation (CA-07)."""
    # Admin login
    client.post("/login", data={"username": "admin", "password": "admin123"})
    resp = client.get("/courses")
    assert resp.status_code == 200
    assert b"Course Catalogue" in resp.data
    assert b"CS101" in resp.data

    # Admin adds new course
    add_resp = client.post(
        "/courses",
        data={"code": "CS401", "name": "Distributed Cloud Systems"},
        follow_redirects=True,
    )
    assert add_resp.status_code == 200
    assert b"CS401" in add_resp.data
    assert b"Distributed Cloud Systems" in add_resp.data

    # Duplicate course code rejected
    dup_resp = client.post(
        "/courses",
        data={"code": "CS401", "name": "Another Cloud Course"},
        follow_redirects=True,
    )
    assert b"already exists" in dup_resp.data


def test_faculty_can_view_courses_but_cannot_create(client):
    """Verify faculty can view courses but POST returns redirect or denial."""
    client.post("/login", data={"username": "prof_smith", "password": "faculty123"})
    get_resp = client.get("/courses")
    assert get_resp.status_code == 200
    assert b"Course Catalogue" in get_resp.data

    # Attempt to POST as faculty
    post_resp = client.post(
        "/courses",
        data={"code": "CS999", "name": "Unauthorized Course"},
        follow_redirects=True,
    )
    assert b"Only administrators are authorized" in post_resp.data


def test_enrollment_management(client):
    """Verify admin can enroll and unenroll students into courses (CA-08)."""
    client.post("/login", data={"username": "admin", "password": "admin123"})

    # Diana (CS-004, ID 4) is not enrolled in CS201 (ID 2) initially
    # Let's enroll student ID 4 into course ID 2
    enroll_resp = client.post(
        "/courses/2/enroll",
        data={"student_id": "4"},
        follow_redirects=True,
    )
    assert enroll_resp.status_code == 200
    assert b"successfully enrolled" in enroll_resp.data

    # Duplicate enrollment should be handled safely
    dup_enroll = client.post(
        "/courses/2/enroll",
        data={"student_id": "4"},
        follow_redirects=True,
    )
    assert b"already enrolled" in dup_enroll.data

    # Unenroll student ID 4 from course ID 2
    unenroll_resp = client.post(
        "/courses/2/unenroll/4",
        follow_redirects=True,
    )
    assert unenroll_resp.status_code == 200
    assert b"enrollment removed" in unenroll_resp.data

