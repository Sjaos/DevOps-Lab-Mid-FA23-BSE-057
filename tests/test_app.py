import pytest
from app import app, submissions


@pytest.fixture
def client():
    app.config["TESTING"] = True

    submissions.clear()

    with app.test_client() as client:
        yield client

    submissions.clear()


def test_valid_submission(client):
    response = client.post(
        "/",
        data={
            "student_name": "Shahab Ahmed",
            "registration_number": "CSC418-001",
            "assignment_title": "DevOps Midterm",
            "submission_url": "https://github.com/example/project",
        },
    )

    assert response.status_code == 200
    assert len(submissions) == 1
    assert b"Submission saved successfully." in response.data


def test_missing_required_field_shows_error(client):
    response = client.post(
        "/",
        data={
            "student_name": "",
            "registration_number": "CSC418-001",
            "assignment_title": "DevOps Midterm",
            "submission_url": "https://github.com/example/project",
        },
    )

    assert response.status_code == 200
    assert b"Student Name is required." in response.data
    assert len(submissions) == 0


def test_missing_registration_number_shows_error(client):
    response = client.post(
        "/",
        data={
            "student_name": "Shahab Ahmed",
            "registration_number": "",
            "assignment_title": "DevOps Midterm",
            "submission_url": "https://github.com/example/project",
        },
    )

    assert response.status_code == 200
    assert b"Registration Number is required." in response.data
    assert len(submissions) == 0


def test_missing_assignment_title_shows_error(client):
    response = client.post(
        "/",
        data={
            "student_name": "Shahab Ahmed",
            "registration_number": "CSC418-001",
            "assignment_title": "",
            "submission_url": "https://github.com/example/project",
        },
    )

    assert response.status_code == 200
    assert b"Assignment Title is required." in response.data
    assert len(submissions) == 0


def test_missing_submission_url_shows_error(client):
    response = client.post(
        "/",
        data={
            "student_name": "Shahab Ahmed",
            "registration_number": "CSC418-001",
            "assignment_title": "DevOps Midterm",
            "submission_url": "",
        },
    )

    assert response.status_code == 200
    assert b"Submission URL is required." in response.data
    assert len(submissions) == 0


def test_malformed_url_is_rejected(client):
    response = client.post(
        "/",
        data={
            "student_name": "Shahab Ahmed",
            "registration_number": "CSC418-001",
            "assignment_title": "DevOps Midterm",
            "submission_url": "http://:80",
        },
    )

    assert response.status_code == 200
    assert b"Please enter a valid http/https URL." in response.data
    assert len(submissions) == 0


def test_url_with_invalid_port_is_rejected(client):
    response = client.post(
        "/",
        data={
            "student_name": "Shahab Ahmed",
            "registration_number": "CSC418-001",
            "assignment_title": "DevOps Midterm",
            "submission_url": "https://example.com:70000/project",
        },
    )

    assert response.status_code == 200
    assert b"Please enter a valid http/https URL." in response.data
    assert len(submissions) == 0


def test_non_http_url_is_rejected(client):
    response = client.post(
        "/",
        data={
            "student_name": "Shahab Ahmed",
            "registration_number": "CSC418-001",
            "assignment_title": "DevOps Midterm",
            "submission_url": "ftp://example.com/project",
        },
    )

    assert response.status_code == 200
    assert b"Please enter a valid http/https URL." in response.data
    assert len(submissions) == 0


def test_url_with_whitespace_is_rejected(client):
    response = client.post(
        "/",
        data={
            "student_name": "Shahab Ahmed",
            "registration_number": "CSC418-001",
            "assignment_title": "DevOps Midterm",
            "submission_url": "http://exa mple.com",
        },
    )

    assert response.status_code == 200
    assert b"Please enter a valid http/https URL." in response.data
    assert len(submissions) == 0