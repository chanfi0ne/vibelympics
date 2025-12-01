# Implementation Guide for Code Droid
# 🕳️ Emoji Zork: Build Instructions

## Quick Reference

This guide summarizes all documentation for efficient implementation.

## Documentation Index

| Document | Purpose | Key Sections |
|----------|---------|--------------|
| [PRD.md](./PRD.md) | What to build | Requirements, User Stories, UI Spec |
| [TECHNICAL_SPEC.md](./TECHNICAL_SPEC.md) | How to build | Architecture, API, Data Structures |
| [SECURITY.md](./SECURITY.md) | Security requirements | Threat Model, Controls, Headers |
| [GAME_DESIGN.md](./GAME_DESIGN.md) | Game content | Rooms, Items, Enemies, Puzzles |
| [CODING_STANDARDS.md](./CODING_STANDARDS.md) | Code quality | Style, Testing, Documentation |

---

## Implementation Checklist

### Phase 1: Project Setup
- [ ] Create project structure
- [ ] Set up requirements.txt (flask, gunicorn)
- [ ] Create Dockerfile with Chainguard base
- [ ] Verify container builds and runs

### Phase 2: Backend Core
- [ ] `models.py` - Data classes (Room, Enemy, GameState)
- [ ] `world.py` - Define all 7 rooms, items, enemies
- [ ] `game_engine.py` - Core game logic
- [ ] `validators.py` - Input validation
- [ ] `app.py` - Flask routes with security headers

### Phase 3: API Implementation
- [ ] POST `/api/new-game` - Start game, return state
- [ ] POST `/api/action` - Handle all game actions
- [ ] GET `/api/state` - Get current state

### Phase 4: Frontend
- [ ] `index.html` - Game layout (emoji-only UI)
- [ ] `styles.css` - Styling, animations
- [ ] `game.js` - Game controller, API client

### Phase 5: Game Features
- [ ] Room navigation (⬆️⬇️⬅️➡️)
- [ ] Item pickup (🖐️)
- [ ] Combat system (⚔️)
- [ ] Potion use (🧪)
- [ ] Key/door puzzle (🔑)
- [ ] Grue/darkness mechanic (🌑🐺)
- [ ] Win condition (👑)
- [ ] Death/retry (💀🔄)

### Phase 6: Polish
- [ ] Animations (item pickup, damage, death)
- [ ] Visual feedback (invalid actions)
- [ ] Score tracking
- [ ] Victory celebration

### Phase 7: Testing & Security
- [ ] Unit tests for game engine
- [ ] API tests
- [ ] Security headers verified
- [ ] Input validation tested
- [ ] Container runs successfully

---

## Quick Reference: Game World

```
🏠 House ──➡️── 🌲 Forest ──➡️── 💧 River
                    │
                    ⬆️
                    │
                   ⛪ Temple
                    │
                    ⬇️
                    │
               🕳️ Cave (DARK!)
                    │
                    ⬇️
                    │
               🏰 Dungeon
                    │
                   🔒 (needs 🔑)
                    │
               👑 Throne Room
```

## Quick Reference: Items

| Emoji | Name | Found In | Effect |
|-------|------|----------|--------|
| 🗡️ | Sword | 🏠 | Enables attack |
| 🔦 | Flashlight | 🌲 | Prevents grue |
| 💎 | Diamond | 💧 | +50 points |
| 🧪 | Potion | ⛪ | Heal +2❤️ |
| 🔑 | Key | ⛪ | Opens throne room |
| 🛡️ | Shield | 🕳️ | Reduces damage |
| 🗺️ | Map | 🏰 | Shows connections |
| 👑 | Crown | 👑 | WIN! |

## Quick Reference: Enemies

| Emoji | Name | Location | HP | DMG |
|-------|------|----------|-----|-----|
| 🦇 | Bat | 🌲 | 1 | 0.5 |
| 👹 | Troll | ⛪, 🏰 | 3 | 1 |
| 🐉 | Dragon | 👑 | 5 | 2 |
| 🐺 | Grue | 🕳️ (dark) | ∞ | 💀 |

## Quick Reference: API

```javascript
// Start new game
POST /api/new-game
→ { session_id, state }

// Perform action
POST /api/action
{ session_id, action, ...params }
→ { success, state, event }

// Actions:
{ action: "move", direction: "⬆️" }
{ action: "look" }
{ action: "take", item: "🗡️" }
{ action: "attack" }
{ action: "use", item: "🧪" }
```

## Quick Reference: Dockerfile

```dockerfile
FROM cgr.dev/chainguard/python:latest-dev AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target=/app/deps

FROM cgr.dev/chainguard/python:latest
WORKDIR /app
COPY --from=builder /app/deps /app/deps
COPY src/ /app/
ENV PYTHONPATH=/app/deps
EXPOSE 8080
ENTRYPOINT ["python", "app.py"]
```

## Judging Criteria Reminders

| Criteria | Weight | Key Focus |
|----------|--------|-----------|
| **Security** | 30% | Chainguard, validation, headers, no vulns |
| **Functionality** | 30% | Complete game, reliable, all features |
| **Code Quality** | 30% | Clean, typed, tested, documented |
| **Vibes** | 10% | Creative, fun, polished |

---

## Ready to Build! 🎮

Start with:
```bash
mkdir -p src/static tests
touch src/app.py src/models.py src/world.py src/game_engine.py src/validators.py
touch src/static/index.html src/static/styles.css src/static/game.js
touch requirements.txt Dockerfile
```

Good luck, Code Droid! 🤖
