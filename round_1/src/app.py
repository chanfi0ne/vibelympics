"""Flask application for Emoji Zork."""

import secrets
import time
import uuid
from functools import wraps

from flask import Flask, jsonify, request, send_from_directory

from game_engine import GameEngine

app = Flask(__name__, static_folder="static", static_url_path="")

# Secure session configuration
app.config.update(
    SECRET_KEY=secrets.token_hex(32),
    MAX_CONTENT_LENGTH=1024,  # 1KB max request
)

# Session configuration
SESSION_TTL = 3600  # 1 hour
MAX_SESSIONS = 1000

# Rate limiting configuration
RATE_LIMIT = 60  # requests per minute
rate_limit_store: dict[str, list] = {}

# In-memory game sessions with timestamps
game_sessions: dict[str, dict] = {}
game_engine = GameEngine()


def cleanup_expired_sessions():
    """Remove expired sessions."""
    current_time = time.time()
    expired = [
        sid
        for sid, data in game_sessions.items()
        if current_time - data.get("created_at", 0) > SESSION_TTL
    ]
    for sid in expired:
        del game_sessions[sid]


def check_rate_limit(ip: str) -> bool:
    """Check if IP has exceeded rate limit. Returns True if allowed."""
    current_time = time.time()

    # Clean old entries
    if ip in rate_limit_store:
        rate_limit_store[ip] = [
            t for t in rate_limit_store[ip] if current_time - t < 60
        ]

    # Check limit
    if len(rate_limit_store.get(ip, [])) >= RATE_LIMIT:
        return False

    # Record request
    rate_limit_store.setdefault(ip, []).append(current_time)
    return True


def rate_limited(f):
    """Rate limiting decorator."""

    @wraps(f)
    def decorated(*args, **kwargs):
        client_ip = request.remote_addr or "unknown"
        if not check_rate_limit(client_ip):
            return jsonify({"error": "🚫"}), 429
        return f(*args, **kwargs)

    return decorated


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.route("/")
def index():
    """Serve the game page."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/new-game", methods=["POST"])
@rate_limited
def new_game():
    """Start a new game session."""
    # Cleanup expired sessions periodically
    cleanup_expired_sessions()

    # Limit total sessions to prevent memory exhaustion
    if len(game_sessions) >= MAX_SESSIONS:
        return jsonify({"error": "🚫"}), 503

    session_id = str(uuid.uuid4())
    state = game_engine.new_game()
    game_sessions[session_id] = {
        "state": state,
        "created_at": time.time(),
    }

    return jsonify(
        {
            "session_id": session_id,
            "state": game_engine.get_state_for_client(state),
        }
    )


@app.route("/api/action", methods=["POST"])
@rate_limited
def action():
    """Perform a game action."""
    if not request.is_json:
        return jsonify({"error": "🚫"}), 400

    data = request.get_json()
    session_id = data.get("session_id")
    action_type = data.get("action")

    # Validate session
    if not session_id or session_id not in game_sessions:
        return jsonify({"error": "❓"}), 400

    session = game_sessions[session_id]
    state = session["state"]

    # Build params from request
    params = {}
    if "direction" in data:
        params["direction"] = data["direction"]
    if "item" in data:
        params["item"] = data["item"]

    # Perform action
    result = game_engine.perform_action(state, action_type, params)

    response = {
        "success": result.success,
        "state": game_engine.get_state_for_client(result.state),
    }

    if result.event_type:
        response["event"] = {
            "type": result.event_type,
            "data": result.event_data,
        }

    if result.error_emoji:
        response["error"] = result.error_emoji

    return jsonify(response)


@app.route("/api/state", methods=["GET"])
@rate_limited
def get_state():
    """Get current game state."""
    session_id = request.args.get("session_id")

    if not session_id or session_id not in game_sessions:
        return jsonify({"error": "❓"}), 400

    session = game_sessions[session_id]
    state = session["state"]

    return jsonify(
        {
            "state": game_engine.get_state_for_client(state),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
