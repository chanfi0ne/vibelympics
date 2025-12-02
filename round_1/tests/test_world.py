"""Tests for the game world definitions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from world import (
    ENEMY_SCORES,
    ENEMY_TEMPLATES,
    ITEMS,
    create_world,
    get_initial_room_enemies,
    get_initial_room_items,
)


class TestWorldCreation:
    """Tests for world creation."""

    def test_world_has_all_rooms(self):
        """World should contain all expected rooms."""
        world = create_world()
        expected_rooms = [
            "house",
            "forest",
            "river",
            "temple",
            "cave",
            "dungeon",
            "throne",
        ]
        for room_id in expected_rooms:
            assert room_id in world

    def test_house_is_starting_room(self):
        """House should have sword and exit to forest."""
        world = create_world()
        house = world["house"]
        assert house.emoji == "🏠"
        assert "🗡️" in house.items
        assert "➡️" in house.exits

    def test_cave_is_dark(self):
        """Cave should be marked as dark."""
        world = create_world()
        assert world["cave"].is_dark

    def test_throne_room_has_dragon_and_crown(self):
        """Throne room should have dragon and crown."""
        world = create_world()
        throne = world["throne"]
        assert "👑" in throne.items
        enemy_emojis = [e.emoji for e in throne.enemies]
        assert "🐉" in enemy_emojis

    def test_dungeon_has_locked_exit(self):
        """Dungeon should have locked exit to throne."""
        world = create_world()
        dungeon = world["dungeon"]
        assert "⬇️" in dungeon.locked_exits
        assert dungeon.locked_exits["⬇️"] == "throne"


class TestItemDefinitions:
    """Tests for item definitions."""

    def test_all_items_have_names(self):
        """All items should have names."""
        for item, data in ITEMS.items():
            assert "name" in data

    def test_sword_has_damage(self):
        """Sword should have damage value."""
        assert ITEMS["🗡️"]["damage"] == 2

    def test_potion_heals(self):
        """Potion should have heal value."""
        assert ITEMS["🧪"]["heal"] == 2

    def test_crown_is_win_condition(self):
        """Crown should be marked as win item."""
        assert ITEMS["👑"]["win"]


class TestEnemyTemplates:
    """Tests for enemy templates."""

    def test_bat_is_weak(self):
        """Bat should have 1 HP."""
        assert ENEMY_TEMPLATES["bat"].health == 1

    def test_dragon_is_strong(self):
        """Dragon should have 5 HP."""
        assert ENEMY_TEMPLATES["dragon"].health == 5

    def test_grue_is_deadly(self):
        """Grue should be marked as grue and very powerful."""
        grue = ENEMY_TEMPLATES["grue"]
        assert grue.is_grue
        assert grue.health == 999


class TestEnemyScores:
    """Tests for enemy score values."""

    def test_defeating_bat_gives_score(self):
        """Defeating bat should give 10 points."""
        assert ENEMY_SCORES["🦇"] == 10

    def test_defeating_dragon_gives_highest_score(self):
        """Defeating dragon should give highest score."""
        assert ENEMY_SCORES["🐉"] >= ENEMY_SCORES["🦇"]
        assert ENEMY_SCORES["🐉"] >= ENEMY_SCORES["👹"]


class TestInitialState:
    """Tests for initial state functions."""

    def test_get_initial_room_items_returns_copies(self):
        """Initial items should be independent copies."""
        world = create_world()
        items1 = get_initial_room_items(world)
        items2 = get_initial_room_items(world)
        items1["house"].remove("🗡️")
        assert "🗡️" in items2["house"]

    def test_get_initial_room_enemies_returns_clones(self):
        """Initial enemies should be clones, not references."""
        world = create_world()
        enemies1 = get_initial_room_enemies(world)
        enemies2 = get_initial_room_enemies(world)
        # Damage enemy in first set
        enemies1["forest"][0].take_damage(1)
        # Second set should be unaffected
        assert enemies2["forest"][0].health == enemies2["forest"][0].max_health
