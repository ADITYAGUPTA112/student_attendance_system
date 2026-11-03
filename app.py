"""CloudAttend - Intelligent Student Attendance & Analytics Platform
ENSP401 - Cloud Computing Capstone Project
"""

import os
from flask import Flask, jsonify
import db

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "instance", "cloudattend.db")


def create_app(test_config=None):
    """Application factory for CloudAttend."""
    app = Flask(__name__, instance_relative_config=True)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-cloudattend-2026"),
        DATABASE=os.environ.get("DATABASE_PATH", DEFAULT_DB_PATH),
    )

    if test_config:
        app.config.update(test_config)

    # Register database handlers and CLI commands
    db.init_app(app)

    # Liveness & Health check route
    @app.route("/health", methods=["GET"])
    def health():
        """Basic liveness response for orchestration and monitoring."""
        return jsonify({
            "status": "healthy",
            "service": "CloudAttend",
            "version": "1.0.0"
        }), 200

    return app


app = create_app()

if __name__ == "__main__":
    # Ensure database is initialized on local start if not exists
    with app.app_context():
        if not os.path.exists(app.config["DATABASE"]):
            db.init_db()
            db.seed_db()
            print("Database initialized and seeded.")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
