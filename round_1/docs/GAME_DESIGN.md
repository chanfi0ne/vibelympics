# Game Design Document
# 🕳️ Emoji Zork: The Great Underground Emoji Empire

## 1. Game Overview

### 1.1 Concept

A dungeon-crawling adventure game in the spirit of Zork, where the entire experience is conveyed through emojis. Players explore a dangerous underground world, collect treasures, fight monsters, solve puzzles, and ultimately claim the Crown of the Emoji Empire.

### 1.2 Core Loop

```
EXPLORE → DISCOVER → COLLECT → FIGHT → SOLVE → PROGRESS → REPEAT
   🚶        👁️         🖐️        ⚔️       🔑       🚪        🔄
```

### 1.3 Win/Lose Conditions

| Condition | Result | Display |
|-----------|--------|---------|
| Collect 👑 Crown | **VICTORY** | 🏆🎉👑 |
| Health reaches 0 | **DEFEAT** | 💀 (with 🔄 retry) |
| Grue attack (dark room, no light) | **INSTANT DEATH** | 🌑👀😱💀 |

## 2. World Map

### 2.1 Map Layout

```
                    ┌─────────┐
                    │   ⛪    │
                    │ Temple  │
                    └────┬────┘
                         │
┌─────────┐         ┌────┴────┐         ┌─────────┐
│   🏠    │─────────│   🌲    │─────────│   💧    │
│  House  │         │ Forest  │         │  River  │
└─────────┘         └────┬────┘         └─────────┘
                         │
                    ┌────┴────┐
                    │   🕳️    │
                    │  Cave   │ 🌑 DARK!
                    └────┬────┘
                         │
                    ┌────┴────┐
                    │   🏰    │
                    │ Dungeon │
                    └────┬────┘
                         │🔒 LOCKED
                    ┌────┴────┐
                    │   👑    │
                    │ Throne  │
                    └─────────┘
```

### 2.2 Room Details

#### 🏠 House (Starting Room)
```
Location Emoji: 🏠
Description: The adventure begins here. A cozy house at the edge of the known world.
Items: 🗡️ (Sword)
Enemies: None
Exits: ➡️ Forest
Special: Safe zone, tutorial area
```

#### 🌲 Forest
```
Location Emoji: 🌲
Description: A dense forest filled with strange sounds.
Items: 🔦 (Flashlight) - CRITICAL for cave!
Enemies: 🦇 (Bat) - ❤️ health, ½❤️ damage
Exits: ⬅️ House, ➡️ River, ⬇️ Cave, ⬆️ Temple
Special: First combat encounter
```

#### 💧 River
```
Location Emoji: 💧
Description: A rushing river with something glinting beneath the surface.
Items: 💎 (Diamond) - 50 points
Enemies: None
Exits: ⬅️ Forest
Special: Treasure location
```

#### ⛪ Temple
```
Location Emoji: ⛪
Description: Ancient temple with mysterious inscriptions (all emoji, of course).
Items: 🧪 (Potion), 🔑 (Key) - CRITICAL for throne room!
Enemies: 👹 (Troll) - ❤️❤️❤️ health, ❤️ damage
Exits: ⬇️ Forest
Special: Key is hidden, appears after defeating Troll
```

#### 🕳️ Cave (DARK)
```
Location Emoji: 🕳️ (when lit) / 🌑 (when dark)
Description: A pitch-black cave. You are likely to be eaten by a grue.
Items: 🛡️ (Shield) - reduces damage taken
Enemies: 🐺 (Grue) - ONLY ATTACKS IN DARKNESS, instant kill
Exits: ⬆️ Forest, ⬇️ Dungeon
Special: 
  - If player has 🔦: Normal room, grue dormant
  - If player lacks 🔦: GRUE ATTACK → instant death
```

#### 🏰 Dungeon
```
Location Emoji: 🏰
Description: The main dungeon hall. Danger lurks in the shadows.
Items: 🗺️ (Map) - reveals all room connections
Enemies: 👹 (Troll) - ❤️❤️❤️ health, ❤️ damage
Exits: ⬆️ Cave, ⬇️ Throne Room (LOCKED - needs 🔑)
Special: Must defeat Troll to proceed safely
```

#### 👑 Throne Room (Final Area)
```
Location Emoji: 👑
Description: The heart of the underground empire.
Items: 👑 (Crown) - WIN CONDITION
Enemies: 🐉 (Dragon) - ❤️❤️❤️❤️❤️ health, ❤️❤️ damage
Exits: ⬆️ Dungeon
Special: 
  - Requires 🔑 to enter
  - Must defeat Dragon to claim Crown
  - Taking Crown = VICTORY
```

