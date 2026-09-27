import json
from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models import Job, MatchResult
from backend.utils.validators import validate_job_input

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")

@jobs_bp.route("", methods=["POST"])
def create_job():
    """Create a new job posting."""
    data = request.get_json(silent=True)
    is_valid, err_msg = validate_job_input(data)
    if not is_valid:
        return jsonify({"success": False, "error": err_msg}), 400

    title = data["title"].strip()
    description = data["description"].strip()
    
    # Process required skills into JSON string
    req_skills = data.get("required_skills", [])
    if isinstance(req_skills, str):
        req_skills = [s.strip() for s in req_skills.split(",") if s.strip()]
    elif isinstance(req_skills, list):
        req_skills = [str(s).strip() for s in req_skills if str(s).strip()]

    # Process preferred skills
    pref_skills = data.get("preferred_skills", [])
    if isinstance(pref_skills, str):
        pref_skills = [s.strip() for s in pref_skills.split(",") if s.strip()]
    elif isinstance(pref_skills, list):
        pref_skills = [str(s).strip() for s in pref_skills if str(s).strip()]

    experience = data.get("experience", "0-2 years").strip()
    education = data.get("education", "Bachelor's Degree").strip()
    created_by = data.get("created_by")

    try:
        new_job = Job(
            title=title,
            description=description,
            required_skills=json.dumps(req_skills),
            preferred_skills=json.dumps(pref_skills),
            experience=experience,
            education=education,
            created_by=created_by
        )
        db.session.add(new_job)
        db.session.commit()

        return jsonify({
            "success": True,
            "job_id": new_job.id,
            "message": "Job created successfully",
            "job": new_job.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Failed to create job: {str(e)}"}), 500

@jobs_bp.route("", methods=["GET"])
def list_jobs():
    """List all job postings with candidate matching count."""
    try:
        jobs = Job.query.order_by(Job.created_at.desc()).all()
        result = []
        for job in jobs:
            job_data = job.to_dict()
            job_data["candidate_count"] = MatchResult.query.filter_by(job_id=job.id).count()
            result.append(job_data)
        return jsonify({
            "success": True,
            "count": len(result),
            "jobs": result
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to fetch jobs: {str(e)}"}), 500

@jobs_bp.route("/<int:job_id>", methods=["GET"])
def get_job(job_id: int):
    """Retrieve details of a specific job."""
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"success": False, "error": f"Job with ID {job_id} not found."}), 404

    job_data = job.to_dict()
    job_data["candidate_count"] = MatchResult.query.filter_by(job_id=job.id).count()
    return jsonify({
        "success": True,
        "job": job_data
    }), 200

@jobs_bp.route("/<int:job_id>", methods=["PUT"])
def update_job(job_id: int):
    """Update an existing job posting."""
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"success": False, "error": f"Job with ID {job_id} not found."}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON body provided."}), 400

    if "title" in data:
        if not data["title"].strip():
            return jsonify({"success": False, "error": "Job title cannot be empty."}), 400
        job.title = data["title"].strip()

    if "description" in data:
        if len(data["description"].strip()) < 20:
            return jsonify({"success": False, "error": "Job description must be at least 20 characters."}), 400
        job.description = data["description"].strip()

    if "required_skills" in data:
        req = data["required_skills"]
        if isinstance(req, str):
            req = [s.strip() for s in req.split(",") if s.strip()]
        job.required_skills = json.dumps(req)

    if "preferred_skills" in data:
        pref = data["preferred_skills"]
        if isinstance(pref, str):
            pref = [s.strip() for s in pref.split(",") if s.strip()]
        job.preferred_skills = json.dumps(pref)

    if "experience" in data:
        job.experience = data["experience"].strip()

    if "education" in data:
        job.education = data["education"].strip()

    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Job updated successfully.",
            "job": job.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Failed to update job: {str(e)}"}), 500

@jobs_bp.route("/<int:job_id>", methods=["DELETE"])
def delete_job(job_id: int):
    """Delete a job posting and its associated match evaluations."""
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"success": False, "error": f"Job with ID {job_id} not found."}), 404

    try:
        db.session.delete(job)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Job {job_id} and its associated matches deleted successfully."
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Failed to delete job: {str(e)}"}), 500
