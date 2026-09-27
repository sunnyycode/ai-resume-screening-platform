import io
import os
import pytest
from backend import create_app
from backend.database import db
from config import TestConfig

@pytest.fixture
def client(tmp_path):
    # Set isolated upload directory
    TestConfig.UPLOAD_FOLDER = str(tmp_path / "test_uploads")
    os.makedirs(TestConfig.UPLOAD_FOLDER, exist_ok=True)

    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_resume_upload_missing_file(client):
    response = client.post("/api/resumes/upload", data={})
    assert response.status_code == 400
    assert "Resume file is required" in response.get_json()["error"]

def test_resume_upload_invalid_extension(client):
    data = {
        "file": (io.BytesIO(b"fake executable content"), "malicious.exe")
    }
    response = client.post("/api/resumes/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "Invalid file format" in response.get_json()["error"]

def test_full_pipeline_upload_match_and_ranking(client):
    # 1. Create a Job Posting
    job_res = client.post(
        "/api/jobs",
        json={
            "title": "Backend Python Engineer",
            "description": "We are seeking a Python developer with solid Flask and SQL skills.",
            "required_skills": ["Python", "Flask", "SQL"],
            "experience": "1-3 years"
        }
    )
    assert job_res.status_code == 201
    job_id = job_res.get_json()["job_id"]

    # 2. Upload Candidate Resume (TXT)
    resume_content = b"""Alice Engineer
Email: alice@sample.com
Phone: +1-555-010-9988
Experienced Python Developer specializing in Flask web frameworks, PostgreSQL, SQL, and Git.
"""
    upload_res = client.post(
        "/api/resumes/upload",
        data={
            "file": (io.BytesIO(resume_content), "alice_resume.txt"),
            "candidate_name": "Alice Engineer"
        },
        content_type="multipart/form-data"
    )
    assert upload_res.status_code == 201
    resume_id = upload_res.get_json()["resume"]["id"]

    # 3. Trigger Match API
    match_res = client.post(f"/api/match/{job_id}/{resume_id}")
    assert match_res.status_code == 200
    match_data = match_res.get_json()
    assert match_data["success"] is True
    assert match_data["match_result"]["overall_score"] > 40

    # 4. Fetch Ranked Candidates for Job
    rank_res = client.get(f"/api/jobs/{job_id}/candidates")
    assert rank_res.status_code == 200
    ranked = rank_res.get_json()
    assert ranked["total_candidates"] == 1
    assert ranked["candidates"][0]["candidate_name"] == "Alice Engineer"
    assert ranked["candidates"][0]["rank"] == 1

    # 5. Filter Candidates by Score
    filter_res_high = client.get(f"/api/jobs/{job_id}/candidates?min_score=99")
    assert filter_res_high.status_code == 200
    assert len(filter_res_high.get_json()["candidates"]) == 0

    # 6. Check Dashboard Stats
    stats_res = client.get("/api/dashboard/stats")
    assert stats_res.status_code == 200
    stats = stats_res.get_json()["stats"]
    assert stats["total_jobs"] == 1
    assert stats["total_candidates"] == 1
    assert stats["total_evaluations"] == 1
    assert stats["average_match_score"] > 0

    # 7. Delete Resume
    del_res = client.delete(f"/api/resumes/{resume_id}")
    assert del_res.status_code == 200

def test_quick_match_endpoint(client):
    response = client.post(
        "/api/match/quick",
        json={
            "job_description": "We need a Python developer who knows Flask and SQL database architecture.",
            "required_skills": ["Python", "Flask", "SQL"],
            "resume_text": "Experienced Python developer with 3 years in Flask, SQL, and MySQL databases."
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    ev = data["evaluation"]
    assert ev["overall_score"] > 40
    assert "Python" in ev["matched_skills"]
    assert "Flask" in ev["matched_skills"]
    assert "contributions" in ev

def test_export_candidates_csv(client):
    # Create job and verify export header
    job_res = client.post(
        "/api/jobs",
        json={
            "title": "Data Analyst",
            "description": "Looking for a SQL and Python analyst for metrics reporting.",
            "required_skills": ["SQL", "Python"]
        }
    )
    job_id = job_res.get_json()["job_id"]

    export_res = client.get(f"/api/jobs/{job_id}/export")
    assert export_res.status_code == 200
    assert "text/csv" in export_res.headers.get("Content-Type", "")
    assert "attachment;filename=" in export_res.headers.get("Content-Disposition", "")
    csv_text = export_res.data.decode("utf-8")
    assert "Rank,Candidate Name,Email" in csv_text
