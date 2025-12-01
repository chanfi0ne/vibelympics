# Coding Standards & Quality Guidelines
# 🕳️ Emoji Zork: Development Best Practices

## 1. Overview

This document establishes coding standards to maximize the 30% Code Quality score in judging:
- Readability & structure
- Maintainability & extensibility
- Efficiency & recommended practices

## 2. Project Structure

```
emoji-zork/
├── Dockerfile              # Chainguard-based container
├── requirements.txt        # Pinned dependencies
├── README.md               # User-facing documentation
├── docs/                   # Technical documentation
│   ├── PRD.md
│   ├── TECHNICAL_SPEC.md
│   ├── SECURITY.md
│   ├── GAME_DESIGN.md
│   └── CODING_STANDARDS.md
├── src/
│   ├── app.py              # Flask application entry point
│   ├── game_engine.py      # Core game logic
│   ├── models.py           # Data classes
│   ├── world.py            # Game world definitions
│   ├── validators.py       # Input validation
│   └── static/
│       ├── index.html      # Single page app
│       ├── styles.css      # Styling & animations
│       └── game.js         # Frontend logic
└── tests/
    ├── __init__.py
    ├── conftest.py         # Pytest fixtures
    ├── test_game_engine.py
    ├── test_api.py
    └── test_validators.py
```

## 3. Python Standards

### 3.1 Style Guide

Follow PEP 8 with these specifics:

```python
# Line length: 88 characters (Black formatter default)
# Indentation: 4 spaces
# Quotes: Double quotes for strings
# Imports: Sorted with isort

# Good
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from flask import Flask, jsonify, request


# Bad
from flask import Flask,jsonify,request
from typing import *
```

### 3.2 Type Hints

All functions must have type hints:

```python
# Good
def calculate_damage(
    player_weapon: str,
    has_shield: bool
) -> int:
    """Calculate damage dealt by player."""
    base_damage = WEAPON_DAMAGE.get(player_weapon, 0)
    return base_damage


# Bad
def calculate_damage(player_weapon, has_shield):
    base_damage = WEAPON_DAMAGE.get(player_weapon, 0)
    return base_damage
```

### 3.3 Docstrings

Use Google-style docstrings:

```python
def perform_action(
    game_state: GameState,
    action: str,
    params: Dict[str, str]
) -> ActionResult:
    """Execute a game action and return the result.

    Args:
        game_state: Current game state object.
        action: Action type (move, take, attack, use).
        params: Action parameters (direction, item, etc.).

    Returns:
        ActionResult containing updated state and events.

    Raises:
        ValidationError: If action or params are invalid.
        GameOverError: If player dies during action.
    """
    pass
```

### 3.4 Constants

Use UPPER_SNAKE_CASE, group related constants:

```python
# Game constants
MAX_HEALTH = 5
STARTING_HEALTH = 3
POTION_HEAL_AMOUNT = 2

# Valid inputs (for validation)
VALID_ACTIONS = frozenset({"move", "look", "take", "attack", "use"})
VALID_DIRECTIONS = frozenset({"⬆️", "⬇️", "⬅️", "➡️"})

# Item categories
WEAPONS = frozenset({"🗡️"})
TOOLS = frozenset({"🔦", "🔑", "🗺️"})
CONSUMABLES = frozenset({"🧪"})
TREASURES = frozenset({"💎", "👑"})
```

### 3.5 Data Classes

Use `@dataclass` for data structures:

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Room:
    """Represents a room in the game world."""
    
    id: str
    emoji: str
    items: List[str] = field(default_factory=list)
    exits: Dict[str, str] = field(default_factory=dict)
    is_dark: bool = False
    locked_exits: Dict[str, str] = field(default_factory=dict)

    def has_exit(self, direction: str) -> bool:
        """Check if room has an exit in the given direction."""
        return direction in self.exits


@dataclass
class Enemy:
    """Represents an enemy in the game."""
    
    emoji: str
    health: int
    max_health: int
    damage: int
    is_grue: bool = False

    @property
    def is_alive(self) -> bool:
        """Check if enemy is still alive."""
        return self.health > 0

    def take_damage(self, amount: int) -> None:
        """Apply damage to enemy."""
        self.health = max(0, self.health - amount)
