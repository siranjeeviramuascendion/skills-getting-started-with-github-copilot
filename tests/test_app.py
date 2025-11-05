import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that the root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test that the activities endpoint returns the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    # Verify activity structure
    activity = activities["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_signup_for_activity_success():
    """Test successful signup for an activity"""
    email = "new.student@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    
    # Verify student was added
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]

def test_signup_for_activity_duplicate():
    """Test that a student cannot sign up for the same activity twice"""
    email = "duplicate@mergington.edu"
    # First signup should succeed
    response = client.post(f"/activities/Programming Class/signup?email={email}")
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(f"/activities/Programming Class/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"

def test_signup_for_nonexistent_activity():
    """Test signup for an activity that doesn't exist"""
    response = client.post("/activities/Nonexistent Club/signup?email=student@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_participant_success():
    """Test successful unregistration from an activity"""
    # First add a student
    email = "todelete@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Then remove them
    response = client.delete(f"/activities/Chess Club/participants/{email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    
    # Verify student was removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]

def test_unregister_nonexistent_participant():
    """Test unregistering a student who isn't registered"""
    email = "notregistered@mergington.edu"
    response = client.delete(f"/activities/Chess Club/participants/{email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"

def test_unregister_from_nonexistent_activity():
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete("/activities/Nonexistent Club/participants/student@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"