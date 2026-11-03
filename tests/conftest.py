"""Pytest test configuration and fixtures for CloudAttend."""

import os
import tempfile
import pytest
from app import create_app
import db


@pytest.fixture
def app():
    """Create and configure a clean Flask application instance with initialized test database."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    app_instance = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "DATABASE": db_path,
    })

    with app_instance.app_context():
        db.init_db()
        db.seed_db()

    yield app_instance

    # Teardown: close and remove temporary test database
    try:
        os.close(db_fd)
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def client(app):
    """Test client for issuing requests to the application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner for testing Flask CLI commands."""
    return app.test_cli_runner()
