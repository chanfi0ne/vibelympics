"""Core game engine for Emoji Zork."""

from models import ActionResult, GameState, Room
from world import (
    ENEMY_SCORES,
    ITEMS,
    create_world,
    get_initial_room_enemies,
    get_initial_room_items,
)

# Valid inputs
VALID_ACTIONS = frozenset({"move", "look", "take", "attack", "use"})
VALID_DIRECTIONS = frozenset({"⬆️", "⬇️", "⬅️", "➡️"})
VALID_ITEMS = frozenset(ITEMS.keys())


class GameEngine:
    """Manages game state and logic."""

    def __init__(self):
        self.world = create_world()

    def new_game(self) -> GameState:
        """Create a new game state."""
        return GameState(
            current_room="house",
            health=3,
            max_health=5,
            inventory=[],
            score=0,
            room_items=get_initial_room_items(self.world),
            room_enemies=get_initial_room_enemies(self.world),
            unlocked_doors=set(),
            game_over=False,
            victory=False,
        )

    def get_current_room(self, state: GameState) -> Room:
        """Get the current room object."""
        return self.world[state.current_room]

    def get_room_display(self, state: GameState) -> dict:
        """Get display data for current room."""
        room = self.get_current_room(state)
        items = state.room_items.get(state.current_room, [])
        enemies = state.room_enemies.get(state.current_room, [])
        alive_enemies = [e for e in enemies if e.is_alive]

        # Show dark room differently
        display_emoji = "🌑" if room.is_dark and not state.has_light else room.emoji

        # Get available exits
        exits = room.get_available_exits(state.unlocked_doors)

        return {
            "location": display_emoji,
            "location_id": room.id,
            "items": items,
            "enemies": [{"emoji": e.emoji, "health": e.health} for e in alive_enemies],
            "exits": list(exits.keys()),
            "is_dark": room.is_dark and not state.has_light,
        }

    def perform_action(
        self, state: GameState, action: str, params: dict
    ) -> ActionResult:
        """Perform a game action and return the result."""
        if state.game_over:
            return ActionResult(success=False, state=state, error_emoji="💀")

        if action not in VALID_ACTIONS:
            return ActionResult(success=False, state=state, error_emoji="❓")

        # Dispatch to action handlers
        handlers = {
            "move": self._handle_move,
            "look": self._handle_look,
            "take": self._handle_take,
            "attack": self._handle_attack,
            "use": self._handle_use,
        }

        return handlers[action](state, params)

    def _handle_move(self, state: GameState, params: dict) -> ActionResult:
        """Handle move action."""
        direction = params.get("direction")
        if direction not in VALID_DIRECTIONS:
            return ActionResult(success=False, state=state, error_emoji="❓")

        room = self.get_current_room(state)
        exits = room.get_available_exits(state.unlocked_doors)

        if direction not in exits:
            # Check if it's a locked exit
            if direction in room.locked_exits:
                return ActionResult(
                    success=False,
                    state=state,
                    event_type="door_locked",
                    error_emoji="🔒",
                )
            return ActionResult(success=False, state=state, error_emoji="🚫")

        # Move to new room
        new_room_id = exits[direction]
        state.current_room = new_room_id

        # Check for grue attack in dark rooms
        new_room = self.world[new_room_id]
        if new_room.is_dark and not state.has_light:
            state.game_over = True
            return ActionResult(
                success=True,
                state=state,
                event_type="grue_attack",
            )

        return ActionResult(
            success=True,
            state=state,
            event_type="room_entered",
            event_data={"room": new_room_id},
        )

    def _handle_look(self, state: GameState, params: dict) -> ActionResult:
        """Handle look action - refresh room view."""
        return ActionResult(
            success=True,
            state=state,
            event_type="looked",
        )

    def _handle_take(self, state: GameState, params: dict) -> ActionResult:
        """Handle take action - pick up an item."""
        item = params.get("item")
        if not item or item not in VALID_ITEMS:
            return ActionResult(success=False, state=state, error_emoji="❓")

        room_items = state.room_items.get(state.current_room, [])
        if item not in room_items:
            return ActionResult(success=False, state=state, error_emoji="🚫")

        # Check for enemies in the room - must defeat them first!
        enemies = state.room_enemies.get(state.current_room, [])
        alive_enemies = [e for e in enemies if e.is_alive]

        if alive_enemies:
            # Cannot take items while enemies are present
            return ActionResult(success=False, state=state, error_emoji="⚔️")

        # Pick up item
        room_items.remove(item)
        state.inventory.append(item)

        # Handle treasure scoring
        item_data = ITEMS.get(item, {})
        if item_data.get("score"):
            state.add_score(item_data["score"])

        # Check win condition
        if item_data.get("win"):
            state.victory = True
            state.game_over = True

        return ActionResult(
            success=True,
            state=state,
            event_type="item_taken",
            event_data={"item": item},
        )

    def _handle_attack(self, state: GameState, params: dict) -> ActionResult:
        """Handle attack action - fight an enemy."""
        if not state.has_weapon:
            return ActionResult(success=False, state=state, error_emoji="🚫")

        enemies = state.room_enemies.get(state.current_room, [])
        alive_enemies = [e for e in enemies if e.is_alive]

        if not alive_enemies:
            return ActionResult(success=False, state=state, error_emoji="🚫")

        # Attack first alive enemy
        enemy = alive_enemies[0]

        # Player attacks
        damage = ITEMS["🗡️"]["damage"]
        enemy.take_damage(damage)

        event_data = {"enemy": enemy.emoji, "damage_dealt": damage}

        # Check if enemy defeated
        if not enemy.is_alive:
            score = ENEMY_SCORES.get(enemy.emoji, 0)
            state.add_score(score)

            # Troll in temple drops key when defeated
            if enemy.emoji == "👹" and state.current_room == "temple":
                if "🔑" not in state.room_items.get("temple", []):
                    state.room_items.setdefault("temple", []).append("🔑")

            return ActionResult(
                success=True,
                state=state,
                event_type="enemy_defeated",
                event_data=event_data,
            )

        # Enemy counter-attacks
        state.take_damage(enemy.damage)
        event_data["damage_taken"] = enemy.damage

        if state.game_over:
            return ActionResult(
                success=True,
                state=state,
                event_type="player_died",
                event_data=event_data,
            )

        return ActionResult(
            success=True,
            state=state,
            event_type="combat_round",
            event_data=event_data,
        )

    def _handle_use(self, state: GameState, params: dict) -> ActionResult:
        """Handle use action - use an item from inventory."""
        item = params.get("item")
        if not item or item not in state.inventory:
            return ActionResult(success=False, state=state, error_emoji="🚫")

        item_data = ITEMS.get(item, {})

        # Handle potion
        if item == "🧪":
            heal_amount = item_data.get("heal", 2)
            state.heal(heal_amount)
            state.inventory.remove(item)
            return ActionResult(
                success=True,
                state=state,
                event_type="healed",
                event_data={"amount": heal_amount},
            )

        # Handle key
        if item == "🔑":
            room = self.get_current_room(state)
            if room.locked_exits:
                # Unlock all locked exits in current room
                for direction, room_id in room.locked_exits.items():
                    state.unlocked_doors.add(room_id)
                state.inventory.remove(item)
                return ActionResult(
                    success=True,
                    state=state,
                    event_type="door_unlocked",
                )
            return ActionResult(success=False, state=state, error_emoji="🚫")

        # Other items don't have use actions
        return ActionResult(success=False, state=state, error_emoji="🚫")

    def get_state_for_client(self, state: GameState) -> dict:
        """Convert game state to client-friendly format."""
        room_display = self.get_room_display(state)
        return {
            "location": room_display["location"],
            "location_id": room_display["location_id"],
            "health": state.health,
            "max_health": state.max_health,
            "score": state.score,
            "inventory": state.inventory,
            "room_items": room_display["items"],
            "room_enemies": room_display["enemies"],
            "exits": room_display["exits"],
            "is_dark": room_display["is_dark"],
            "game_over": state.game_over,
            "victory": state.victory,
        }
