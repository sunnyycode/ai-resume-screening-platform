import json
from flask import Blueprint, request, jsonify, current_app
from backend.database import db
from backend.models import Job, Resume, MatchResult
from backend.services.scoring import CandidateScorer

candidates_bp = Blueprint("candidates", __name__, url_prefix="/api")

@candidates_bp.route("/match/quick", methods=["POST"])
def quick_match():
    """
    Live interactive matching between arbitrary job description and resume text.
    Does not persist to database - ideal for testing, interactive demos, and live evaluation.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON payload."}), 400

    job_desc = data.get("job_description", "").strip()
    resume_text = data.get("resume_text", "").strip()
    req_skills = data.get("required_skills", [])

    if not job_desc:
        return jsonify({"success": False, "error": "Job description is required."}), 400
    if not resume_text:
        return jsonify({"success": False, "error": "Resume text is required."}), 400

    if isinstance(req_skills, str):
        req_skills = [s.strip() for s in req_skills.split(",") if s.strip()]

    scorer = CandidateScorer(
        weight_tfidf=current_app.config.get("WEIGHT_TFIDF", 0.30),
        weight_semantic=current_app.config.get("WEIGHT_SEMANTIC", 0.40),
        weight_skill=current_app.config.get("WEIGHT_SKILL", 0.30)
    )

    evaluation = scorer.evaluate_candidate(
        job_description=job_desc,
        required_skills=req_skills,
        resume_text=resume_text,
        preferred_skills=data.get("preferred_skills", [])
    )

    return jsonify({
        "success": True,
        "evaluation": evaluation
    }), 200

@candidates_bp.route("/match/<int:job_id>/<int:resume_id>", methods=["POST"])
def match_job_and_resume(job_id: int, resume_id: int):
    """
    Run NLP and skill matching pipeline for a specific job and resume.
    Saves or updates match result in SQLite.
    """
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"success": False, "error": f"Job {job_id} not found."}), 404

    resume = db.session.get(Resume, resume_id)
    if not resume:
        return jsonify({"success": False, "error": f"Resume {resume_id} not found."}), 404

    scorer = CandidateScorer(
        weight_tfidf=current_app.config.get("WEIGHT_TFIDF", 0.30),
        weight_semantic=current_app.config.get("WEIGHT_SEMANTIC", 0.40),
        weight_skill=current_app.config.get("WEIGHT_SKILL", 0.30)
    )

    evaluation = scorer.evaluate_candidate(
        job_description=job.description,
        required_skills=job.get_required_skills_list(),
        resume_text=resume.extracted_text,
        preferred_skills=job.get_preferred_skills_list()
    )

    # Check for existing match record or create new
    match = MatchResult.query.filter_by(job_id=job.id, resume_id=resume.id).first()
    if not match:
        match = MatchResult(job_id=job.id, resume_id=resume.id)
        db.session.add(match)

    match.tfidf_score = evaluation["tfidf_score"]
    match.semantic_score = evaluation["semantic_score"]
    match.skill_score = evaluation["skill_score"]
    match.overall_score = evaluation["overall_score"]
    match.matched_skills = json.dumps(evaluation["matched_skills"])
    match.missing_skills = json.dumps(evaluation["missing_skills"])
    match.strong_areas = json.dumps(evaluation["strong_areas"])
    match.weak_areas = json.dumps(evaluation["weak_areas"])

    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Matching completed successfully.",
            "match_result": match.to_dict(),
            "evaluation": evaluation
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Failed to save match result: {str(e)}"}), 500

@candidates_bp.route("/jobs/<int:job_id>/match-all", methods=["POST"])
def match_all_candidates_for_job(job_id: int):
    """
    Run matching pipeline for all existing resumes in the database against this job.
    """
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"success": False, "error": f"Job {job_id} not found."}), 404

    resumes = Resume.query.all()
    if not resumes:
        return jsonify({"success": True, "message": "No resumes available to match.", "matched_count": 0}), 200

    scorer = CandidateScorer(
        weight_tfidf=current_app.config.get("WEIGHT_TFIDF", 0.30),
        weight_semantic=current_app.config.get("WEIGHT_SEMANTIC", 0.40),
        weight_skill=current_app.config.get("WEIGHT_SKILL", 0.30)
    )

    matched_count = 0
    for resume in resumes:
        evaluation = scorer.evaluate_candidate(
            job_description=job.description,
            required_skills=job.get_required_skills_list(),
            resume_text=resume.extracted_text,
            preferred_skills=job.get_preferred_skills_list()
        )

        match = MatchResult.query.filter_by(job_id=job.id, resume_id=resume.id).first()
        if not match:
            match = MatchResult(job_id=job.id, resume_id=resume.id)
            db.session.add(match)

        match.tfidf_score = evaluation["tfidf_score"]
        match.semantic_score = evaluation["semantic_score"]
        match.skill_score = evaluation["skill_score"]
        match.overall_score = evaluation["overall_score"]
        match.matched_skills = json.dumps(evaluation["matched_skills"])
        match.missing_skills = json.dumps(evaluation["missing_skills"])
        match.strong_areas = json.dumps(evaluation["strong_areas"])
        match.weak_areas = json.dumps(evaluation["weak_areas"])
        matched_count += 1

    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": f"Successfully evaluated and ranked {matched_count} candidates.",
            "matched_count": matched_count
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Failed during batch match: {str(e)}"}), 500

@candidates_bp.route("/jobs/<int:job_id>/candidates", methods=["GET"])
def get_job_candidates(job_id: int):
    """
    Retrieve ranked candidates for a specific job posting.
    Supports query parameters:
    - min_score: float (e.g. ?min_score=70)
    - skill: string (e.g. ?skill=Python)
    - sort: 'desc' or 'asc' (default: 'desc')
    - search: string (matches candidate name)
    """
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"success": False, "error": f"Job {job_id} not found."}), 404

    min_score = request.args.get("min_score", type=float)
    skill_filter = request.args.get("skill", "").strip().lower()
    search = request.args.get("search", "").strip().lower()
    sort_dir = request.args.get("sort", "desc").lower()

    query = MatchResult.query.filter_by(job_id=job.id)

    if min_score is not None:
        query = query.filter(MatchResult.overall_score >= min_score)

    if sort_dir == "asc":
        query = query.order_by(MatchResult.overall_score.asc())
    else:
        query = query.order_by(MatchResult.overall_score.desc())

    matches = query.all()
    candidates = []

    for rank, match in enumerate(matches, start=1):
        candidate_data = match.to_dict()
        candidate_data["rank"] = rank

        # Filter by skill if requested
        if skill_filter:
            matched_lower = [s.lower() for s in candidate_data["matched_skills"]]
            if not any(skill_filter in s for s in matched_lower):
                continue

        # Filter by candidate name search
        if search:
            c_name = candidate_data.get("candidate_name", "").lower()
            if search not in c_name:
                continue

        candidates.append(candidate_data)

    return jsonify({
        "success": True,
        "job": job.to_dict(),
        "total_candidates": len(candidates),
        "candidates": candidates
    }), 200

@candidates_bp.route("/candidates/<int:candidate_id>", methods=["GET"])
def get_candidate(candidate_id: int):
    """
    Get candidate resume details and all matches.
    """
    resume = db.session.get(Resume, candidate_id)
    if not resume:
        return jsonify({"success": False, "error": f"Candidate {candidate_id} not found."}), 404

    matches = MatchResult.query.filter_by(resume_id=resume.id).all()
    return jsonify({
        "success": True,
        "candidate": resume.to_dict(include_text=True),
        "match_history": [m.to_dict() for m in matches]
    }), 200

@candidates_bp.route("/match/<int:match_id>", methods=["GET"])
def get_match_detail(match_id: int):
    """Get full deep-dive explanation for a single match evaluation."""
    match = db.session.get(MatchResult, match_id)
    if not match:
        return jsonify({"success": False, "error": f"Match record {match_id} not found."}), 404

    data = match.to_dict()
    # Add resume text snippet
    if match.resume:
        data["resume_text_preview"] = match.resume.extracted_text[:1000] + ("..." if len(match.resume.extracted_text) > 1000 else "")
    if match.job:
        data["job_details"] = match.job.to_dict()

    return jsonify({
        "success": True,
        "match": data
    }), 200

@candidates_bp.route("/jobs/<int:job_id>/export", methods=["GET"])
def export_job_candidates_csv(job_id: int):
    """
    Export ranked candidate report for a job as downloadable CSV.
    """
    import csv
    import io
    from flask import Response

    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"success": False, "error": f"Job {job_id} not found."}), 404

    matches = (
        MatchResult.query.filter_by(job_id=job.id)
        .order_by(MatchResult.overall_score.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Candidate Name", "Email", "Phone",
        "Overall Score (%)", "TF-IDF (%)", "Semantic (%)", "Skill (%)",
        "Matched Skills", "Missing Skills", "Fit Recommendation"
    ])

    for rank, m in enumerate(matches, start=1):
        score = m.overall_score
        if score >= 80:
            rec = "Strong Match"
        elif score >= 60:
            rec = "Moderate Fit"
        else:
            rec = "Low Fit"

        writer.writerow([
            rank,
            m.resume.candidate_name if m.resume else "Unknown",
            m.resume.candidate_email if m.resume else "",
            m.resume.candidate_phone if m.resume else "",
            score,
            round(m.tfidf_score * 100, 1),
            round(m.semantic_score * 100, 1),
            round(m.skill_score * 100, 1),
            ", ".join(m.get_matched_skills_list()),
            ", ".join(m.get_missing_skills_list()),
            rec
        ])

    csv_data = output.getvalue()
    filename = f"candidates_job_{job_id}_{job.title.lower().replace(' ', '_')[:30]}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@candidates_bp.route("/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """Retrieve overall analytics for the recruiter dashboard including skill frequency."""
    try:
        from collections import Counter
        from backend.services.skill_matcher import extract_skills_from_text

        total_jobs = Job.query.count()
        total_resumes = Resume.query.count()
        total_matches = MatchResult.query.count()

        # Calculate average match score
        matches = MatchResult.query.all()
        avg_score = round(sum(m.overall_score for m in matches) / len(matches), 1) if matches else 0.0

        # Top 5 ranked matches across the system
        top_matches = (
            MatchResult.query.order_by(MatchResult.overall_score.desc())
            .limit(5)
            .all()
        )

        # Aggregate top in-demand skills from all jobs
        all_jobs = Job.query.all()
        job_skill_counter = Counter()
        for j in all_jobs:
            for s in j.get_required_skills_list():
                job_skill_counter[s] += 1

        # Aggregate skills from uploaded candidate pool
        all_resumes = Resume.query.all()
        resume_skill_counter = Counter()
        for r in all_resumes:
            for s in extract_skills_from_text(r.extracted_text):
                resume_skill_counter[s] += 1

        top_demanded_skills = [
            {"skill": k, "count": v} for k, v in job_skill_counter.most_common(6)
        ]
        top_candidate_skills = [
            {"skill": k, "count": v} for k, v in resume_skill_counter.most_common(6)
        ]

        return jsonify({
            "success": True,
            "stats": {
                "total_jobs": total_jobs,
                "total_candidates": total_resumes,
                "total_evaluations": total_matches,
                "average_match_score": avg_score,
                "top_demanded_skills": top_demanded_skills,
                "top_candidate_skills": top_candidate_skills
            },
            "top_candidates": [m.to_dict() for m in top_matches]
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to retrieve dashboard stats: {str(e)}"}), 500
