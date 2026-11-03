"""CloudAttend - Intelligent Student Attendance & Analytics Platform
ENSP401 - Cloud Computing Capstone Project
"""

import os
import sqlite3
from flask import Flask, jsonify, g

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "instance", "cloudattend.db")


def create_app(test_config=None):
    """Application factory for CloudAttend."""
    app = Flask(__name__, instance_relative_config=True)

    # Ensure the instance directory exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-cloudattend-2026"),
        DATABASE=os.environ.get("DATABASE_PATH", DEFAULT_DB_PATH),
    )

    if test_config:
        app.config.update(test_config)

    # Register teardown function to close DB connections
    app.teardown_appcontext(close_db)

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


def get_db(app_instance=None):
    """Retrieve or open a SQLite connection with foreign key enforcement."""
    if "db" not in g:
        from flask import current_app
        db_path = current_app.config["DATABASE"] if not app_instance else app_instance.config["DATABASE"]
        
        # Ensure parent directory of the DB exists
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        # CRITICAL: Enforce foreign keys on every connection
        conn.execute("PRAGMA foreign_keys = ON;")
        g.db = conn
    return g.db


def close_db(e=None):
    """Close the active database connection if open."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

