# Product Requirements Document (PRD)
# 🕳️ Emoji Zork: The Great Underground Emoji Empire

## 1. Executive Summary

**Product Name:** Emoji Zork  
**Version:** 1.0  
**Date:** 2024  
**Type:** Web-based dungeon crawler adventure game  

Emoji Zork is a fully functional dungeon crawler inspired by the classic Zork text adventure, reimagined with a 100% emoji-based user interface. No text is used in any interactive elements - all buttons, navigation, labels, status indicators, and game content are represented purely through emojis.

## 2. Problem Statement

Traditional text-based adventures require language comprehension and reading. Emoji Zork proves that a complete, engaging gaming experience can be delivered through universal visual symbols, making it:
- Language-agnostic
- Instantly intuitive
- Visually distinctive
- Surprisingly deep

## 3. Target Users

- Judges evaluating creativity, security, and code quality
- Gamers who appreciate retro adventure games
- Anyone who wants to experience a "text adventure" without text

## 4. Core Requirements

### 4.1 Absolute Requirements (Must Have)

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| R1 | **All UI elements must be emojis only** | Zero text in buttons, labels, navigation, status displays |
| R2 | **Fully functional game** | Player can navigate, collect items, fight monsters, solve puzzles, win/lose |
| R3 | **Containerized with Chainguard** | Dockerfile uses Chainguard base image, builds and runs successfully |
| R4 | **Web accessible** | Runs on a port, viewable in browser locally |

### 4.2 Functional Requirements

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| F1 | Room Navigation | Move between connected rooms via directional emojis | P0 |
| F2 | Room Display | Show current location, visible items, exits, enemies | P0 |
| F3 | Inventory System | Collect, view, and use items (all emoji) | P0 |
| F4 | Combat System | Fight monsters with emoji weapons, health tracking | P0 |
| F5 | Puzzle Mechanics | Use items to unlock doors/passages | P0 |
| F6 | Win/Lose States | Victory on treasure collection, death on health=0 | P0 |
| F7 | Grue Mechanic | Classic Zork: darkness = grue danger | P1 |
| F8 | Score System | Track points for discoveries and victories | P1 |
| F9 | Sound Effects | Emoji-appropriate audio feedback (optional) | P2 |

### 4.3 Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NF1 | Page Load Time | < 2 seconds |
| NF2 | Container Size | < 100MB |
| NF3 | Memory Usage | < 50MB runtime |
| NF4 | Browser Support | Modern browsers (Chrome, Firefox, Safari, Edge) |
| NF5 | Responsive | Works on desktop (mobile stretch goal) |

## 5. User Stories

### 5.1 Core Gameplay

```
As a player, I want to see my current location as an emoji
  So that I instantly understand where I am

As a player, I want to tap directional arrows to move
  So that I can explore the dungeon

As a player, I want to see items in the room as emojis
  So that I know what I can interact with

As a player, I want to tap an item + 🖐️ to pick it up
  So that I can collect useful items

As a player, I want to see my inventory as emoji icons
  So that I know what I'm carrying

As a player, I want to tap ⚔️ when an enemy is present
  So that I can fight monsters

As a player, I want to see my health as heart emojis
  So that I know my survival status

As a player, I want to use 🔑 on 🚪 to unlock passages
  So that I can solve puzzles and progress

As a player, I want a 🏆 screen when I win
  So that I feel accomplished
```

### 5.2 Zork Homage

```
As a player, I want to encounter a grue in darkness
  So that I experience classic Zork danger

As a player, I want to find the ultimate treasure
  So that I can complete the quest

As a player, I want to see 💀 when I die
  So that failure is clear (and I can retry)
```

## 6. Game World Design

### 6.1 Locations (Rooms)

| Emoji | Location | Description | Connects To |
|-------|----------|-------------|-------------|
| 🏠 | House | Starting location, safe | Forest |
| 🌲 | Forest | Outdoor area, basic enemy | House, Cave, River |
| 🕳️ | Cave | Dark (grue!), need light | Forest, Dungeon |
| 💧 | River | Water obstacle, need boat | Forest, Temple |
| 🏰 | Dungeon | Main dungeon, monsters | Cave, Throne Room |
| ⛪ | Temple | Ancient temple, puzzles | River |
| 👑 | Throne Room | Final area, boss + treasure | Dungeon |

### 6.2 Items

