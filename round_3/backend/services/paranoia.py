# PURPOSE: Paranoia state management for PARANOID
# 3 levels (CHILL, ANXIOUS, MELTDOWN), simple triggers, session-based

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import random
import uuid

# Paranoia levels
CHILL = 0
ANXIOUS = 1
MELTDOWN = 2

LEVEL_NAMES = {
    CHILL: "CHILL",
    ANXIOUS: "ANXIOUS",
    MELTDOWN: "MELTDOWN"
}

# Dangerous strings that trigger paranoia
DANGEROUS_STRINGS = ["eval", "exec", "__import__", "subprocess", "os.system", "shell"]


@dataclass
class Session:
    session_id: str
    level: int = CHILL
    triggers: list[str] = field(default_factory=list)
    request_count: int = 0
    last_request: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)


# In-memory session store (simple dict with TTL cleanup)
_sessions: dict[str, Session] = {}
SESSION_TTL_MINUTES = 30


def _cleanup_old_sessions():
    """Remove sessions older than TTL."""
    cutoff = datetime.now() - timedelta(minutes=SESSION_TTL_MINUTES)
    expired = [sid for sid, s in _sessions.items() if s.last_request < cutoff]
    for sid in expired:
        del _sessions[sid]


def get_or_create_session(session_id: Optional[str] = None) -> Session:
    """Get existing session or create new one."""
    _cleanup_old_sessions()

    if session_id and session_id in _sessions:
        return _sessions[session_id]

    # Create new session
    new_id = session_id or str(uuid.uuid4())
    session = Session(session_id=new_id)
    _sessions[new_id] = session
    return session


def apply_triggers(session: Session, dep_count: int, content: str) -> list[str]:
    """Apply triggers based on request, return list of triggered conditions."""
    triggered = []
    now = datetime.now()

    # Trigger: Large dependency file (>100 deps)
    if dep_count > 100:
        triggered.append("large_input")

    # Trigger: Rapid requests (< 5 seconds since last)
    if session.request_count > 0:
        time_since_last = (now - session.last_request).total_seconds()
        if time_since_last < 5:
            triggered.append("rapid_requests")

    # Trigger: Dangerous strings in input
    content_lower = content.lower()
    for dangerous in DANGEROUS_STRINGS:
        if dangerous in content_lower:
            triggered.append(f"dangerous_string:{dangerous}")
            break

    # Trigger: Session time > 5 minutes
    session_duration = (now - session.created_at).total_seconds()
    if session_duration > 300:  # 5 minutes
        triggered.append("long_session")

    # Update session
    session.request_count += 1
    session.last_request = now
    session.triggers.extend(triggered)

    # Escalate level based on triggers
    if triggered:
        session.level = min(session.level + 1, MELTDOWN)

    return triggered


def apply_reducers(session: Session, is_simple_lookup: bool = False) -> bool:
    """Apply reducers that can decrease paranoia. Returns True if reduced."""
    reduced = False
    now = datetime.now()

    # Reducer: Simple single-package lookup
    if is_simple_lookup and session.level > CHILL:
        session.level = max(session.level - 1, CHILL)
        reduced = True

    # Reducer: Waiting 30+ seconds between requests
    if session.request_count > 0:
        time_since_last = (now - session.last_request).total_seconds()
        if time_since_last > 30 and session.level > CHILL:
            session.level = max(session.level - 1, CHILL)
            reduced = True

    return reduced


def get_paranoia_state(session: Session) -> dict:
    """Get current paranoia state as dict for API response."""
    return {
        "level": session.level,
        "level_name": LEVEL_NAMES[session.level],
        "triggers_this_session": list(set(session.triggers)),  # Dedupe
        "request_count": session.request_count
    }


def should_refuse_request(session: Session) -> bool:
    """At MELTDOWN level, 50% chance of refusing request."""
    if session.level == MELTDOWN:
        return random.random() < 0.5
    return False


def reset_session(session_id: str) -> Session:
    """Reset a session to CHILL level."""
    if session_id in _sessions:
        del _sessions[session_id]
    return get_or_create_session(session_id)
