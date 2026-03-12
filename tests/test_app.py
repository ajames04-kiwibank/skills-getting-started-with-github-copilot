"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test."""
    original = {
        name: {**details, "participants": list(details["participants"])}
        for name, details in activities.items()
    }
    yield
    # Restore original state
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities_returns_200():
    """Arrange: API client ready. Act: GET /activities. Assert: 200 response."""
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200


def test_get_activities_returns_dict():
    """Arrange: API client ready. Act: GET /activities. Assert: response is a dict."""
    # Act
    response = client.get("/activities")
    # Assert
    data = response.json()
    assert isinstance(data, dict)


def test_get_activities_contains_expected_fields():
    """Arrange: API client ready. Act: GET /activities. Assert: each activity has required fields."""
    # Act
    response = client.get("/activities")
    data = response.json()
    # Assert
    for name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details


def test_signup_for_activity_success():
    """Arrange: a valid activity and email. Act: POST signup. Assert: 200 and success message."""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    # Assert
    assert response.status_code == 200
    assert "message" in response.json()


def test_signup_adds_participant():
    """Arrange: a valid activity and email. Act: POST signup. Assert: email in participants."""
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    # Act
    client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    response = client.get("/activities")
    data = response.json()
    assert email in data[activity_name]["participants"]


def test_signup_prevents_duplicate():
    """Arrange: an email already in participants. Act: POST signup again. Assert: 400 error."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already registered
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 400


def test_signup_for_nonexistent_activity():
    """Arrange: a nonexistent activity name. Act: POST signup. Assert: 404 error."""
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404


def test_unregister_from_activity_success():
    """Arrange: an email in participants. Act: DELETE signup. Assert: 200 and success message."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert "message" in response.json()


def test_unregister_removes_participant():
    """Arrange: an email in participants. Act: DELETE signup. Assert: email removed."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    # Act
    client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity_name]["participants"]


def test_unregister_nonregistered_student():
    """Arrange: an email not in participants. Act: DELETE signup. Assert: 400 error."""
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 400
