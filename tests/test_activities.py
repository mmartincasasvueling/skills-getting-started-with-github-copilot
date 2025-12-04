from fastapi.testclient import TestClient
from src.app import app, activities
import copy

client = TestClient(app)


def snapshot_activities():
    # Deep copy participants lists to restore state after tests
    return {k: copy.deepcopy(v["participants"]) for k, v in activities.items()}


def restore_activities(snapshot):
    for name, participants in snapshot.items():
        activities[name]["participants"] = participants


def test_get_activities_returns_dict():
    resp = client.get("/activities")
    assert resp.status_code == 200
    json = resp.json()
    assert isinstance(json, dict)
    # ensure at least one known activity present
    assert "Chess Club" in json


def test_signup_and_unregister_participant():
    snapshot = snapshot_activities()
    activity = "Programming Class"
    email = "pytest_student@example.com"

    # Ensure not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Participant appears in GET
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    assert email in resp2.json()[activity]["participants"]

    # Unregister
    resp3 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp3.status_code == 200
    assert "Unregistered" in resp3.json().get("message", "")

    # Participant removed in GET
    resp4 = client.get("/activities")
    assert email not in resp4.json()[activity]["participants"]

    # Restore original state
    restore_activities(snapshot)