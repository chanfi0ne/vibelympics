"""Integration tests for complete gameplay sequences."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game_engine import GameEngine


class TestCombatItemInteraction:
    """Tests for item pickup while enemies are present."""

    def test_cannot_take_item_with_enemy_present_and_takes_damage(self):
        """Taking an item while enemy alive should be blocked AND deal damage."""
        engine = GameEngine()
        state = engine.new_game()
        # Move to forest (has bat)
        engine.perform_action(state, "move", {"direction": "➡️"})
        initial_health = state.health
        # Try to take flashlight while bat is alive - should fail and take damage
        result = engine.perform_action(state, "take", {"item": "🔦"})
        assert not result.success
        assert result.error_emoji == "⚔️"  # Combat required
        assert "🔦" not in state.inventory  # Item not taken
        assert "🔦" in state.room_items["forest"]  # Item still in room
        assert state.health < initial_health  # Took damage from enemy

    def test_taking_item_with_enemy_can_kill_player(self):
        """Trying to take item at low health can result in death."""
        engine = GameEngine()
        state = engine.new_game()
        # Move to forest (has bat)
        engine.perform_action(state, "move", {"direction": "➡️"})
        state.health = 1  # Low health
        # Try to take flashlight - bat attacks and kills player
        result = engine.perform_action(state, "take", {"item": "🔦"})
        assert not result.success
        assert result.state.game_over
        assert result.event_type == "player_died"

    def test_taking_item_without_enemy_is_safe(self):
        """Taking an item with no enemies should work normally."""
        engine = GameEngine()
        state = engine.new_game()
        initial_health = state.health
        # Take sword in house (no enemies)
        result = engine.perform_action(state, "take", {"item": "🗡️"})
        assert result.success
        assert result.state.health == initial_health

    def test_taking_item_after_killing_enemy_works(self):
        """Taking item after defeating enemy should work."""
        engine = GameEngine()
        state = engine.new_game()
        engine.perform_action(state, "take", {"item": "🗡️"})
        engine.perform_action(state, "move", {"direction": "➡️"})
        # Kill the bat
        engine.perform_action(state, "attack", {})
        initial_health = state.health
        # Now take flashlight - should work
        result = engine.perform_action(state, "take", {"item": "🔦"})
        assert result.success
        assert result.state.health == initial_health
        assert "🔦" in state.inventory


class TestTrollVariants:
    """Tests for different troll types."""

    def test_temple_troll_has_different_emoji_than_dungeon(self):
        """Temple and dungeon trolls should have different emojis."""
        engine = GameEngine()
        state = engine.new_game()
        temple_enemies = state.room_enemies.get("temple", [])
        dungeon_enemies = state.room_enemies.get("dungeon", [])
        # Find trolls by health (3 HP)
        temple_troll = next((e for e in temple_enemies if e.health == 3), None)
        dungeon_troll = next((e for e in dungeon_enemies if e.health == 3), None)
        assert temple_troll is not None
        assert dungeon_troll is not None
        assert temple_troll.emoji != dungeon_troll.emoji

    def test_temple_troll_drops_key(self):
        """Temple troll should drop key when defeated."""
        engine = GameEngine()
        state = engine.new_game()
        state.inventory = ["🗡️"]
        state.current_room = "temple"
        # Kill troll
        for enemy in state.room_enemies["temple"]:
            enemy.health = 1
        engine.perform_action(state, "attack", {})
        assert "🔑" in state.room_items.get("temple", [])

    def test_dungeon_troll_does_not_drop_key(self):
        """Dungeon troll should NOT drop key when defeated."""
        engine = GameEngine()
        state = engine.new_game()
        state.inventory = ["🗡️"]
        state.current_room = "dungeon"
        # Kill dungeon troll
        for enemy in state.room_enemies["dungeon"]:
            enemy.health = 1
        engine.perform_action(state, "attack", {})
        assert "🔑" not in state.room_items.get("dungeon", [])


class TestCompletePlaythrough:
    """Tests for complete game playthroughs."""

    def test_optimal_path_victory(self):
        """Test optimal path: house->forest->temple->forest->cave->dungeon->throne."""
        engine = GameEngine()
        state = engine.new_game()

        # House: take sword
        result = engine.perform_action(state, "take", {"item": "🗡️"})
        assert result.success

        # Move to forest
        result = engine.perform_action(state, "move", {"direction": "➡️"})
        assert state.current_room == "forest"

        # Kill bat
        result = engine.perform_action(state, "attack", {})
        assert result.event_type == "enemy_defeated"

        # Take flashlight
        result = engine.perform_action(state, "take", {"item": "🔦"})
        assert result.success

        # Go to temple (up from forest)
        result = engine.perform_action(state, "move", {"direction": "⬆️"})
        assert state.current_room == "temple"

        # Kill temple troll (2 hits: sword does 2 damage, troll has 3 HP)
        result = engine.perform_action(state, "attack", {})
        assert result.event_type == "combat_round"
        result = engine.perform_action(state, "attack", {})
        assert result.event_type == "enemy_defeated"

        # Take key dropped by troll
        result = engine.perform_action(state, "take", {"item": "🔑"})
        assert result.success
        assert "🔑" in state.inventory

        # Take potion
        result = engine.perform_action(state, "take", {"item": "🧪"})
        assert result.success

        # Go back to forest
        result = engine.perform_action(state, "move", {"direction": "⬇️"})
        assert state.current_room == "forest"

        # Go to cave
        result = engine.perform_action(state, "move", {"direction": "⬇️"})
        assert state.current_room == "cave"
        assert not state.game_over  # Has flashlight, so no grue

        # Go to dungeon
        result = engine.perform_action(state, "move", {"direction": "⬇️"})
        assert state.current_room == "dungeon"

        # Kill dungeon troll
        result = engine.perform_action(state, "attack", {})
        result = engine.perform_action(state, "attack", {})

        # Use key to unlock throne room
        result = engine.perform_action(state, "use", {"item": "🔑"})
        assert result.event_type == "door_unlocked"

        # Enter throne room
        result = engine.perform_action(state, "move", {"direction": "⬇️"})
        assert state.current_room == "throne"

        # Use potion if needed
        if state.health < 3:
            engine.perform_action(state, "use", {"item": "🧪"})

        # Kill dragon (5 HP, sword does 2, so 3 hits)
        for _ in range(3):
            result = engine.perform_action(state, "attack", {})
            if result.state.game_over and not result.state.victory:
                break  # Player died

        # Take crown for victory (if still alive)
        if not state.game_over:
            result = engine.perform_action(state, "take", {"item": "👑"})
            assert result.success
            assert result.state.victory

    def test_death_by_grue(self):
        """Test that entering cave without light causes grue death."""
        engine = GameEngine()
        state = engine.new_game()

        engine.perform_action(state, "move", {"direction": "➡️"})  # forest
        result = engine.perform_action(state, "move", {"direction": "⬇️"})  # cave

        assert result.event_type == "grue_attack"
        assert state.game_over
        assert not state.victory

    def test_death_in_combat(self):
        """Test player death from enemy damage."""
        engine = GameEngine()
        state = engine.new_game()

        engine.perform_action(state, "take", {"item": "🗡️"})
        engine.perform_action(state, "move", {"direction": "➡️"})  # forest
        engine.perform_action(state, "attack", {})  # kill bat
        engine.perform_action(state, "move", {"direction": "⬆️"})  # temple

        # Fight troll at low health
        state.health = 1
        result = engine.perform_action(state, "attack", {})

        assert result.state.game_over
        assert result.event_type == "player_died"

    def test_fleeing_from_combat(self):
        """Test that player can flee from combat by moving away."""
        engine = GameEngine()
        state = engine.new_game()

        engine.perform_action(state, "move", {"direction": "➡️"})  # forest with bat
        initial_health = state.health

        # Flee back to house
        result = engine.perform_action(state, "move", {"direction": "⬅️"})
        assert result.success
        assert state.current_room == "house"
        assert state.health == initial_health  # No damage from fleeing


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_invalid_direction(self):
        """Test moving in invalid direction."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "move", {"direction": "⬆️"})
        assert not result.success
        assert result.error_emoji == "🚫"

    def test_take_nonexistent_item(self):
        """Test taking item not in room."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "take", {"item": "👑"})
        assert not result.success
        assert result.error_emoji == "🚫"

    def test_attack_without_weapon(self):
        """Test attacking without weapon equipped."""
        engine = GameEngine()
        state = engine.new_game()
        engine.perform_action(state, "move", {"direction": "➡️"})  # forest
        result = engine.perform_action(state, "attack", {})
        assert not result.success
        assert result.error_emoji == "🚫"

    def test_use_item_not_in_inventory(self):
        """Test using item not in inventory."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "use", {"item": "🔑"})
        assert not result.success
        assert result.error_emoji == "🚫"

    def test_locked_door_without_key(self):
        """Test entering locked room without key."""
        engine = GameEngine()
        state = engine.new_game()
        state.current_room = "dungeon"
        result = engine.perform_action(state, "move", {"direction": "⬇️"})
        assert not result.success
        assert result.event_type == "door_locked"
        assert result.error_emoji == "🔒"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
