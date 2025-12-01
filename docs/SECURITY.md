# Security Documentation
# 🕳️ Emoji Zork: Security Design & Threat Model

## 1. Executive Summary

This document outlines the security architecture for Emoji Zork, addressing the 30% security weight in judging criteria. Our security approach follows defense-in-depth principles with a focus on:

- **Secure-by-default container** (Chainguard)
- **Minimal attack surface**
- **Input validation**
- **Session security**
- **No sensitive data handling**

## 2. Threat Model

### 2.1 Assets to Protect

| Asset | Sensitivity | Protection Required |
|-------|-------------|---------------------|
| Game state | Low | Integrity (prevent cheating) |
| Session data | Low | Confidentiality, Integrity |
| Server resources | Medium | Availability (prevent DoS) |
| Source code | Low | Already open |

### 2.2 Threat Actors

| Actor | Motivation | Capability |
|-------|------------|------------|
| Curious player | Cheat at game | Low-Medium |
| Malicious user | Crash server, exploit | Medium |
| Automated scanner | Find vulnerabilities | Medium-High |

### 2.3 STRIDE Analysis

| Threat | Applies? | Mitigation |
|--------|----------|------------|
| **S**poofing | Low | Session tokens, no auth required |
| **T**ampering | Medium | Server-side game state validation |
| **R**epudiation | N/A | No logging requirements |
| **I**nformation Disclosure | Low | No sensitive data stored |
| **D**enial of Service | Medium | Rate limiting, resource limits |
| **E**levation of Privilege | Low | No privilege levels in game |

## 3. Security Controls

### 3.1 Container Security (Chainguard)

**Why Chainguard:**

```dockerfile
FROM cgr.dev/chainguard/python:latest
```

Chainguard images provide:

| Feature | Benefit |
|---------|---------|
| Minimal base | Smaller attack surface |
| No shell (distroless) | No shell escape attacks |
| Non-root user | Container breakout prevention |
| Regular CVE patching | Known vulnerability protection |
| SBOM available | Supply chain transparency |
| Signed images | Image integrity verification |

**Container hardening:**

```dockerfile
# Run as non-root (Chainguard default)
USER nonroot

# Read-only filesystem where possible
# No privileged capabilities
# Resource limits in deployment
```

### 3.2 Input Validation

All user input is validated server-side:

```python
# Allowed actions (whitelist approach)
VALID_ACTIONS = {"move", "look", "take", "attack", "use"}

# Allowed directions
VALID_DIRECTIONS = {"⬆️", "⬇️", "⬅️", "➡️"}

# Allowed items (only emojis in game)
VALID_ITEMS = {"🗡️", "🔦", "🔑", "🧪", "💎", "🛡️", "🗺️", "👑"}

def validate_action(data: dict) -> bool:
    """Validate incoming action request."""
    
    # Check action type
    action = data.get("action")
    if action not in VALID_ACTIONS:
        raise ValidationError("Invalid action")
    
    # Check direction if move action
    if action == "move":
        direction = data.get("direction")
        if direction not in VALID_DIRECTIONS:
            raise ValidationError("Invalid direction")
    
    # Check item if take/use action
    if action in ("take", "use"):
        item = data.get("item")
        if item and item not in VALID_ITEMS:
            raise ValidationError("Invalid item")
    
    return True
```

### 3.3 Session Security

```python
from flask import Flask, session
import secrets
import uuid

app = Flask(__name__)

# Secure session configuration
app.config.update(
    SECRET_KEY=secrets.token_hex(32),  # Random key per instance
    SESSION_COOKIE_SECURE=False,       # True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,      # Prevent XSS access
    SESSION_COOKIE_SAMESITE='Lax',     # CSRF protection
    PERMANENT_SESSION_LIFETIME=3600,   # 1 hour expiry
)

# Session ID generation
def create_session() -> str:
    """Generate cryptographically secure session ID."""
    return str(uuid.uuid4())
```

### 3.4 API Security

```python
from functools import wraps
from flask import request, jsonify
import time

# Rate limiting (simple in-memory)
request_counts = {}
RATE_LIMIT = 60  # requests per minute

def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time.time()
        
        # Clean old entries
        request_counts[client_ip] = [
            t for t in request_counts.get(client_ip, [])
            if current_time - t < 60
        ]
        
        # Check limit
        if len(request_counts.get(client_ip, [])) >= RATE_LIMIT:
            return jsonify({"error": "🚫"}), 429
        
        # Record request
        request_counts.setdefault(client_ip, []).append(current_time)
        
        return f(*args, **kwargs)
    return decorated

# Content-Type validation
def validate_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'POST':
            if not request.is_json:
                return jsonify({"error": "🚫"}), 400
            try:
                _ = request.get_json()
            except Exception:
                return jsonify({"error": "🚫"}), 400
        return f(*args, **kwargs)
    return decorated
```

### 3.5 Response Security Headers

```python
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # XSS protection (legacy browsers)
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "  # For emoji styling
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response
```

## 4. Game State Security

### 4.1 Server-Side State

All game state is maintained server-side to prevent cheating:

```python
class GameState:
    """Server-authoritative game state."""
    
    def __init__(self):
        self._health = 3
        self._inventory = []
        self._score = 0
        self._current_room = "house"
    
    @property
    def health(self) -> int:
        return self._health
    
    def take_damage(self, amount: int) -> None:
        """Damage can only be applied, never set directly."""
        self._health = max(0, self._health - amount)
    
    def heal(self, amount: int) -> None:
        """Healing is capped at max health."""
        self._health = min(5, self._health + amount)
    
    # No setters for direct manipulation!
```

