"""Tests for the Flask API endpoints."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from app import app, game_sessions


@pytest.fixture
def client():
    """Create a test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
    game_sessions.clear()


@pytest.fixture
def game_session(client):
    """Create a new game session and return session_id."""
    response = client.post("/api/new-game")
    return response.get_json()["session_id"]


class TestSecurityHeaders:
    """Tests for security headers."""

    def test_security_headers_present(self, client):
        """All security headers should be present."""
        response = client.get("/")
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Content-Security-Policy" in response.headers


class TestIndexRoute:
    """Tests for the index route."""

    def test_index_returns_html(self, client):
        """Index should return the game page."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data


class TestNewGameRoute:
    """Tests for new game creation."""

    def test_new_game_returns_session_id(self, client):
        """New game should return a session ID."""
        response = client.post("/api/new-game")
        assert response.status_code == 200
        data = response.get_json()
        assert "session_id" in data
        assert "state" in data

    def test_new_game_state_has_expected_fields(self, client):
        """New game state should have all expected fields."""
        response = client.post("/api/new-game")
        state = response.get_json()["state"]
        assert "location" in state
        assert "health" in state
        assert "inventory" in state
        assert "score" in state


class TestActionRoute:
    """Tests for the action route."""

    def test_action_requires_json(self, client, game_session):
        """Action should require JSON content type."""
        response = client.post("/api/action", data="not json")
        assert response.status_code == 400
        assert response.get_json()["error"] == "🚫"

    def test_action_requires_valid_session(self, client):
        """Action should require valid session ID."""
        response = client.post(
            "/api/action",
            json={"session_id": "invalid", "action": "look"},
        )
        assert response.status_code == 400
        assert response.get_json()["error"] == "❓"

    def test_action_move_works(self, client, game_session):
        """Move action should work."""
        response = client.post(
            "/api/action",
            json={"session_id": game_session, "action": "move", "direction": "➡️"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert data["state"]["location_id"] == "forest"

    def test_action_look_works(self, client, game_session):
        """Look action should work."""
        response = client.post(
            "/api/action",
            json={"session_id": game_session, "action": "look"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert data["event"]["type"] == "looked"

    def test_action_take_works(self, client, game_session):
        """Take action should work."""
        response = client.post(
            "/api/action",
            json={"session_id": game_session, "action": "take", "item": "🗡️"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"]
        assert "🗡️" in data["state"]["inventory"]

    def test_action_returns_error_emoji(self, client, game_session):
        """Failed action should return error emoji."""
        response = client.post(
            "/api/action",
            json={"session_id": game_session, "action": "take", "item": "🔦"},
        )
        data = response.get_json()
        assert not data["success"]
        assert "error" in data


class TestStateRoute:
    """Tests for the state route."""

    def test_get_state_works(self, client, game_session):
        """Get state should return current state."""
        response = client.get(f"/api/state?session_id={game_session}")
        assert response.status_code == 200
        data = response.get_json()
        assert "state" in data

    def test_get_state_requires_valid_session(self, client):
        """Get state should require valid session."""
        response = client.get("/api/state?session_id=invalid")
        assert response.status_code == 400

    def test_get_state_requires_session_id(self, client):
        """Get state should require session ID parameter."""
        response = client.get("/api/state")
        assert response.status_code == 400
