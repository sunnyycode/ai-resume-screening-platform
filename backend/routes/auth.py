from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models import User
from backend.utils.validators import is_valid_email, validate_password_strength, generate_jwt_token, token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user / recruiter."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON body provided."}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "recruiter").strip()

    if not name:
        return jsonify({"success": False, "error": "Name is required."}), 400

    if not is_valid_email(email):
        return jsonify({"success": False, "error": "A valid email address is required."}), 400

    valid_pwd, pwd_msg = validate_password_strength(password)
    if not valid_pwd:
        return jsonify({"success": False, "error": pwd_msg}), 400

    # Check for existing user
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "An account with this email already exists."}), 400

    try:
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = generate_jwt_token(user.id, user.role)

        return jsonify({
            "success": True,
            "message": "User registered successfully.",
            "token": token,
            "user": user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Failed to register user: {str(e)}"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT session token."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON body provided."}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "error": "Both email and password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"success": False, "error": "Invalid email or password."}), 401

    token = generate_jwt_token(user.id, user.role)

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": user.to_dict()
    }), 200

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    """Retrieve profile of currently authenticated user."""
    return jsonify({
        "success": True,
        "user": current_user.to_dict()
    }), 200