## 3. Items

### 3.1 Weapons

| Emoji | Name | Effect | Location |
|-------|------|--------|----------|
| 🗡️ | Sword | Enables attack, 2 damage per hit | House |
| 🛡️ | Shield | Reduces damage by 1 | Cave |

### 3.2 Tools

| Emoji | Name | Effect | Location |
|-------|------|--------|----------|
| 🔦 | Flashlight | Prevents grue attack in dark rooms | Forest |
| 🔑 | Key | Opens locked Throne Room | Temple (after Troll) |
| 🗺️ | Map | Shows all room connections | Dungeon |

### 3.3 Consumables

| Emoji | Name | Effect | Location |
|-------|------|--------|----------|
| 🧪 | Potion | Restores 2 ❤️ (single use) | Temple |

### 3.4 Treasures

| Emoji | Name | Points | Location |
|-------|------|--------|----------|
| 💎 | Diamond | +50 | River |
| 👑 | Crown | WIN + 100 | Throne Room |

## 4. Enemies

### 4.1 Enemy Stats

| Emoji | Name | Health | Damage | Behavior |
|-------|------|--------|--------|----------|
| 🦇 | Bat | ❤️ | ½❤️ | Attacks every turn |
| 👹 | Troll | ❤️❤️❤️ | ❤️ | Guards key items |
| 🐉 | Dragon | ❤️❤️❤️❤️❤️ | ❤️❤️ | Final boss |
| 🐺 | Grue | ∞ | 💀 | Instant kill in dark |

### 4.2 Combat System

```
Combat Flow:
1. Player clicks ⚔️
2. Player attacks first (if has weapon)
3. Player damage = 2 (with sword) or 3 (sword + shield bonus doesn't apply to attack)
4. Enemy health reduced
5. If enemy survives, enemy attacks back
6. Player damage = enemy.damage - (1 if has shield else 0)
7. Repeat until one is defeated
```

### 4.3 Combat Formulas

```python
# Damage calculation
player_damage = 2  # Base sword damage

enemy_damage_to_player = enemy.damage - (1 if "🛡️" in inventory else 0)
enemy_damage_to_player = max(1, enemy_damage_to_player)  # Minimum 1 damage
```

## 5. Player Stats

### 5.1 Initial State

```
Health: ❤️❤️❤️ (3/3)
Inventory: [] (empty)
Score: 💰 0
Location: 🏠 House
```

### 5.2 Health System

- Max health: ❤️❤️❤️❤️❤️ (5)
- Starting health: ❤️❤️❤️ (3)
- Potion heals: ❤️❤️ (+2)
- Death at: 0 ❤️

### 5.3 Scoring

| Action | Points |
|--------|--------|
| Pick up 💎 | +50 |
| Defeat 🦇 | +10 |
| Defeat 👹 | +25 |
| Defeat 🐉 | +50 |
| Pick up 👑 | +100 (WIN) |

## 6. Puzzles

### 6.1 Light Puzzle (Cave)

```
Problem: Cave is dark (🌑), grue will attack
Solution: Get 🔦 from Forest before entering

Visual Flow:
Enter cave without 🔦:
  🌑 → 👀 (eyes appear) → 😱 (fear) → 💀 (death)

Enter cave with 🔦:
  🕳️ (normal cave) → safe to explore
```

### 6.2 Door Puzzle (Throne Room)

```
Problem: Throne Room is locked (🔒)
Solution: Get 🔑 from Temple, use on door

Visual Flow:
Try to enter without 🔑:
  🚪🔒 → ❌ (shake animation)

Use 🔑 on door:
  🔑 → 🚪 → ✨ (unlock animation) → ⬇️ now available
```

### 6.3 Boss Order

Recommended path to victory:
```
1. 🏠 Get 🗡️ (sword)
2. 🌲 Get 🔦, defeat 🦇
3. 💧 Get 💎 (treasure)
4. ⛪ Defeat 👹, get 🧪 and 🔑
5. 🕳️ Enter safely (have 🔦), get 🛡️
6. 🏰 Defeat 👹, get 🗺️
7. 👑 Use 🔑, defeat 🐉, claim 👑
```

## 7. UI Elements

### 7.1 Status Bar

```
┌─────────────────────────────────────┐
│ 📍🏠        ❤️❤️❤️        💰 42    │
│ [location]  [health]      [score]   │
└─────────────────────────────────────┘
```

