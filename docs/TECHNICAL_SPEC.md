# Technical Specification
# 🕳️ Emoji Zork: Architecture & Implementation

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser Client                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Vanilla JavaScript                  │    │
│  │  - Game renderer (emoji display)                 │    │
│  │  - Input handler (click events)                  │    │
│  │  - State manager (current view)                  │    │
│  │  - Animation controller                          │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│                    HTTP/JSON API                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Chainguard Python Container                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │                 Flask Server                     │    │
│  │  - REST API endpoints                            │    │
│  │  - Session management                            │    │
│  │  - Game logic engine                             │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │                Game Engine                       │    │
│  │  - World/room graph                              │    │
│  │  - Player state                                  │    │
│  │  - Combat system                                 │    │
│  │  - Puzzle logic                                  │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         FRONTEND                              │
├──────────────────────────────────────────────────────────────┤
│  index.html          │  styles.css         │  game.js        │
│  - Game container    │  - Emoji sizing     │  - API client   │
│  - Button layout     │  - Animations       │  - Event loop   │
│  - Status displays   │  - Responsive grid  │  - Renderer     │
└──────────────────────────────────────────────────────────────┘
                              │
                         HTTP/JSON
                              │
┌──────────────────────────────────────────────────────────────┐
│                         BACKEND                               │
├──────────────────────────────────────────────────────────────┤
│  app.py              │  game_engine.py     │  world.py       │
│  - Flask routes      │  - Game state       │  - Room defs    │
│  - Session mgmt      │  - Combat logic     │  - Item defs    │
│  - CORS handling     │  - Puzzle logic     │  - Enemy defs   │
│  - Input validation  │  - Win/lose check   │  - Connections  │
└──────────────────────────────────────────────────────────────┘
```

## 2. API Specification

### 2.1 Endpoints

All responses return JSON with emoji-only content for display.

#### `POST /api/new-game`
Start a new game session.

**Request:** None  
**Response:**
```json
{
  "session_id": "uuid",
  "state": {
    "location": "🏠",
    "location_name": "house",
    "health": 3,
    "max_health": 3,
    "score": 0,
    "inventory": [],
    "room_items": ["🗡️"],
    "room_enemies": [],
    "exits": {"➡️": "🌲"},
    "is_dark": false,
    "message": null,
    "game_over": false,
    "victory": false
  }
}
```

#### `POST /api/action`
Perform a game action.

**Request:**
```json
{
  "session_id": "uuid",
  "action": "move",
  "direction": "➡️"
}
```

**Action Types:**
| action | parameters | description |
|--------|------------|-------------|
| `move` | `direction`: ⬆️⬇️⬅️➡️ | Move to adjacent room |
| `look` | none | Refresh room view |
| `take` | `item`: emoji | Pick up item |
| `attack` | none | Attack enemy in room |
| `use` | `item`: emoji | Use item (potion, key) |

**Response:**
```json
{
  "success": true,
  "state": { /* updated game state */ },
  "event": {
    "type": "item_taken",
    "emoji": "🗡️"
  }
}
```

#### `GET /api/state`
Get current game state.

**Request:** Query param `session_id`  
**Response:** Same state object as above

### 2.2 Event Types

Events trigger frontend animations:

| Event Type | Data | Frontend Animation |
|------------|------|-------------------|
| `item_taken` | `emoji` | Item flies to inventory |
| `damage_taken` | `amount` | Hearts flash, screen shake |
| `damage_dealt` | `amount` | Enemy health decreases |
| `enemy_defeated` | `enemy` | Enemy explodes (💥) |
| `door_locked` | none | Door shakes with ❌ |
| `door_unlocked` | none | Door sparkles ✨ |
| `grue_attack` | none | Darkness → eyes → death |
| `player_died` | none | 💀 overlay |
| `victory` | none | 🏆🎉 celebration |

## 3. Data Structures

### 3.1 Room Definition

```python
@dataclass
class Room:
    id: str                          # Internal identifier
    emoji: str                       # Display emoji (🏠, 🌲, etc.)
    items: List[str]                 # Items in room (emoji list)
    enemies: List[Enemy]             # Enemies present
    exits: Dict[str, str]            # {direction_emoji: room_id}
    is_dark: bool                    # Requires light source
    locked_exits: Dict[str, str]     # {direction: required_item}
