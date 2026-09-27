import re
import os
import jwt
from functools import wraps
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, current_app
from backend.models import User

# Email regex pattern
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

def is_valid_email(email: str) -> bool:
    """Validate email address format."""
    if not email or not isinstance(email, str):
        return False
    return bool(re.match(EMAIL_REGEX, email.strip()))

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password requirements:
    - At least 6 characters
    """
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""

def validate_job_input(data: dict) -> tuple[bool, str]:
    """Validate job creation and update payload."""
    if not data or not isinstance(data, dict):
        return False, "Invalid JSON payload."
    
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    required_skills = data.get("required_skills")

    if not title:
        return False, "Job title is required and cannot be empty."
    if len(title) > 200:
        return False, "Job title must not exceed 200 characters."

    if not description:
        return False, "Job description is required and cannot be empty."
    if len(description) < 20:
        return False, "Job description must be at least 20 characters long."

    if not required_skills:
        return False, "At least one required skill must be provided."
    if not isinstance(required_skills, (list, str)):
        return False, "Required skills must be an array of strings or comma-separated string."

    return True, ""

def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """Check if filename has an allowed extension."""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions

def generate_jwt_token(user_id: int, role: str) -> str:
    """Generate a JWT token for authenticated sessions."""
    secret = current_app.config.get("JWT_SECRET", "default-jwt-secret")
    exp_hours = current_app.config.get("JWT_EXPIRATION_HOURS", 24)
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=exp_hours)
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def decode_jwt_token(token: str) -> dict:
    """Decode and verify JWT token."""
    secret = current_app.config.get("JWT_SECRET", "default-jwt-secret")
    return jwt.decode(token, secret, algorithms=["HS256"])

def token_required(f):
    """Decorator to require JWT authentication for API routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({
                "success": False,
                "error": "Authorization token is missing."
            }), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "success": False,
                "error": "Invalid token format. Expected 'Bearer <token>'."
            }), 401

        token = parts[1]
        try:
            payload = decode_jwt_token(token)
            current_user = db.session.get(User, payload["sub"])
            if not current_user:
                return jsonify({
                    "success": False,
                    "error": "User associated with token no longer exists."
                }), 401
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "error": "Session token has expired. Please log in again."
            }), 401
        except (jwt.InvalidTokenError, Exception) as e:
            return jsonify({
                "success": False,
                "error": f"Invalid session token: {str(e)}"
            }), 401

        return f(current_user, *args, **kwargs)
    return decorated
