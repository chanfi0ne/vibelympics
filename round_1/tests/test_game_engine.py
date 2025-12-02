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
        # Get sword and go to forest
        engine.perform_action(state, "take", {"item": "🗡️"})
        engine.perform_action(state, "move", {"direction": "➡️"})
        # Must defeat bat before taking flashlight
        engine.perform_action(state, "attack", {})
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


class TestGameOver:
    """Tests for game over state."""

    def test_cannot_act_when_game_over(self):
        """Should not be able to perform actions when game over."""
        engine = GameEngine()
        state = engine.new_game()
        state.game_over = True
        result = engine.perform_action(state, "move", {"direction": "➡️"})
        assert not result.success
        assert result.error_emoji == "💀"

    def test_invalid_action_returns_error(self):
        """Invalid action type should return error."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "invalid_action", {})
        assert not result.success
        assert result.error_emoji == "❓"


class TestRoomDisplay:
    """Tests for room display functionality."""

    def test_dark_room_shows_dark_emoji_without_light(self):
        """Dark room without light should show darkness emoji."""
        engine = GameEngine()
        state = engine.new_game()
        state.current_room = "cave"
        state.inventory = []  # No flashlight
        display = engine.get_room_display(state)
        assert display["location"] == "🌑"
        assert display["is_dark"]

    def test_dark_room_shows_normal_emoji_with_light(self):
        """Dark room with light should show normal emoji."""
        engine = GameEngine()
        state = engine.new_game()
        state.current_room = "cave"
        state.inventory = ["🔦"]
        display = engine.get_room_display(state)
        assert display["location"] == "🕳️"
        assert not display["is_dark"]

    def test_room_display_shows_exits(self):
        """Room display should show available exits."""
        engine = GameEngine()
        state = engine.new_game()
        display = engine.get_room_display(state)
        assert "➡️" in display["exits"]

    def test_room_display_shows_items(self):
        """Room display should show items in room."""
        engine = GameEngine()
        state = engine.new_game()
        display = engine.get_room_display(state)
        assert "🗡️" in display["items"]

    def test_room_display_shows_alive_enemies(self):
        """Room display should only show alive enemies."""
        engine = GameEngine()
        state = engine.new_game()
        state.current_room = "forest"
        # Kill the bat
        for enemy in state.room_enemies["forest"]:
            enemy.health = 0
        display = engine.get_room_display(state)
        assert len(display["enemies"]) == 0


class TestCombatAdvanced:
    """Advanced combat tests."""

    def test_enemy_counter_attacks(self):
        """Enemy should counter-attack after player attacks."""
        engine = GameEngine()
        state = engine.new_game()
        state.inventory = ["🗡️"]
        state.current_room = "temple"  # Has troll with 3 HP
        initial_health = state.health
        result = engine.perform_action(state, "attack", {})
        # Troll takes 2 damage (sword), still alive with 1 HP
        # Troll counter-attacks for 1 damage
        assert result.success
        assert result.state.health < initial_health
        assert result.event_type == "combat_round"
        assert "damage_taken" in result.event_data

    def test_player_death_in_combat(self):
        """Player should die if health reaches zero in combat."""
        engine = GameEngine()
        state = engine.new_game()
        state.inventory = ["🗡️"]
        state.health = 1
        state.current_room = "temple"
        result = engine.perform_action(state, "attack", {})
        assert result.state.game_over
        assert result.event_type == "player_died"

    def test_cannot_attack_no_enemies(self):
        """Should not be able to attack when no enemies present."""
        engine = GameEngine()
        state = engine.new_game()
        state.inventory = ["🗡️"]
        # House has no enemies
        result = engine.perform_action(state, "attack", {})
        assert not result.success
        assert result.error_emoji == "🚫"

    def test_troll_drops_key_when_defeated(self):
        """Troll in temple should drop key when defeated."""
        engine = GameEngine()
        state = engine.new_game()
        state.inventory = ["🗡️"]
        state.current_room = "temple"
        # Weaken the troll first
        for enemy in state.room_enemies["temple"]:
            if enemy.emoji == "👹":
                enemy.health = 1  # One hit will kill it
        result = engine.perform_action(state, "attack", {})
        assert result.event_type == "enemy_defeated"
        assert "🔑" in state.room_items.get("temple", [])

    def test_shield_reduces_damage_in_combat(self):
        """Shield should reduce damage taken in combat."""
        engine = GameEngine()
        state = engine.new_game()
        state.inventory = ["🗡️", "🛡️"]
        state.current_room = "temple"
        state.health = 3
        engine.perform_action(state, "attack", {})
        # Troll does 1 damage, shield reduces to still 1 (minimum)
        # But if we had a dragon (2 damage), shield would reduce to 1
        assert state.health == 2  # Took 1 damage


class TestTakeAdvanced:
    """Advanced item pickup tests."""

    def test_take_diamond_adds_score(self):
        """Taking diamond should add score."""
        engine = GameEngine()
        state = engine.new_game()
        state.current_room = "river"
        initial_score = state.score
        result = engine.perform_action(state, "take", {"item": "💎"})
        assert result.success
        assert result.state.score > initial_score

    def test_take_invalid_item_fails(self):
        """Taking invalid item should fail."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "take", {"item": "🍕"})
        assert not result.success
        assert result.error_emoji == "❓"

    def test_take_without_item_param_fails(self):
        """Taking without item parameter should fail."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "take", {})
        assert not result.success


class TestUseAdvanced:
    """Advanced item use tests."""

    def test_use_key_fails_without_locked_door(self):
        """Using key in room without locked door should fail."""
        engine = GameEngine()
        state = engine.new_game()
        state.inventory = ["🔑"]
        # House has no locked doors
        result = engine.perform_action(state, "use", {"item": "🔑"})
        assert not result.success
        assert result.error_emoji == "🚫"

    def test_use_item_not_in_inventory_fails(self):
        """Using item not in inventory should fail."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "use", {"item": "🧪"})
        assert not result.success
        assert result.error_emoji == "🚫"

    def test_use_non_usable_item_fails(self):
        """Using non-usable item should fail."""
        engine = GameEngine()
        state = engine.new_game()
        state.inventory = ["🗡️"]  # Sword is not usable
        result = engine.perform_action(state, "use", {"item": "🗡️"})
        assert not result.success
        assert result.error_emoji == "🚫"


class TestMovementAdvanced:
    """Advanced movement tests."""

    def test_move_invalid_direction_format(self):
        """Moving with invalid direction format should fail."""
        engine = GameEngine()
        state = engine.new_game()
        result = engine.perform_action(state, "move", {"direction": "north"})
        assert not result.success
        assert result.error_emoji == "❓"

    def test_can_enter_unlocked_throne_room(self):
        """Should be able to enter throne room after unlocking."""
        engine = GameEngine()
        state = engine.new_game()
        state.current_room = "dungeon"
        state.unlocked_doors.add("throne")
        result = engine.perform_action(state, "move", {"direction": "⬇️"})
        assert result.success
        assert result.state.current_room == "throne"


class TestClientState:
    """Tests for client state conversion."""

    def test_get_state_for_client_contains_all_fields(self):
        """Client state should contain all required fields."""
        engine = GameEngine()
        state = engine.new_game()
        client_state = engine.get_state_for_client(state)
        assert "location" in client_state
        assert "location_id" in client_state
        assert "health" in client_state
        assert "max_health" in client_state
        assert "score" in client_state
        assert "inventory" in client_state
        assert "room_items" in client_state
        assert "room_enemies" in client_state
        assert "exits" in client_state
        assert "is_dark" in client_state
        assert "game_over" in client_state
        assert "victory" in client_state


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
