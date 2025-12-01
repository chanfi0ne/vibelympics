"""Game world definitions for Emoji Zork."""

from models import Enemy, Room

# Enemy templates (will be cloned for each game)
ENEMY_TEMPLATES: dict[str, Enemy] = {
    "bat": Enemy(emoji="🦇", health=1, max_health=1, damage=1),
    "troll": Enemy(emoji="👹", health=3, max_health=3, damage=1),
    "dragon": Enemy(emoji="🐉", health=5, max_health=5, damage=2),
    "grue": Enemy(emoji="🐺", health=999, max_health=999, damage=999, is_grue=True),
}

# Item definitions
ITEMS = {
    "🗡️": {"name": "sword", "type": "weapon", "damage": 2},
    "🔦": {"name": "flashlight", "type": "tool"},
    "🔑": {"name": "key", "type": "tool"},
    "🧪": {"name": "potion", "type": "consumable", "heal": 2},
    "💎": {"name": "diamond", "type": "treasure", "score": 50},
    "🛡️": {"name": "shield", "type": "armor"},
    "🗺️": {"name": "map", "type": "tool"},
    "👑": {"name": "crown", "type": "treasure", "score": 100, "win": True},
}

# Score values for defeating enemies
ENEMY_SCORES = {
    "🦇": 10,
    "👹": 25,
    "🐉": 50,
}


def create_world() -> dict[str, Room]:
    """Create the game world with all rooms."""
    return {
        "house": Room(
            id="house",
            emoji="🏠",
            items=["🗡️"],
            enemies=[],
            exits={"➡️": "forest"},
            is_dark=False,
        ),
        "forest": Room(
            id="forest",
            emoji="🌲",
            items=["🔦"],
            enemies=[ENEMY_TEMPLATES["bat"].clone()],
            exits={
                "⬅️": "house",
                "➡️": "river",
                "⬇️": "cave",
                "⬆️": "temple",
            },
            is_dark=False,
        ),
        "river": Room(
            id="river",
            emoji="💧",
            items=["💎"],
            enemies=[],
            exits={"⬅️": "forest"},
            is_dark=False,
        ),
        "temple": Room(
            id="temple",
            emoji="⛪",
            items=["🧪"],
            enemies=[ENEMY_TEMPLATES["troll"].clone()],
            exits={"⬇️": "forest"},
            is_dark=False,
        ),
        "cave": Room(
            id="cave",
            emoji="🕳️",
            items=["🛡️"],
            enemies=[ENEMY_TEMPLATES["grue"].clone()],
            exits={
                "⬆️": "forest",
                "⬇️": "dungeon",
            },
            is_dark=True,
        ),
        "dungeon": Room(
            id="dungeon",
            emoji="🏰",
            items=["🗺️"],
            enemies=[ENEMY_TEMPLATES["troll"].clone()],
            exits={"⬆️": "cave"},
            locked_exits={"⬇️": "throne"},
            is_dark=False,
        ),
        "throne": Room(
            id="throne",
            emoji="👑",
            items=["👑"],
            enemies=[ENEMY_TEMPLATES["dragon"].clone()],
            exits={"⬆️": "dungeon"},
            is_dark=False,
        ),
    }


def get_initial_room_items(world: dict[str, Room]) -> dict[str, list[str]]:
    """Extract initial item placement from world."""
    return {room_id: list(room.items) for room_id, room in world.items()}


def get_initial_room_enemies(world: dict[str, Room]) -> dict[str, list[Enemy]]:
    """Extract initial enemy placement from world, cloning enemies."""
    return {
        room_id: [e.clone() for e in room.enemies] for room_id, room in world.items()
    }
