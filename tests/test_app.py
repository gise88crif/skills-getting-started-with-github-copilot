import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_data():
    # Reset participants to initial state for isolation
    for name, data in activities.items():
        # Keep original seeded participants for reproducibility
        # (Alternatively we could deep copy an ORIGINAL dict.)
        pass
    yield


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_success():
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    assert email not in activities[activity]["participants"]
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    payload = response.json()
    assert "Signed up" in payload["message"]


def test_signup_duplicate():
    # Use an existing participant
    activity = "Programming Class"
    existing_email = activities[activity]["participants"][0]
    response = client.post(f"/activities/{activity}/signup?email={existing_email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_invalid_activity():
    response = client.post("/activities/Unknown Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_success():
    activity = "Gym Class"
    existing_email = activities[activity]["participants"][0]
    response = client.delete(f"/activities/{activity}/unregister?email={existing_email}")
    assert response.status_code == 200
    assert existing_email not in activities[activity]["participants"]
    assert "Unregistered" in response.json()["message"]


def test_unregister_not_registered():
    activity = "Gym Class"
    email = "notregistered@mergington.edu"
    assert email not in activities[activity]["participants"]
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not registered for this activity"


def test_unregister_invalid_activity():
    response = client.delete("/activities/Unknown/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"