```

### 3.6 Error Handling

Create specific exceptions:

```python
class GameError(Exception):
    """Base exception for game errors."""
    
    def __init__(self, emoji_code: str, message: str):
        self.emoji_code = emoji_code
        self.message = message
        super().__init__(message)


class ValidationError(GameError):
    """Raised for invalid input."""
    pass


class InvalidActionError(GameError):
    """Raised for impossible actions."""
    pass


class GameOverError(GameError):
    """Raised when player dies."""
    pass


# Usage
try:
    result = game_engine.perform_action(state, action, params)
except ValidationError as e:
    return jsonify({"error": e.emoji_code}), 400
except GameOverError as e:
    return jsonify({"error": "💀", "game_over": True}), 200
```

## 4. JavaScript Standards

### 4.1 Style Guide

```javascript
// Use const/let, never var
const GAME_CONFIG = {
    apiUrl: '/api',
    animationDuration: 300
};

let gameState = null;

// Use arrow functions for callbacks
document.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('click', handleAction);
});

// Use async/await for promises
async function fetchGameState() {
    try {
        const response = await fetch(`${GAME_CONFIG.apiUrl}/state`);
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch state:', error);
        throw error;
    }
}
```

### 4.2 Class Structure

```javascript
/**
 * Main game controller.
 */
class EmojiZorkGame {
    constructor() {
        this.sessionId = null;
        this.state = null;
        this.isAnimating = false;
    }

    /**
     * Initialize game and bind events.
     */
    async init() {
        await this.newGame();
        this.bindEvents();
        this.render();
    }

    /**
     * Bind all UI event handlers.
     */
    bindEvents() {
        // Navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => this.handleMove(btn.dataset.dir));
        });

        // Action buttons
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', () => this.handleAction(btn.dataset.action));
        });
    }

    // ... more methods
}
```

### 4.3 DOM Manipulation

```javascript
// Use textContent for text (XSS safe)
element.textContent = state.location;

// Use classList for classes
element.classList.add('active');
element.classList.remove('disabled');
element.classList.toggle('hidden');

// Use data attributes for data
const direction = button.dataset.direction;
const action = button.dataset.action;

// Cache DOM queries
const elements = {
    location: document.getElementById('location'),
    health: document.getElementById('health'),
    score: document.getElementById('score'),
    inventory: document.getElementById('inventory-slots')
};
```

## 5. HTML/CSS Standards

### 5.1 HTML Structure

```html
<!-- Semantic elements -->
<main id="game-container">
    <header id="status-bar">...</header>
    <section id="room-view">...</section>
    <aside id="inventory">...</aside>
    <nav id="controls">...</nav>
</main>

<!-- Data attributes for JS hooks -->
<button class="nav-btn" data-dir="⬆️">⬆️</button>

<!-- ARIA labels for accessibility (even with emojis) -->
<button class="action-btn" data-action="attack" aria-label="Attack">⚔️</button>
```

### 5.2 CSS Organization

```css
/* ==========================================================================
   1. Variables & Tokens
   ========================================================================== */
:root {
    --color-bg: #1a1a2e;
    --color-panel: #16213e;
    --color-accent: #e94560;
    --color-text: #ffffff;
    
    --emoji-size-sm: 1.5rem;
    --emoji-size-md: 2rem;
    --emoji-size-lg: 4rem;
    
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 2rem;
    
    --animation-fast: 150ms;
    --animation-normal: 300ms;
    --animation-slow: 500ms;
}

/* ==========================================================================
   2. Base Styles
   ========================================================================== */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

/* ==========================================================================
   3. Layout Components
   ========================================================================== */
#game-container {
    display: grid;
    grid-template-rows: auto 1fr auto auto;
    height: 100vh;
}

/* ==========================================================================
   4. UI Components
   ========================================================================== */
.btn {
    /* Base button styles */
}

.nav-btn {
    /* Navigation button specifics */
}

/* ==========================================================================
   5. Animations
   ========================================================================== */
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.shake {
    animation: shake var(--animation-fast) ease-in-out;
}
```

## 6. Testing Standards

### 6.1 Test File Structure

```python
# test_game_engine.py

