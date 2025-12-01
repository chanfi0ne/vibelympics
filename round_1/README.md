# 🕳️ Emoji Zork

> *The Great Underground Emoji Empire*

A dungeon-crawling adventure game inspired by Zork, with a 100% emoji-based UI. No text in the interface - just emojis!

## 🎮 Quick Start

```bash
# Build the container
docker build -t emoji-zork .

# Run the game
docker run -p 8080:8080 emoji-zork

# Open in browser
open http://localhost:8080
```

## 🗺️ How to Play

```
📍 = Your location     ❤️ = Health     💰 = Score     🎒 = Inventory
```

### Navigation
```
    ⬆️          
  ⬅️ 👁️ ➡️    ← Move around, 👁️ = look
    ⬇️          
```

### Actions
```
🖐️ = Pick up item (select item first, then tap)
⚔️ = Attack enemy (need 🗡️)
🧪 = Use potion (heals ❤️❤️)
🔑 = Unlock door
```

## 🏰 Game World

```
🏠 → 🌲 → 💧
      ↓
     ⛪
      ↓
     🕳️ ← ⚠️ DARK! Need 🔦
      ↓
     🏰
      ↓ 🔒
     👑 ← 🐉 guards the crown!
```

## ⚔️ Items

| 🗡️ | ⚔️ Sword - Attack enemies |
|---|---|
| 🔦 | 💡 Flashlight - Survive darkness |
| 🔑 | 🚪 Key - Unlock throne room |
| 🧪 | ❤️ Potion - Heal yourself |
| 🛡️ | 🛡️ Shield - Reduce damage |
| 💎 | 💰 Diamond - Treasure (+50) |
| 👑 | 🏆 Crown - WIN! |

## 👹 Enemies

| 🦇 | Bat - 1 HP |
|---|---|
| 👹 | Troll - 3 HP |
| 🐉 | Dragon - 5 HP |
| 🐺 | Grue - ∞ HP (instant kill in 🌑) |

## 🎯 Goal

Get the 👑 from the 🐉 in the 👑 throne room!

## 💀 Tips

- Get 🗡️ first (🏠)
- Get 🔦 before 🕳️ or 🐺 will eat you!
- Get 🔑 from ⛪ (defeat 👹 first)
- Use 🧪 when low on ❤️

## 🔧 Development

```bash
# Create venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run locally
python src/app.py

# Run tests
pytest tests/ -v
```

## 🏗️ Architecture

```
src/
├── app.py          # Flask API
├── game_engine.py  # Game logic
├── models.py       # Data classes
├── world.py        # World definition
└── static/         # Frontend
    ├── index.html
    ├── styles.css
    └── game.js
```

## 📜 License

MIT

---

*🌑 It is dark. You are likely to be eaten by a grue. 🐺*