| Emoji | Item | Use |
|-------|------|-----|
| 🗡️ | Sword | Combat weapon (+2 damage) |
| 🔦 | Flashlight | Prevents grue attacks |
| 🔑 | Key | Opens locked doors |
| 🧪 | Potion | Restores 2 hearts |
| 💎 | Diamond | Treasure (score +50) |
| 🛡️ | Shield | Reduces damage taken |
| 🗺️ | Map | Reveals room connections |
| 👑 | Crown | Ultimate treasure (win condition) |

### 6.3 Enemies

| Emoji | Enemy | Health | Damage | Location |
|-------|-------|--------|--------|----------|
| 🐺 | Grue | ∞ (instakill) | 💀 | Dark rooms |
| 🦇 | Bat | ❤️ | ½❤️ | Cave |
| 👹 | Troll | ❤️❤️❤️ | ❤️ | Dungeon |
| 🐉 | Dragon | ❤️❤️❤️❤️❤️ | ❤️❤️ | Throne Room |

## 7. User Interface Specification

### 7.1 Main Game Screen Layout

```
┌─────────────────────────────────────────┐
│                TOP BAR                   │
│  📍[location]     ❤️❤️❤️     💰[score]  │
├─────────────────────────────────────────┤
│                                         │
│              ROOM VIEW                   │
│                                         │
│         [location emoji large]          │
│                                         │
│    👁️: [visible items/enemies]          │
│                                         │
├─────────────────────────────────────────┤
│              INVENTORY                   │
│  🎒: [item] [item] [item] [item]        │
├─────────────────────────────────────────┤
│            ACTION BUTTONS                │
│                  ⬆️                      │
│              ⬅️  👁️  ➡️                  │
│                  ⬇️                      │
│                                         │
│        🖐️   ⚔️   🧪   🔑              │
└─────────────────────────────────────────┘
```

### 7.2 Emoji-Only Feedback

| Event | Visual Feedback |
|-------|-----------------|
| Item picked up | Item animates to inventory |
| Damage taken | ❤️ → 💔 animation, screen flash |
| Enemy defeated | Enemy → 💥 → disappears |
| Locked door | 🚪❌ shake animation |
| Door unlocked | 🔑→🚪 → 🚪✨ |
| Grue attack | 🌑 → 👀 → 😱 → 💀 |
| Victory | 🎉👑🏆 celebration |
| Death | 💀 with 🔄 retry button |

### 7.3 Action Buttons

| Button | Action | When Available |
|--------|--------|----------------|
| ⬆️⬇️⬅️➡️ | Move in direction | Exit exists |
| 👁️ | Look around (refresh view) | Always |
| 🖐️ | Pick up selected item | Item in room |
| ⚔️ | Attack enemy | Enemy present + weapon |
| 🧪 | Use potion | Potion in inventory |
| 🔑 | Use key on door | Key in inventory + locked door |

## 8. Technical Constraints

### 8.1 Technology Stack

- **Backend:** Python 3.11+ with Flask
- **Frontend:** Vanilla HTML/CSS/JavaScript (no frameworks)
- **Container:** Chainguard Python base image
- **No external databases** - game state in memory/session

### 8.2 Chainguard Container Requirements

```dockerfile
FROM cgr.dev/chainguard/python:latest
# Minimal, secure base image
```

## 9. Success Metrics

### 9.1 Judging Criteria Alignment

| Criteria | Weight | How We Score |
|----------|--------|--------------|
| Security | 30% | Secure container, input validation, no vulnerabilities |
| Functionality | 30% | Complete game loop, all features work |
| Code Quality | 30% | Clean structure, documented, maintainable |
| Vibes | 10% | Creative emoji-only concept, fun to play |

### 9.2 Definition of Done

- [ ] All UI elements are emojis (zero text)
- [ ] Player can complete a full game (win or lose)
- [ ] Container builds with Chainguard base
- [ ] Container runs and game is accessible on port
- [ ] No security vulnerabilities
- [ ] Code is clean, readable, documented
- [ ] README explains how to run

## 10. Out of Scope (v1.0)

- Multiplayer
- Save/load game state
- Mobile-optimized responsive design
- Accessibility features (screen readers)
- Internationalization (emojis are universal!)
- Leaderboards

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Emojis render differently across OS | Medium | Test on multiple browsers, use common emojis |
| Game too confusing without text | High | Intuitive design, visual feedback, consistent patterns |
| Container build issues | Medium | Test Chainguard image early, simple Dockerfile |

---

**Document Status:** Ready for Technical Specification  
**Next Step:** Architecture & Technical Spec
