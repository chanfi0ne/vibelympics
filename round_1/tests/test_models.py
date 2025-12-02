"""Tests for the game models."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import ActionResult, Enemy, GameState, Room


class TestEnemy:
    """Tests for the Enemy model."""

    def test_enemy_is_alive_when_health_positive(self):
        """Enemy with positive health should be alive."""
        enemy = Enemy(emoji="🦇", health=1, max_health=1, damage=1)
        assert enemy.is_alive

    def test_enemy_is_dead_when_health_zero(self):
        """Enemy with zero health should be dead."""
        enemy = Enemy(emoji="🦇", health=0, max_health=1, damage=1)
        assert not enemy.is_alive

    def test_take_damage_reduces_health(self):
        """Taking damage should reduce health."""
        enemy = Enemy(emoji="👹", health=3, max_health=3, damage=1)
        enemy.take_damage(2)
        assert enemy.health == 1

    def test_take_damage_cannot_go_below_zero(self):
        """Health should not go below zero."""
        enemy = Enemy(emoji="🦇", health=1, max_health=1, damage=1)
        enemy.take_damage(10)
        assert enemy.health == 0

    def test_clone_creates_independent_copy(self):
        """Clone should create an independent copy."""
        original = Enemy(emoji="👹", health=3, max_health=3, damage=1)
        clone = original.clone()
        clone.take_damage(2)
        assert original.health == 3
        assert clone.health == 1

    def test_clone_preserves_grue_flag(self):
        """Clone should preserve is_grue flag."""
        grue = Enemy(emoji="🐺", health=999, max_health=999, damage=999, is_grue=True)
        clone = grue.clone()
        assert clone.is_grue


class TestRoom:
    """Tests for the Room model."""

    def test_has_exit_returns_true_for_valid_exit(self):
        """has_exit should return True for valid exit."""
        room = Room(id="test", emoji="🏠", exits={"➡️": "forest"})
        assert room.has_exit("➡️")

    def test_has_exit_returns_false_for_invalid_exit(self):
        """has_exit should return False for invalid exit."""
        room = Room(id="test", emoji="🏠", exits={"➡️": "forest"})
        assert not room.has_exit("⬆️")

    def test_has_exit_includes_locked_exits(self):
        """has_exit should include locked exits."""
        room = Room(id="test", emoji="🏰", locked_exits={"⬇️": "throne"})
        assert room.has_exit("⬇️")

    def test_get_available_exits_without_unlocks(self):
        """get_available_exits should return only unlocked exits."""
        room = Room(
            id="test",
            emoji="🏰",
            exits={"⬆️": "cave"},
            locked_exits={"⬇️": "throne"},
        )
        exits = room.get_available_exits(set())
        assert "⬆️" in exits
        assert "⬇️" not in exits

    def test_get_available_exits_with_unlocks(self):
        """get_available_exits should include unlocked doors."""
        room = Room(
            id="test",
            emoji="🏰",
            exits={"⬆️": "cave"},
            locked_exits={"⬇️": "throne"},
        )
        exits = room.get_available_exits({"throne"})
        assert "⬆️" in exits
        assert "⬇️" in exits


class TestGameState:
    """Tests for the GameState model."""

    def test_has_light_with_flashlight(self):
        """has_light should return True with flashlight."""
        state = GameState(inventory=["🔦"])
        assert state.has_light

    def test_has_light_without_flashlight(self):
        """has_light should return False without flashlight."""
        state = GameState(inventory=[])
        assert not state.has_light

    def test_has_weapon_with_sword(self):
        """has_weapon should return True with sword."""
        state = GameState(inventory=["🗡️"])
        assert state.has_weapon

    def test_has_weapon_without_sword(self):
        """has_weapon should return False without sword."""
        state = GameState(inventory=[])
        assert not state.has_weapon

    def test_has_shield_with_shield(self):
        """has_shield should return True with shield."""
        state = GameState(inventory=["🛡️"])
        assert state.has_shield

    def test_has_shield_without_shield(self):
        """has_shield should return False without shield."""
        state = GameState(inventory=[])
        assert not state.has_shield

    def test_take_damage_reduces_health(self):
        """take_damage should reduce health."""
        state = GameState(health=3)
        state.take_damage(1)
        assert state.health == 2

    def test_take_damage_with_shield_reduces_damage(self):
        """take_damage with shield should reduce damage by 1."""
        state = GameState(health=3, inventory=["🛡️"])
        state.take_damage(2)
        assert state.health == 2  # 2 - 1 (shield) = 1 actual damage

    def test_take_damage_minimum_one_with_shield(self):
        """Shield should not reduce damage below 1."""
        state = GameState(health=3, inventory=["🛡️"])
        state.take_damage(1)
        assert state.health == 2  # Still takes 1 damage minimum

    def test_take_damage_triggers_game_over(self):
        """Reducing health to 0 should trigger game over."""
        state = GameState(health=1)
        state.take_damage(1)
        assert state.health == 0
        assert state.game_over

    def test_heal_increases_health(self):
        """heal should increase health."""
        state = GameState(health=1, max_health=5)
        state.heal(2)
        assert state.health == 3

    def test_heal_cannot_exceed_max_health(self):
        """heal should not exceed max_health."""
        state = GameState(health=4, max_health=5)
        state.heal(10)
        assert state.health == 5

    def test_add_score_increases_score(self):
        """add_score should increase score."""
        state = GameState(score=0)
        state.add_score(50)
        assert state.score == 50


class TestActionResult:
    """Tests for the ActionResult model."""

    def test_action_result_defaults(self):
        """ActionResult should have correct defaults."""
        state = GameState()
        result = ActionResult(success=True, state=state)
        assert result.success
        assert result.event_type is None
        assert result.event_data is None
        assert result.error_emoji is None

    def test_action_result_with_event(self):
        """ActionResult should store event data."""
        state = GameState()
        result = ActionResult(
            success=True,
            state=state,
            event_type="item_taken",
            event_data={"item": "🗡️"},
        )
        assert result.event_type == "item_taken"
        assert result.event_data["item"] == "🗡️"
