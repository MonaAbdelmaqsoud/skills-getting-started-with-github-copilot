from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

TEST_ACTIVITY = "Chess Club"
TEST_EMAIL = "pytest_tester@mergington.edu"


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert TEST_ACTIVITY in data
    assert "participants" in data[TEST_ACTIVITY]


def test_signup_and_unregister_flow():
    # Ensure clean state
    activities = client.get("/activities").json()
    participants = activities[TEST_ACTIVITY]["participants"]
    if TEST_EMAIL in participants:
        client.delete(f"/activities/{TEST_ACTIVITY}/unregister?email={TEST_EMAIL}")

    # Sign up
    res = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert res.status_code == 200
    assert "Signed up" in res.json().get("message", "")

    # Verify present
    activities = client.get("/activities").json()
    assert TEST_EMAIL in activities[TEST_ACTIVITY]["participants"]

    # Unregister
    res = client.delete(f"/activities/{TEST_ACTIVITY}/unregister?email={TEST_EMAIL}")
    assert res.status_code == 200
    assert "Unregistered" in res.json().get("message", "")

    # Verify removed
    activities = client.get("/activities").json()
    assert TEST_EMAIL not in activities[TEST_ACTIVITY]["participants"]


def test_signup_already_exists():
    # Add email
    res = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert res.status_code == 200

    # Second signup should fail with 400
    res = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert res.status_code == 400

    # Cleanup
    client.delete(f"/activities/{TEST_ACTIVITY}/unregister?email={TEST_EMAIL}")


def test_unregister_not_found():
    # Ensure it's not present
    client.delete(f"/activities/{TEST_ACTIVITY}/unregister?email={TEST_EMAIL}")

    # Try again — should get 404
    res = client.delete(f"/activities/{TEST_ACTIVITY}/unregister?email={TEST_EMAIL}")
    assert res.status_code == 404


def test_activity_not_found():
    res = client.post("/activities/NoSuchActivity/signup?email=test@example.com")
    assert res.status_code == 404

    res = client.delete("/activities/NoSuchActivity/unregister?email=test@example.com")
    assert res.status_code == 404