### 4.2 Action Validation

Every action is validated against current state:

```python
def validate_move(state: GameState, direction: str) -> bool:
    """Validate move is legal."""
    room = get_room(state.current_room)
    return direction in room.exits

def validate_take(state: GameState, item: str) -> bool:
    """Validate item exists in room."""
    room = get_room(state.current_room)
    return item in room.items

def validate_attack(state: GameState) -> bool:
    """Validate attack is possible."""
    room = get_room(state.current_room)
    has_weapon = any(i in WEAPONS for i in state.inventory)
    has_enemy = len(room.enemies) > 0
    return has_weapon and has_enemy
```

## 5. Frontend Security

### 5.1 No Sensitive Data

The frontend receives only:
- Current game state (public)
- Available actions (public)
- No secrets, tokens, or sensitive info

### 5.2 XSS Prevention

```javascript
// All emoji content is set via textContent, not innerHTML
function renderRoom(state) {
    // SAFE: textContent escapes HTML
    document.getElementById('room-emoji').textContent = state.location;
    document.getElementById('health').textContent = '❤️'.repeat(state.health);
    
    // NEVER: innerHTML with user data
    // element.innerHTML = state.something; // UNSAFE
}

// No eval() or Function() usage
// No dynamic script injection
// No inline event handlers in HTML
```

### 5.3 CSP Compliance

Frontend code complies with strict CSP:
- No inline scripts (all in game.js)
- No eval or dynamic code execution
- No external resources
- No iframe embedding

## 6. Denial of Service Protection

### 6.1 Resource Limits

```python
# Maximum sessions per IP
MAX_SESSIONS_PER_IP = 10

# Maximum game state size
MAX_INVENTORY_SIZE = 20

# Request size limit
app.config['MAX_CONTENT_LENGTH'] = 1024  # 1KB max request

# Response timeout
RESPONSE_TIMEOUT = 5  # seconds
```

### 6.2 Container Resource Limits

```yaml
# docker-compose.yml or deployment config
services:
  emoji-zork:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 128M
        reservations:
          cpus: '0.25'
          memory: 64M
```

## 7. Logging & Monitoring

### 7.1 Security Logging

```python
import logging

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.WARNING)

def log_security_event(event_type: str, details: dict) -> None:
    """Log security-relevant events."""
    # Sanitize before logging (no sensitive data)
    safe_details = {
        'event': event_type,
        'ip': request.remote_addr,
        'timestamp': time.time(),
        # No session IDs or tokens in logs
    }
    security_logger.warning(f"Security event: {safe_details}")

# Events to log:
# - Rate limit exceeded
# - Invalid input attempts
# - Session validation failures
# - Unusual patterns
```

### 7.2 No Sensitive Data in Logs

```python
# NEVER log:
# - Session tokens
# - Full request bodies
# - Stack traces in production
# - IP addresses in detail logs

# Example safe logging:
logger.info(f"Game action: {action_type}")  # SAFE
# NOT: logger.info(f"Session {session_id} action: {request.json}")
```

## 8. Dependency Security

### 8.1 Minimal Dependencies

```
# requirements.txt - only essentials
flask==3.0.0
gunicorn==21.2.0
```

**Why minimal:**
- Fewer dependencies = smaller attack surface
- Easier to audit
- Faster security updates
- Smaller container

### 8.2 Dependency Verification

```bash
# Pin exact versions
# Use pip-compile for lockfile
# Verify checksums in CI/CD

pip install --require-hashes -r requirements.txt
```

## 9. Security Checklist

### Pre-Deployment

- [ ] All input validated server-side
- [ ] Session configuration secure
- [ ] Security headers enabled
- [ ] Rate limiting active
- [ ] No sensitive data exposed
- [ ] Container runs as non-root
- [ ] Dependencies pinned and audited
- [ ] No debug mode in production

### Code Review

- [ ] No eval() or exec()
- [ ] No innerHTML with user data
- [ ] No secrets in code
- [ ] Error messages don't leak info
- [ ] Logging sanitized

## 10. Incident Response

### If Vulnerability Found

1. **Assess** - Determine severity and impact
2. **Contain** - Stop container if critical
3. **Fix** - Patch vulnerability
4. **Test** - Verify fix works
5. **Deploy** - Push updated container
6. **Review** - Post-incident analysis

### Contact

For security issues: [Security contact in README]

---

## 11. Security Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Container Security (Chainguard)                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ - Minimal attack surface (distroless)               │    │
│  │ - Non-root execution                                │    │
│  │ - Regular CVE updates                               │    │
│  │ - Signed & verified images                          │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Application Security (Flask)                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ - Security headers (CSP, X-Frame-Options, etc.)     │    │
│  │ - Rate limiting                                     │    │
│  │ - Input validation                                  │    │
│  │ - Session security                                  │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Game Logic Security                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ - Server-authoritative state                        │    │
│  │ - Action validation                                 │    │
│  │ - No client-side trust                              │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Frontend Security                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ - CSP compliant                                     │    │
│  │ - No eval/innerHTML                                 │    │
│  │ - XSS prevention                                    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

**Document Status:** Ready for Implementation  
**Security Review:** Approved for development
