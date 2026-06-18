import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as activities_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities_store)
    yield
    activities_store.clear()
    activities_store.update(copy.deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert "participants" in data["Chess Club"]
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities_store[activity_name]["participants"]


def test_signup_for_activity_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities_store[activity_name]["participants"]


def test_activity_endpoints_invalid_activity_return_404():
    # Arrange
    invalid_activity = "Nonexistent Club"
    email = "teststudent@mergington.edu"

    # Act
    signup_response = client.post(
        f"/activities/{invalid_activity}/signup",
        params={"email": email},
    )
    delete_response = client.delete(
        f"/activities/{invalid_activity}/participants",
        params={"email": email},
    )

    # Assert
    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"

    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Activity not found"
