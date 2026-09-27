import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production-resume-ai-2026")
    JWT_SECRET = os.environ.get("JWT_SECRET", "jwt-super-secret-key-ai-screening")
    JWT_EXPIRATION_HOURS = 24
    
    # SQLite Database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Configurations
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB maximum upload size
    
    # NLP Matching Weights (Configurable)
    # Final Score = w_tfidf * TF-IDF + w_semantic * Semantic + w_skill * Skill
    WEIGHT_TFIDF = float(os.environ.get("WEIGHT_TFIDF", "0.30"))
    WEIGHT_SEMANTIC = float(os.environ.get("WEIGHT_SEMANTIC", "0.40"))
    WEIGHT_SKILL = float(os.environ.get("WEIGHT_SKILL", "0.30"))
    
    # Fast embedding mode (enables instant sub-15ms inference without blocking on external HuggingFace downloads)
    USE_FAST_EMBEDDINGS = os.environ.get("USE_FAST_EMBEDDINGS", "1").lower() in ("1", "true")

class TestConfig(Config):
    """Testing configuration with in-memory SQLite and isolated directories."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "tests", "test_uploads")
