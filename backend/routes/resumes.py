import os
import uuid
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from backend.database import db
from backend.models import Resume, Job, MatchResult
from backend.services.resume_parser import ResumeParser, ResumeParserError
from backend.services.scoring import CandidateScorer
from backend.utils.validators import validate_file_extension

resumes_bp = Blueprint("resumes", __name__, url_prefix="/api/resumes")

@resumes_bp.route("/upload", methods=["POST"])
def upload_resume():
    """
    Upload and parse resume file (PDF, DOCX, TXT).
    Extracts text, contact details, and stores in database.
    Optional form field: job_id to immediately match against a specific job posting.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "Resume file is required. Key 'file' missing in multipart form."}), 400

    uploaded_file = request.files["file"]
    if not uploaded_file or uploaded_file.filename == "":
        return jsonify({"success": False, "error": "No file selected for upload."}), 400

    allowed_exts = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "docx", "txt"})
    if not validate_file_extension(uploaded_file.filename, allowed_exts):
        return jsonify({
            "success": False,
            "error": f"Invalid file format '{uploaded_file.filename}'. Allowed formats: {', '.join(allowed_exts)}."
        }), 400

    # Ensure upload directory exists
    upload_folder = current_app.config.get("UPLOAD_FOLDER")
    os.makedirs(upload_folder, exist_ok=True)

    original_filename = secure_filename(uploaded_file.filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{original_filename}"
    file_path = os.path.join(upload_folder, unique_filename)

    try:
        uploaded_file.save(file_path)
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to save file: {str(e)}"}), 500

    # Parse and extract text
    try:
        extracted_text = ResumeParser.extract_text_from_file(file_path)
    except ResumeParserError as pe:
        # Clean up file on parsing failure
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"success": False, "error": str(pe)}), 400
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"success": False, "error": f"Unexpected parsing error: {str(e)}"}), 500

    # Extract metadata or take override from form
    candidate_metadata = ResumeParser.extract_candidate_metadata(extracted_text, original_filename)
    form_candidate_name = request.form.get("candidate_name", "").strip()
    candidate_name = form_candidate_name if form_candidate_name else candidate_metadata["name"]
    candidate_email = request.form.get("candidate_email", "").strip() or candidate_metadata["email"]
    candidate_phone = request.form.get("candidate_phone", "").strip() or candidate_metadata["phone"]

    try:
        resume = Resume(
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_phone=candidate_phone,
            filename=original_filename,
            file_path=file_path,
            extracted_text=extracted_text
        )
        db.session.add(resume)
        db.session.commit()

        response_data = {
            "success": True,
            "message": "Resume uploaded and parsed successfully.",
            "resume": resume.to_dict(include_text=False)
        }

        # Check if caller requested automatic matching with a job_id
        job_id_param = request.form.get("job_id")
        if job_id_param:
            try:
                job_id = int(job_id_param)
                job = db.session.get(Job, job_id)
                if job:
                    scorer = CandidateScorer(
                        weight_tfidf=current_app.config.get("WEIGHT_TFIDF", 0.30),
                        weight_semantic=current_app.config.get("WEIGHT_SEMANTIC", 0.40),
                        weight_skill=current_app.config.get("WEIGHT_SKILL", 0.30)
                    )
                    eval_result = scorer.evaluate_candidate(
                        job_description=job.description,
                        required_skills=job.get_required_skills_list(),
                        resume_text=resume.extracted_text,
                        preferred_skills=job.get_preferred_skills_list()
                    )

                    # Persist match result
                    match = MatchResult(
                        job_id=job.id,
                        resume_id=resume.id,
                        tfidf_score=eval_result["tfidf_score"],
                        semantic_score=eval_result["semantic_score"],
                        skill_score=eval_result["skill_score"],
                        overall_score=eval_result["overall_score"],
                        matched_skills=json.dumps(eval_result["matched_skills"]),
                        missing_skills=json.dumps(eval_result["missing_skills"]),
                        strong_areas=json.dumps(eval_result["strong_areas"]),
                        weak_areas=json.dumps(eval_result["weak_areas"])
                    )
                    db.session.add(match)
                    db.session.commit()
                    response_data["match_result"] = match.to_dict()
                    response_data["match_evaluation"] = eval_result
            except Exception as me:
                db.session.rollback()
                current_app.logger.error(f"Auto match failed on upload: {me}")

        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"success": False, "error": f"Failed to persist resume: {str(e)}"}), 500

@resumes_bp.route("", methods=["GET"])
def list_resumes():
    """Retrieve all uploaded candidate resumes."""
    try:
        resumes = Resume.query.order_by(Resume.uploaded_at.desc()).all()
        return jsonify({
            "success": True,
            "count": len(resumes),
            "resumes": [r.to_dict(include_text=False) for r in resumes]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to retrieve resumes: {str(e)}"}), 500

@resumes_bp.route("/<int:resume_id>", methods=["GET"])
def get_resume(resume_id: int):
    """Retrieve single resume with full extracted text."""
    resume = db.session.get(Resume, resume_id)
    if not resume:
        return jsonify({"success": False, "error": f"Resume with ID {resume_id} not found."}), 404

    return jsonify({
        "success": True,
        "resume": resume.to_dict(include_text=True)
    }), 200

@resumes_bp.route("/<int:resume_id>", methods=["DELETE"])
def delete_resume(resume_id: int):
    """Delete candidate resume and remove file from disk."""
    resume = db.session.get(Resume, resume_id)
    if not resume:
        return jsonify({"success": False, "error": f"Resume with ID {resume_id} not found."}), 404

    try:
        # Delete file if exists
        if os.path.exists(resume.file_path):
            try:
                os.remove(resume.file_path)
            except Exception:
                pass

        db.session.delete(resume)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Resume {resume_id} and associated file deleted successfully."
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Failed to delete resume: {str(e)}"}), 500