import pytest
from src.game_engine import GameEngine
from src.models import GameState, Enemy


class TestCombat:
    """Tests for combat system."""

    def test_attack_with_weapon_deals_damage(self, game_with_sword):
        """Player with sword should deal damage to enemy."""
        initial_health = game_with_sword.current_enemy.health
        game_with_sword.perform_attack()
        assert game_with_sword.current_enemy.health < initial_health

    def test_attack_without_weapon_fails(self, game_without_sword):
        """Player without weapon should not be able to attack."""
        with pytest.raises(InvalidActionError):
            game_without_sword.perform_attack()


class TestGrueMechanic:
    """Tests for grue behavior in dark rooms."""

    def test_entering_dark_room_without_light_kills_player(self):
        """Grue should instantly kill player in darkness."""
        pass

    def test_entering_dark_room_with_flashlight_is_safe(self):
        """Flashlight should prevent grue attack."""
        pass
```

### 6.2 Fixtures

```python
# conftest.py

import pytest
from src.game_engine import GameEngine
from src.models import GameState


@pytest.fixture
def fresh_game() -> GameEngine:
    """Create a new game in starting state."""
    return GameEngine()


@pytest.fixture
def game_with_sword(fresh_game) -> GameEngine:
    """Game where player has picked up sword."""
    fresh_game.perform_take("🗡️")
    return fresh_game


@pytest.fixture
def game_at_cave(fresh_game) -> GameEngine:
    """Game with player at cave entrance."""
    fresh_game.perform_move("➡️")  # Forest
    fresh_game.perform_move("⬇️")  # Cave
    return fresh_game
```

### 6.3 Test Coverage Requirements

- Minimum 80% code coverage
- 100% coverage for:
  - Input validation
  - Combat calculations
  - Win/lose conditions
  - Security-critical code

## 7. Documentation Standards

### 7.1 Code Comments

```python
# Good: Explain WHY, not WHAT
# We check for light source before room entry to prevent
# the grue attack sequence which is an instant death condition
if room.is_dark and not player.has_light:
    raise GrueAttackError()

# Bad: Obvious comment
# Check if room is dark
if room.is_dark:
    pass
```

### 7.2 README Requirements

- How to build the container
- How to run the game
- Brief gameplay instructions (in emoji!)
- Architecture overview

## 8. Git Standards

### 8.1 Commit Messages

```
feat: add combat system with damage calculation

- Implement player attack action
- Add enemy counter-attack logic
- Include shield damage reduction
- Add tests for combat scenarios

Closes #12
```

Format:
```
<type>: <short description>

<detailed description if needed>

<references>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### 8.2 Branch Naming

```
feature/combat-system
fix/grue-attack-animation
docs/readme-update
```

## 9. Performance Guidelines

### 9.1 Backend

```python
# Cache world data (it's static)
WORLD_CACHE = None

def get_world() -> Dict[str, Room]:
    global WORLD_CACHE
    if WORLD_CACHE is None:
        WORLD_CACHE = load_world()
    return WORLD_CACHE

# Use generators for large iterations
def find_items_in_world():
    for room in get_world().values():
        yield from room.items
```

### 9.2 Frontend

```javascript
// Debounce rapid clicks
let lastClick = 0;
function handleClick(event) {
    const now = Date.now();
    if (now - lastClick < 200) return;
    lastClick = now;
    // ... handle click
}

// Batch DOM updates
function renderInventory(items) {
    const fragment = document.createDocumentFragment();
    items.forEach(item => {
        const span = document.createElement('span');
        span.textContent = item;
        fragment.appendChild(span);
    });
    inventoryEl.innerHTML = '';
    inventoryEl.appendChild(fragment);
}
```

## 10. Security Coding Checklist

Before each commit, verify:

- [ ] No `eval()` or `exec()` anywhere
- [ ] No `innerHTML` with user data
- [ ] All inputs validated server-side
- [ ] No secrets in code or logs
- [ ] Error messages don't leak info
- [ ] Type hints on all functions
- [ ] Tests for edge cases

---

**Document Status:** Complete  
**Apply to:** All code in this project
