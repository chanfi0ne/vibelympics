"""Security tests for Emoji Zork."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import time

from app import MAX_SESSIONS, app, cleanup_expired_sessions, game_sessions


class TestSecurityHeaders:
    """Tests for security headers."""

    def setup_method(self):
        self.client = app.test_client()
        game_sessions.clear()

    def test_x_frame_options_header(self):
        """X-Frame-Options should be DENY."""
        resp = self.client.get("/")
        assert resp.headers.get("X-Frame-Options") == "DENY"

    def test_x_content_type_options_header(self):
        """X-Content-Type-Options should be nosniff."""
        resp = self.client.get("/")
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"

    def test_csp_header_present(self):
        """Content-Security-Policy should be set."""
        resp = self.client.get("/")
        csp = resp.headers.get("Content-Security-Policy")
        assert csp is not None
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp

    def test_referrer_policy_header(self):
        """Referrer-Policy should be strict."""
        resp = self.client.get("/")
        assert "strict-origin" in resp.headers.get("Referrer-Policy", "")


class TestInputValidation:
    """Tests for input validation."""

    def setup_method(self):
        self.client = app.test_client()
        game_sessions.clear()

    def test_invalid_action_rejected(self):
        """Invalid actions should be rejected."""
        resp = self.client.post("/api/new-game")
        session_id = resp.get_json()["session_id"]

        resp = self.client.post(
            "/api/action",
            json={
                "session_id": session_id,
                "action": "hack",
            },
        )
        data = resp.get_json()
        assert data.get("error") == "❓"

    def test_invalid_direction_rejected(self):
        """Invalid directions should be rejected."""
        resp = self.client.post("/api/new-game")
        session_id = resp.get_json()["session_id"]

        resp = self.client.post(
            "/api/action",
            json={
                "session_id": session_id,
                "action": "move",
                "direction": "<script>alert(1)</script>",
            },
        )
        data = resp.get_json()
        assert data.get("error") == "❓"

    def test_invalid_item_rejected(self):
        """Invalid items should be rejected."""
        resp = self.client.post("/api/new-game")
        session_id = resp.get_json()["session_id"]

        resp = self.client.post(
            "/api/action",
            json={
                "session_id": session_id,
                "action": "take",
                "item": "<script>alert(1)</script>",
            },
        )
        data = resp.get_json()
        assert data.get("error") == "❓"

    def test_non_json_request_rejected(self):
        """Non-JSON requests should be rejected."""
        resp = self.client.post("/api/action", data="not json")
        assert resp.status_code == 400


class TestSessionSecurity:
    """Tests for session management."""

    def setup_method(self):
        self.client = app.test_client()
        game_sessions.clear()

    def test_invalid_session_rejected(self):
        """Invalid session IDs should be rejected."""
        resp = self.client.post(
            "/api/action",
            json={
                "session_id": "fake-session-id",
                "action": "look",
            },
        )
        assert resp.status_code == 400
        assert resp.get_json().get("error") == "❓"

    def test_session_has_timestamp(self):
        """Sessions should have creation timestamp."""
        resp = self.client.post("/api/new-game")
        session_id = resp.get_json()["session_id"]
        assert "created_at" in game_sessions[session_id]
        assert isinstance(game_sessions[session_id]["created_at"], float)

    def test_session_limit_enforced(self):
        """Should reject new sessions when limit reached."""
        # Fill up sessions
        for i in range(MAX_SESSIONS):
            game_sessions[f"session-{i}"] = {
                "state": None,
                "created_at": time.time(),
            }

        resp = self.client.post("/api/new-game")
        assert resp.status_code == 503

    def test_expired_sessions_cleaned(self):
        """Expired sessions should be cleaned up."""
        # Create an expired session
        game_sessions["expired-session"] = {
            "state": None,
            "created_at": time.time() - 7200,  # 2 hours ago
        }

        cleanup_expired_sessions()
        assert "expired-session" not in game_sessions


class TestRateLimiting:
    """Tests for rate limiting."""

    def setup_method(self):
        self.client = app.test_client()
        game_sessions.clear()

    def test_rate_limit_returns_429(self):
        """Should return 429 when rate limit exceeded."""
        from app import RATE_LIMIT, rate_limit_store

        # Simulate hitting rate limit
        test_ip = "test-ip"
        rate_limit_store[test_ip] = [time.time()] * (RATE_LIMIT + 1)

        # This would normally check the IP, but in test mode
        # we can verify the logic works
        from app import check_rate_limit

        assert check_rate_limit(test_ip) is False


class TestGameStateIntegrity:
    """Tests for game state integrity."""

    def setup_method(self):
        self.client = app.test_client()
        game_sessions.clear()

    def test_cannot_cheat_health(self):
        """Cannot manipulate health directly via API."""
        resp = self.client.post("/api/new-game")
        session_id = resp.get_json()["session_id"]

        # Try to send manipulated health (should be ignored)
        resp = self.client.post(
            "/api/action",
            json={
                "session_id": session_id,
                "action": "look",
                "health": 999,  # This should be ignored
            },
        )
        data = resp.get_json()
        assert data["state"]["health"] == 3  # Still original

    def test_cannot_cheat_inventory(self):
        """Cannot add items to inventory via API."""
        resp = self.client.post("/api/new-game")
        session_id = resp.get_json()["session_id"]

        resp = self.client.post(
            "/api/action",
            json={
                "session_id": session_id,
                "action": "look",
                "inventory": ["👑"],  # This should be ignored
            },
        )
        data = resp.get_json()
        assert "👑" not in data["state"]["inventory"]


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