```

### 3.2 Player State

```python
@dataclass
class PlayerState:
    current_room: str                # Room ID
    health: int                      # Current health (max 5)
    max_health: int                  # Maximum health
    inventory: List[str]             # Item emojis
    score: int                       # Current score
    has_light: bool                  # Computed from inventory
    equipped_weapon: Optional[str]   # Current weapon
```

### 3.3 Enemy Definition

```python
@dataclass
class Enemy:
    emoji: str                       # 👹, 🦇, 🐉, etc.
    health: int                      # Current health
    max_health: int                  # Starting health
    damage: int                      # Damage per attack
    is_grue: bool                    # Special grue behavior
```

### 3.4 Game World Graph

```python
WORLD = {
    "house": Room(
        id="house",
        emoji="🏠",
        items=["🗡️"],
        enemies=[],
        exits={"➡️": "forest"},
        is_dark=False,
        locked_exits={}
    ),
    "forest": Room(
        id="forest",
        emoji="🌲",
        items=["🔦"],
        enemies=[Enemy("🦇", 1, 1, 1, False)],
        exits={
            "⬅️": "house",
            "➡️": "river",
            "⬇️": "cave"
        },
        is_dark=False,
        locked_exits={}
    ),
    # ... etc
}
```

## 4. Game Logic

### 4.1 Combat Flow

```
Player clicks ⚔️
    │
    ▼
Has weapon in inventory?
    │
    ├── No  → Return error event (❌ flash)
    │
    ├── Yes → Calculate player damage
    │           │
    │           ▼
    │         Apply damage to enemy
    │           │
    │           ▼
    │         Enemy health > 0?
    │           │
    │           ├── Yes → Enemy attacks back
    │           │           │
    │           │           ▼
    │           │         Apply damage to player
    │           │           │
    │           │           ▼
    │           │         Player health > 0?
    │           │           │
    │           │           ├── Yes → Continue
    │           │           └── No  → Game Over 💀
    │           │
    │           └── No  → Enemy defeated 💥
    │                       │
    │                       ▼
    │                     Drop loot, add score
```

### 4.2 Grue Logic

```
Player enters dark room
    │
    ▼
has_light_source?
    │
    ├── Yes → Normal room, grue dormant
    │
    └── No  → GRUE ATTACK
                │
                ▼
              Instant death (💀)
              Special animation: 🌑 → 👀 → 😱 → 💀
```

### 4.3 Puzzle Logic (Key + Door)

```
Player clicks 🔑 action
    │
    ▼
Has 🔑 in inventory?
    │
    ├── No  → Error flash
    │
    └── Yes → Is there a locked exit?
                │
                ├── No  → Error flash
                │
                └── Yes → Unlock exit
                            │
                            ▼
                          Remove 🔑 from inventory
                          Add exit to available exits
                          Door unlock animation ✨
```

## 5. Frontend Architecture

### 5.1 HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="game-container">
        <!-- Top status bar -->
        <div id="status-bar">
            <span id="location">📍🏠</span>
            <span id="health">❤️❤️❤️</span>
            <span id="score">💰0</span>
        </div>
        
        <!-- Main room view -->
        <div id="room-view">
            <div id="room-emoji">🏠</div>
            <div id="room-contents">
                <span id="visible-items">👁️: 🗡️</span>
            </div>
            <div id="enemy-display"></div>
        </div>
        
        <!-- Inventory -->
        <div id="inventory">
            <span>🎒:</span>
            <div id="inventory-slots"></div>
        </div>
        
        <!-- Navigation -->
        <div id="navigation">
            <button class="nav-btn" data-dir="⬆️">⬆️</button>
            <div class="nav-row">
                <button class="nav-btn" data-dir="⬅️">⬅️</button>
                <button class="action-btn" data-action="look">👁️</button>
                <button class="nav-btn" data-dir="➡️">➡️</button>
            </div>
            <button class="nav-btn" data-dir="⬇️">⬇️</button>
        </div>
        
        <!-- Actions -->
        <div id="actions">
            <button class="action-btn" data-action="take">🖐️</button>
            <button class="action-btn" data-action="attack">⚔️</button>
            <button class="action-btn" data-action="use-potion">🧪</button>
            <button class="action-btn" data-action="use-key">🔑</button>
        </div>
    </div>
    
    <!-- Overlays -->
    <div id="death-overlay" class="hidden">💀<button id="retry">🔄</button></div>
    <div id="victory-overlay" class="hidden">🏆👑🎉</div>
    
    <script src="game.js"></script>
</body>
</html>
```

