import os
from flask import Flask, jsonify, send_from_directory
from backend.database import db
from config import Config

def create_app(config_class=Config):
    """
    Application factory pattern to create and configure the Flask app.
    Enables isolated testing environments and clean dependency injection.
    """
    # Base directory paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    frontend_dir = os.path.join(base_dir, "frontend")

    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path=""
    )
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Ensure uploads and instance directories exist
    os.makedirs(app.config.get("UPLOAD_FOLDER", os.path.join(base_dir, "uploads")), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "instance"), exist_ok=True)

    # Register blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.jobs import jobs_bp
    from backend.routes.resumes import resumes_bp
    from backend.routes.candidates import candidates_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(resumes_bp)
    app.register_blueprint(candidates_bp)

    # Serve Frontend UI Pages
    @app.route("/")
    def index_page():
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/login")
    def login_page():
        return send_from_directory(frontend_dir, "login.html")

    @app.route("/dashboard")
    def dashboard_page():
        return send_from_directory(frontend_dir, "dashboard.html")

    @app.route("/job")
    def job_page():
        return send_from_directory(frontend_dir, "job.html")

    @app.route("/candidates")
    def candidates_page():
        return send_from_directory(frontend_dir, "candidates.html")

    @app.route("/candidate-details")
    def candidate_details_page():
        return send_from_directory(frontend_dir, "candidate-details.html")

    @app.route("/live-match")
    def live_match_page():
        return send_from_directory(frontend_dir, "live-match.html")

    # Error Handlers returning structured JSON
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": "Bad request. Please check input parameters."
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "error": "Unauthorized access. Authentication token is required."
        }), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": "Resource not found."
        }), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "success": False,
            "error": "File size exceeds the 10 MB limit."
        }), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": "An internal server error occurred."
        }), 500

    # Auto create database schema
    with app.app_context():
        import backend.models  # Ensure models are discovered
        db.create_all()

    return app