### 7.2 Room View

```
┌─────────────────────────────────────┐
│                                     │
│              🏠                     │ ← Large room emoji
│                                     │
│     👁️: 🗡️                         │ ← Visible items
│                                     │
│     👹 ❤️❤️❤️                      │ ← Enemy + its health
│                                     │
└─────────────────────────────────────┘
```

### 7.3 Inventory

```
┌─────────────────────────────────────┐
│ 🎒: 🗡️  🔦  🔑  🛡️               │
│     [tap item to select]            │
└─────────────────────────────────────┘
```

### 7.4 Navigation & Actions

```
        ⬆️
     ⬅️ 👁️ ➡️    ← Directional + Look
        ⬇️

   🖐️  ⚔️  🧪  🔑  ← Take, Attack, Use Potion, Use Key
```

## 8. Visual Feedback

### 8.1 Animations

| Event | Animation |
|-------|-----------|
| Item taken | Item emoji flies to inventory bar |
| Damage taken | Hearts pulse red, screen shakes |
| Enemy hit | Enemy shakes, health heart breaks |
| Enemy defeated | Enemy → 💥 → fades out |
| Door locked | Door emoji shakes with ❌ |
| Door unlocked | Door emoji sparkles ✨ |
| Level up/healing | Hearts glow green |
| Invalid action | Button flashes ❌ |

### 8.2 Screen Transitions

| Transition | Animation |
|------------|-----------|
| Room change | Slide in direction of movement |
| Death | Fade to black → 💀 → 🔄 button |
| Victory | Confetti of 🎉 → 🏆 → 👑 |
| Grue attack | 🌑 → 👀 → 😱 → 💀 (sequential) |

## 9. Audio (Optional Enhancement)

If time permits, simple audio cues:

| Event | Sound |
|-------|-------|
| Button tap | Soft click |
| Item pickup | Positive chime |
| Damage taken | Ouch/hit sound |
| Enemy defeated | Victory sting |
| Door unlock | Key turning |
| Death | Sad trombone |
| Victory | Fanfare |

## 10. Easter Eggs & Zork References

### 10.1 Classic Zork Callbacks

| Reference | Implementation |
|-----------|----------------|
| "It is dark. You are likely to be eaten by a grue." | 🌑🐺 in dark rooms |
| Mailbox | 📬 decorative in House |
| Leaflet | 📜 if clicked, shows game hints as emojis |
| Maze | If player backtracks too much, show 🌀 confusion |
| Score display | "Your score is [X] of 335" → 💰[X]/💰335 |

### 10.2 Hidden Details

- House lamp flickers occasionally (CSS animation)
- Forest has ambient 🍃 leaf particles
- Cave has dripping 💧 animation
- Dragon occasionally breathes 🔥 puffs

## 11. Complete Game State

```python
@dataclass
class CompleteGameState:
    # Player
    current_room: str = "house"
    health: int = 3
    max_health: int = 5
    inventory: List[str] = field(default_factory=list)
    score: int = 0
    
    # World state
    room_items: Dict[str, List[str]]  # Items remaining in each room
    room_enemies: Dict[str, List[Enemy]]  # Enemies remaining
    unlocked_doors: Set[str] = field(default_factory=set)
    
    # Flags
    has_light: bool = False  # Computed from inventory
    game_over: bool = False
    victory: bool = False
```

## 12. Difficulty Tuning

### 12.1 Easy Mode (Default)

- Player starts with 3 ❤️
- Potion heals 2 ❤️
- Shield blocks 1 damage
- Balanced for completion in ~10 minutes

### 12.2 Balance Considerations

| Scenario | Expected Outcome |
|----------|------------------|
| No weapon, enter combat | ❌ Can't attack, must flee |
| No light, enter cave | 💀 Grue death |
| Skip Temple, go to Throne | 🔒 Can't enter |
| Fight Dragon with low health | Risky but possible |
| Optimal path | Win with ~2 ❤️ remaining |

---

## 13. Implementation Priority

### Phase 1: Core (MVP)
1. Room navigation
2. Item pickup
3. Basic combat
4. Win condition (get crown)

### Phase 2: Polish
5. Grue/light mechanics
6. Door/key puzzle
7. Score system
8. Animations

### Phase 3: Enhancement
9. Audio
10. Easter eggs
11. Extra rooms/items

---

**Document Status:** Complete  
**Ready for:** Implementation Phase