### 5.2 CSS Animation Classes

```css
/* Item pickup animation */
.item-fly-to-inventory {
    animation: flyToInventory 0.5s ease-in-out;
}

/* Damage flash */
.damage-flash {
    animation: damageFlash 0.3s ease-in-out;
}

/* Enemy death */
.enemy-explode {
    animation: explode 0.5s ease-out forwards;
}

/* Grue sequence */
.grue-darkness { background: black; }
.grue-eyes { content: "👀"; }
.grue-death { content: "💀"; }
```

### 5.3 JavaScript Game Loop

```javascript
class EmojiZork {
    constructor() {
        this.sessionId = null;
        this.state = null;
        this.init();
    }
    
    async init() {
        await this.newGame();
        this.bindEvents();
        this.render();
    }
    
    async newGame() {
        const response = await fetch('/api/new-game', { method: 'POST' });
        const data = await response.json();
        this.sessionId = data.session_id;
        this.state = data.state;
    }
    
    async performAction(action, params = {}) {
        const response = await fetch('/api/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: this.sessionId,
                action,
                ...params
            })
        });
        const data = await response.json();
        if (data.event) {
            await this.animateEvent(data.event);
        }
        this.state = data.state;
        this.render();
    }
    
    render() {
        // Update all UI elements with current state
    }
    
    async animateEvent(event) {
        // Trigger CSS animations based on event type
    }
}
```

## 6. File Structure

```
emoji-zork/
├── Dockerfile
├── requirements.txt
├── README.md
├── docs/
│   ├── PRD.md
│   ├── TECHNICAL_SPEC.md
│   ├── SECURITY.md
│   └── GAME_DESIGN.md
├── src/
│   ├── app.py              # Flask application
│   ├── game_engine.py      # Core game logic
│   ├── world.py            # Room/item/enemy definitions
│   ├── models.py           # Data classes
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── game.js
└── tests/
    ├── test_game_engine.py
    ├── test_api.py
    └── test_world.py
```

## 7. Dockerfile Specification

```dockerfile
# Use Chainguard's secure Python image
FROM cgr.dev/chainguard/python:latest-dev AS builder

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target=/app/deps

# Production image
FROM cgr.dev/chainguard/python:latest

WORKDIR /app

# Copy dependencies and source
COPY --from=builder /app/deps /app/deps
COPY src/ /app/

# Set Python path
ENV PYTHONPATH=/app/deps

# Expose port
EXPOSE 8080

# Run the application
ENTRYPOINT ["python", "app.py"]
```

## 8. Dependencies

### requirements.txt

```
flask==3.0.0
gunicorn==21.2.0
```

Minimal dependencies for:
- Security (less attack surface)
- Small container size
- Fast startup

## 9. Session Management

- Sessions stored in-memory (Flask session)
- Session ID is UUID4
- Session expires after 1 hour of inactivity
- No persistent storage (stateless per container restart)

## 10. Error Handling

### Backend Errors

```python
class GameError(Exception):
    def __init__(self, emoji_code: str, message: str):
        self.emoji_code = emoji_code  # For frontend display
        self.message = message        # For logging

# Examples:
# GameError("❌", "Invalid action")
# GameError("🚫", "Cannot move that direction")
# GameError("💀", "Player is dead")
```

### Frontend Error Display

All errors shown as emoji feedback:
- Invalid move: Exit button flashes ❌
- Can't take item: Item flashes 🚫
- No weapon for attack: ⚔️ button flashes ❌

## 11. Performance Considerations

1. **No database** - All state in memory
2. **Minimal assets** - Emojis are system fonts
3. **Small payload** - JSON responses < 1KB
4. **No external CDN** - Everything self-contained
5. **Efficient container** - Chainguard minimal image

---

**Document Status:** Ready for Security Review  
**Next Step:** Security Documentation
