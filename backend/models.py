import json
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import db

class User(db.Model):
    """Recruiter / User model."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="recruiter", nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    jobs = db.relationship("Job", backref="creator", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        """Hashes the password with salt."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifies candidate password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Job(db.Model):
    """Job posting created by recruiters."""
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)  # Stored as JSON list string
    preferred_skills = db.Column(db.Text, default="[]")   # Stored as JSON list string
    experience = db.Column(db.String(100), default="0-2 years")
    education = db.Column(db.String(100), default="Bachelor's Degree")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    matches = db.relationship("MatchResult", backref="job", lazy=True, cascade="all, delete-orphan")

    def get_required_skills_list(self):
        try:
            return json.loads(self.required_skills) if self.required_skills else []
        except Exception:
            return [s.strip() for s in self.required_skills.split(",") if s.strip()]

    def get_preferred_skills_list(self):
        try:
            return json.loads(self.preferred_skills) if self.preferred_skills else []
        except Exception:
            return [s.strip() for s in self.preferred_skills.split(",") if s.strip()]

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "required_skills": self.get_required_skills_list(),
            "preferred_skills": self.get_preferred_skills_list(),
            "experience": self.experience,
            "education": self.education,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Resume(db.Model):
    """Candidate resume entity."""
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    candidate_name = db.Column(db.String(150), nullable=False)
    candidate_email = db.Column(db.String(120), nullable=True)
    candidate_phone = db.Column(db.String(50), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    matches = db.relationship("MatchResult", backref="resume", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_text=False):
        data = {
            "id": self.id,
            "candidate_name": self.candidate_name,
            "candidate_email": self.candidate_email,
            "candidate_phone": self.candidate_phone,
            "filename": self.filename,
            "file_path": self.file_path,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
        if include_text:
            data["extracted_text"] = self.extracted_text
        return data

class MatchResult(db.Model):
    """Calculated matching metrics between a Job and a Resume."""
    __tablename__ = "match_results"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    tfidf_score = db.Column(db.Float, nullable=False, default=0.0)
    semantic_score = db.Column(db.Float, nullable=False, default=0.0)
    skill_score = db.Column(db.Float, nullable=False, default=0.0)
    overall_score = db.Column(db.Float, nullable=False, default=0.0)
    matched_skills = db.Column(db.Text, default="[]")   # JSON list
    missing_skills = db.Column(db.Text, default="[]")   # JSON list
    strong_areas = db.Column(db.Text, default="[]")     # JSON list
    weak_areas = db.Column(db.Text, default="[]")       # JSON list
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def get_matched_skills_list(self):
        try:
            return json.loads(self.matched_skills) if self.matched_skills else []
        except Exception:
            return []

    def get_missing_skills_list(self):
        try:
            return json.loads(self.missing_skills) if self.missing_skills else []
        except Exception:
            return []

    def get_strong_areas_list(self):
        try:
            return json.loads(self.strong_areas) if self.strong_areas else []
        except Exception:
            return []

    def get_weak_areas_list(self):
        try:
            return json.loads(self.weak_areas) if self.weak_areas else []
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "resume_id": self.resume_id,
            "candidate_name": self.resume.candidate_name if self.resume else "Unknown",
            "candidate_email": self.resume.candidate_email if self.resume else None,
            "candidate_phone": self.resume.candidate_phone if self.resume else None,
            "job_title": self.job.title if self.job else "Unknown",
            "tfidf_score": round(self.tfidf_score, 4),
            "semantic_score": round(self.semantic_score, 4),
            "skill_score": round(self.skill_score, 4),
            "overall_score": round(self.overall_score, 2),
            "matched_skills": self.get_matched_skills_list(),
            "missing_skills": self.get_missing_skills_list(),
            "strong_areas": self.get_strong_areas_list(),
            "weak_areas": self.get_weak_areas_list(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
