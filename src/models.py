"""Data models for Emoji Zork game."""

from dataclasses import dataclass, field


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

    def clone(self) -> "Enemy":
        """Create a copy of this enemy."""
        return Enemy(
            emoji=self.emoji,
            health=self.health,
            max_health=self.max_health,
            damage=self.damage,
            is_grue=self.is_grue,
        )


@dataclass
class Room:
    """Represents a room in the game world."""

    id: str
    emoji: str
    items: list[str] = field(default_factory=list)
    enemies: list[Enemy] = field(default_factory=list)
    exits: dict[str, str] = field(default_factory=dict)
    is_dark: bool = False
    locked_exits: dict[str, str] = field(default_factory=dict)

    def has_exit(self, direction: str) -> bool:
        """Check if room has an exit in the given direction."""
        return direction in self.exits or direction in self.locked_exits

    def get_available_exits(self, unlocked: set) -> dict[str, str]:
        """Get all currently available exits."""
        exits = dict(self.exits)
        for direction, room_id in self.locked_exits.items():
            if room_id in unlocked:
                exits[direction] = room_id
        return exits


@dataclass
class GameState:
    """Represents the current state of a game session."""

    current_room: str = "house"
    health: int = 3
    max_health: int = 5
    inventory: list[str] = field(default_factory=list)
    score: int = 0
    room_items: dict[str, list[str]] = field(default_factory=dict)
    room_enemies: dict[str, list[Enemy]] = field(default_factory=dict)
    unlocked_doors: set = field(default_factory=set)
    game_over: bool = False
    victory: bool = False

    @property
    def has_light(self) -> bool:
        """Check if player has a light source."""
        return "🔦" in self.inventory

    @property
    def has_weapon(self) -> bool:
        """Check if player has a weapon."""
        return "🗡️" in self.inventory

    @property
    def has_shield(self) -> bool:
        """Check if player has a shield."""
        return "🛡️" in self.inventory

    def take_damage(self, amount: int) -> None:
        """Apply damage to player, accounting for shield."""
        actual_damage = max(1, amount - (1 if self.has_shield else 0))
        self.health = max(0, self.health - actual_damage)
        if self.health <= 0:
            self.game_over = True

    def heal(self, amount: int) -> None:
        """Heal player up to max health."""
        self.health = min(self.max_health, self.health + amount)

    def add_score(self, points: int) -> None:
        """Add points to score."""
        self.score += points


@dataclass
class ActionResult:
    """Result of performing a game action."""

    success: bool
    state: GameState
    event_type: str | None = None
    event_data: dict | None = None
    error_emoji: str | None = None
