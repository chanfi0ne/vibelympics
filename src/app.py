"""Flask application for Emoji Zork."""

import secrets
import uuid
from typing import Dict

from flask import Flask, jsonify, request, send_from_directory

from game_engine import GameEngine

app = Flask(__name__, static_folder="static", static_url_path="")

# Secure session configuration
app.config.update(
    SECRET_KEY=secrets.token_hex(32),
    MAX_CONTENT_LENGTH=1024,  # 1KB max request
)

# In-memory game sessions
game_sessions: Dict[str, Dict] = {}
game_engine = GameEngine()


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
def new_game():
    """Start a new game session."""
    session_id = str(uuid.uuid4())
    state = game_engine.new_game()
    game_sessions[session_id] = {"state": state}

    return jsonify({
        "session_id": session_id,
        "state": game_engine.get_state_for_client(state),
    })


@app.route("/api/action", methods=["POST"])
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
def get_state():
    """Get current game state."""
    session_id = request.args.get("session_id")

    if not session_id or session_id not in game_sessions:
        return jsonify({"error": "❓"}), 400

    session = game_sessions[session_id]
    state = session["state"]

    return jsonify({
        "state": game_engine.get_state_for_client(state),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
