import pytest
from backend import create_app
from backend.database import db
from config import TestConfig

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_job_creation_success(client):
    response = client.post(
        "/api/jobs",
        json={
            "title": "Python Developer",
            "description": "Looking for a seasoned Python Flask backend engineer.",
            "required_skills": ["Python", "Flask", "SQL"],
            "preferred_skills": ["Docker", "AWS"],
            "experience": "2-4 years",
            "education": "Bachelor's Degree"
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["job_id"] is not None
    assert data["job"]["title"] == "Python Developer"
    assert "Python" in data["job"]["required_skills"]

def test_job_creation_missing_title(client):
    response = client.post(
        "/api/jobs",
        json={
            "title": "",
            "description": "Valid description exceeding twenty characters.",
            "required_skills": ["Python"]
        }
    )
    assert response.status_code == 400
    assert response.get_json()["success"] is False

def test_job_creation_short_description(client):
    response = client.post(
        "/api/jobs",
        json={
            "title": "Backend Dev",
            "description": "Too short",
            "required_skills": ["Python"]
        }
    )
    assert response.status_code == 400
    assert "at least 20 characters" in response.get_json()["error"]

def test_job_creation_empty_skills(client):
    response = client.post(
        "/api/jobs",
        json={
            "title": "Backend Dev",
            "description": "Valid description exceeding twenty characters.",
            "required_skills": []
        }
    )
    assert response.status_code == 400
    assert "required skill" in response.get_json()["error"]

def test_get_jobs_and_single_job(client):
    res_post = client.post(
        "/api/jobs",
        json={
            "title": "DevOps Engineer",
            "description": "Responsible for managing AWS infrastructure and CI/CD pipelines.",
            "required_skills": ["Docker", "Kubernetes", "AWS"]
        }
    )
    job_id = res_post.get_json()["job_id"]

    # List jobs
    res_list = client.get("/api/jobs")
    assert res_list.status_code == 200
    assert res_list.get_json()["count"] >= 1

    # Get single job
    res_single = client.get(f"/api/jobs/{job_id}")
    assert res_single.status_code == 200
    assert res_single.get_json()["job"]["title"] == "DevOps Engineer"

def test_update_job(client):
    res_post = client.post(
        "/api/jobs",
        json={
            "title": "Initial Title",
            "description": "Initial description with more than twenty characters.",
            "required_skills": ["Python"]
        }
    )
    job_id = res_post.get_json()["job_id"]

    res_put = client.put(
        f"/api/jobs/{job_id}",
        json={
            "title": "Updated Title",
            "experience": "5+ years"
        }
    )
    assert res_put.status_code == 200
    assert res_put.get_json()["job"]["title"] == "Updated Title"
    assert res_put.get_json()["job"]["experience"] == "5+ years"

def test_delete_job(client):
    res_post = client.post(
        "/api/jobs",
        json={
            "title": "Job to Delete",
            "description": "Job description for deletion test purpose.",
            "required_skills": ["SQL"]
        }
    )
    job_id = res_post.get_json()["job_id"]

    res_del = client.delete(f"/api/jobs/{job_id}")
    assert res_del.status_code == 200

    # Verify 404 on get
    res_get = client.get(f"/api/jobs/{job_id}")
    assert res_get.status_code == 404
