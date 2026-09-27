# Routes package
from backend.routes.auth import auth_bp
from backend.routes.jobs import jobs_bp
from backend.routes.resumes import resumes_bp
from backend.routes.candidates import candidates_bp

__all__ = ["auth_bp", "jobs_bp", "resumes_bp", "candidates_bp"]
