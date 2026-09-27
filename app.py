import os
from backend import create_app
from config import Config

app = create_app(Config)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    print(f"\n=======================================================")
    print(f" AI-Powered Resume Screening & Job Matching Platform")
    print(f" Server running at: http://127.0.0.1:{port}")
    print(f" Recruiter Portal:  http://127.0.0.1:{port}/login")
    print(f" Dashboard:         http://127.0.0.1:{port}/dashboard")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
