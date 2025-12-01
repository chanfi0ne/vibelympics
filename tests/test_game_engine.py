"""Tests for the game engine."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game_engine import GameEngine


class TestNewGame:
    """Tests for new game creation."""

    def test_new_game_starts_at_house(self):
        """New game should start in the house."""
        engine = GameEngine()
        state = engine.new_game()
        assert state.current_room == "house"

    def test_new_game_has_starting_health(self):
        """New game should have 3 health."""
        engine = GameEngine()
        state = engine.new_game()
        assert state.health == 3

    def test_new_game_has_empty_inventory(self):
        """New game should have empty inventory."""
        engine = GameEngine()
        state = engine.new_game()
        assert state.inventory == []

    def test_new_game_has_sword_in_house(self):
        """House should contain the sword."""
        engine = GameEngine()
        state = engine.new_game()
        assert "🗡️" in state.room_items["house"]


class TestMovement:
    """Tests for movement actions."""

    def test_can_move_to_forest_from_house(self):
        """Should be able to move right from house to forest."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "move", {"direction": "➡️"})
        assert result.success
        assert result.state.current_room == "forest"

    def test_cannot_move_invalid_direction(self):
        """Should fail to move in direction with no exit."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "move", {"direction": "⬆️"})
        assert not result.success
        assert result.error_emoji == "🚫"


class TestItemPickup:
    """Tests for item pickup."""

    def test_can_pick_up_sword(self):
        """Should be able to pick up sword in house."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "take", {"item": "🗡️"})
        assert result.success
        assert "🗡️" in result.state.inventory
        assert "🗡️" not in result.state.room_items["house"]

    def test_cannot_pick_up_item_not_in_room(self):
        """Should fail to pick up item not present."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "take", {"item": "🔦"})
        assert not result.success


class TestCombat:
    """Tests for combat system."""

    def test_cannot_attack_without_weapon(self):
        """Should fail to attack without a weapon."""
        engine = GameEngine()
        state = engine.new_game()
        # Move to forest (has bat enemy)
        engine.perform_action(state, "move", {"direction": "➡️"})
        result = engine.perform_action(state, "attack", {})
        assert not result.success
        assert result.error_emoji == "🚫"

    def test_can_attack_with_sword(self):
        """Should be able to attack with sword."""
        engine = GameEngine()
        state = engine.new_game()
        # Pick up sword
        engine.perform_action(state, "take", {"item": "🗡️"})
        # Move to forest
        engine.perform_action(state, "move", {"direction": "➡️"})
        result = engine.perform_action(state, "attack", {})
        assert result.success

    def test_bat_defeated_in_one_hit(self):
        """Bat should be defeated in one sword hit."""
        engine = GameEngine()
        state = engine.new_game()
        engine.perform_action(state, "take", {"item": "🗡️"})
        engine.perform_action(state, "move", {"direction": "➡️"})
        result = engine.perform_action(state, "attack", {})
        assert result.event_type == "enemy_defeated"


class TestGrueMechanic:
    """Tests for grue in dark rooms."""

    def test_entering_dark_room_without_light_kills(self):
        """Entering cave without flashlight should trigger grue attack."""
        engine = GameEngine()
        state = engine.new_game()
        # Move to forest, then cave
        engine.perform_action(state, "move", {"direction": "➡️"})
        result = engine.perform_action(state, "move", {"direction": "⬇️"})
        assert result.event_type == "grue_attack"
        assert result.state.game_over

    def test_entering_dark_room_with_light_is_safe(self):
        """Entering cave with flashlight should be safe."""
        engine = GameEngine()
        state = engine.new_game()
        engine.perform_action(state, "move", {"direction": "➡️"})
        # Pick up flashlight (need to defeat bat first or just take it)
        engine.perform_action(state, "take", {"item": "🔦"})
        result = engine.perform_action(state, "move", {"direction": "⬇️"})
        assert result.success
        assert not result.state.game_over
        assert result.state.current_room == "cave"


class TestPotionUse:
    """Tests for potion healing."""

    def test_potion_heals_player(self):
        """Using potion should heal player."""
        engine = GameEngine()
        state = engine.new_game()
        state.health = 1  # Low health
        state.inventory.append("🧪")  # Give potion
        result = engine.perform_action(state, "use", {"item": "🧪"})
        assert result.success
        assert result.state.health == 3  # Healed by 2
        assert "🧪" not in result.state.inventory  # Consumed


class TestKeyMechanic:
    """Tests for key and locked doors."""

    def test_cannot_enter_locked_room_without_key(self):
        """Should not be able to enter throne room without key."""
        engine = GameEngine()
        state = engine.new_game()
        state.current_room = "dungeon"  # Skip to dungeon
        result = engine.perform_action(state, "move", {"direction": "⬇️"})
        assert not result.success
        assert result.event_type == "door_locked"

    def test_can_unlock_door_with_key(self):
        """Should be able to unlock throne room with key."""
        engine = GameEngine()
        state = engine.new_game()
        state.current_room = "dungeon"
        state.inventory.append("🔑")
        result = engine.perform_action(state, "use", {"item": "🔑"})
        assert result.success
        assert result.event_type == "door_unlocked"
        assert "throne" in result.state.unlocked_doors


class TestVictory:
    """Tests for win condition."""

    def test_picking_up_crown_wins_game(self):
        """Picking up crown should trigger victory."""
        engine = GameEngine()
        state = engine.new_game()
        state.current_room = "throne"
        state.room_items["throne"] = ["👑"]
        state.room_enemies["throne"] = []  # Remove dragon for test
        result = engine.perform_action(state, "take", {"item": "👑"})
        assert result.success
        assert result.state.victory
        assert result.state.game_over


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
