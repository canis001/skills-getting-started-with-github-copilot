import os
import sys
from urllib.parse import quote

from fastapi.testclient import TestClient

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

from app import app  # noqa: E402

client = TestClient(app)


def test_get_activities_returns_data():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "participants" in activities["Chess Club"]


def test_signup_and_unregister_participant():
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    activity_path = quote(activity_name, safe="")

    signup_response = client.post(f"/activities/{activity_path}/signup", params={"email": email})
    assert signup_response.status_code == 200
    assert "Signed up" in signup_response.json()["message"]

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    assert email in activities_response.json()[activity_name]["participants"]

    unregister_response = client.delete(f"/activities/{activity_path}/signup", params={"email": email})
    assert unregister_response.status_code == 200
    assert "Unregistered" in unregister_response.json()["message"]

    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    activity_path = quote(activity_name, safe="")

    response = client.post(f"/activities/{activity_path}/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_missing_participant_returns_404():
    activity_name = "Gym Class"
    email = "missingstudent@mergington.edu"
    activity_path = quote(activity_name, safe="")

    response = client.delete(f"/activities/{activity_path}/signup", params={"email": email})
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
