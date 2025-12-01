/**
 * Emoji Zork Game Controller
 */
class EmojiZorkGame {
    constructor() {
        this.sessionId = null;
        this.state = null;
        this.selectedItem = null;
        this.isAnimating = false;

        // DOM element cache
        this.elements = {
            location: document.getElementById("location"),
            health: document.getElementById("health"),
            score: document.getElementById("score"),
            roomEmoji: document.getElementById("room-emoji"),
            roomView: document.getElementById("room-view"),
            visibleItems: document.getElementById("visible-items"),
            enemyDisplay: document.getElementById("enemy-display"),
            inventorySlots: document.getElementById("inventory-slots"),
            deathOverlay: document.getElementById("death-overlay"),
            grueOverlay: document.getElementById("grue-overlay"),
            victoryOverlay: document.getElementById("victory-overlay"),
            errorFlash: document.getElementById("error-flash"),
            retryBtn: document.getElementById("retry-btn"),
            playAgainBtn: document.getElementById("play-again-btn"),
        };

        this.init();
    }

    async init() {
        await this.newGame();
        this.bindEvents();
        this.render();
    }

    async newGame() {
        try {
            const response = await fetch("/api/new-game", { method: "POST" });
            const data = await response.json();
            this.sessionId = data.session_id;
            this.state = data.state;
            this.selectedItem = null;
            this.hideAllOverlays();
        } catch (error) {
            console.error("Failed to start new game:", error);
        }
    }

    bindEvents() {
        // Navigation buttons
        document.querySelectorAll(".nav-btn").forEach((btn) => {
            btn.addEventListener("click", () => {
                if (!btn.disabled) {
                    this.handleMove(btn.dataset.dir);
                }
            });
        });

        // Action buttons
        document.querySelectorAll(".action-btn").forEach((btn) => {
            btn.addEventListener("click", () => {
                if (!btn.disabled) {
                    this.handleAction(btn.dataset.action);
                }
            });
        });

        // Retry buttons
        this.elements.retryBtn.addEventListener("click", () => this.restart());
        this.elements.playAgainBtn.addEventListener("click", () => this.restart());

        // Item selection in room
        this.elements.visibleItems.addEventListener("click", (e) => {
            if (e.target.classList.contains("item")) {
                this.selectItem(e.target.dataset.item, "room");
            }
        });

        // Item selection in inventory
        this.elements.inventorySlots.addEventListener("click", (e) => {
            if (e.target.classList.contains("inv-item")) {
                this.selectItem(e.target.dataset.item, "inventory");
            }
        });
    }

    selectItem(item, source) {
        // Toggle selection
        if (this.selectedItem === item) {
            this.selectedItem = null;
        } else {
            this.selectedItem = item;
        }
        this.render();
    }

    async handleMove(direction) {
        if (this.isAnimating) return;
        await this.performAction("move", { direction });
    }

    async handleAction(action) {
        if (this.isAnimating) return;

        switch (action) {
            case "look":
                await this.performAction("look", {});
                break;
            case "take":
                if (this.selectedItem) {
                    await this.performAction("take", { item: this.selectedItem });
                    this.selectedItem = null;
                }
                break;
            case "attack":
                await this.performAction("attack", {});
                break;
            case "use-potion":
                await this.performAction("use", { item: "🧪" });
                break;
            case "use-key":
                await this.performAction("use", { item: "🔑" });
                break;
        }
    }

    async performAction(action, params) {
        try {
            const response = await fetch("/api/action", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    action,
                    ...params,
                }),
            });
            const data = await response.json();

            if (data.event) {
                await this.handleEvent(data.event);
            }

            if (data.error) {
                this.showError(data.error);
            }

            this.state = data.state;
            this.render();
        } catch (error) {
            console.error("Action failed:", error);
        }
    }

    async handleEvent(event) {
        this.isAnimating = true;

        switch (event.type) {
            case "item_taken":
                await this.animateItemPickup(event.data.item);
                break;
            case "enemy_defeated":
                await this.animateEnemyDefeat();
                break;
            case "combat_round":
                await this.animateCombat();
                break;
            case "player_died":
                await this.animateDeath();
                break;
            case "grue_attack":
                await this.animateGrueAttack();
                break;
            case "door_unlocked":
                await this.animateDoorUnlock();
                break;
            case "healed":
                await this.animateHeal();
                break;
        }

        this.isAnimating = false;
    }

    async animateItemPickup(item) {
        const itemEl = this.elements.visibleItems.querySelector(
            `[data-item="${item}"]`
        );
        if (itemEl) {
            itemEl.classList.add("item-pickup");
            await this.delay(400);
        }
    }

    async animateEnemyDefeat() {
        const enemyEl = this.elements.enemyDisplay.querySelector(".enemy-emoji");
        if (enemyEl) {
            enemyEl.textContent = "💥";
            enemyEl.classList.add("explode");
            await this.delay(400);
        }
    }

    async animateCombat() {
        this.elements.roomEmoji.classList.add("shake");
        this.elements.health.classList.add("damage-flash");
        await this.delay(300);
        this.elements.roomEmoji.classList.remove("shake");
        this.elements.health.classList.remove("damage-flash");
    }

    async animateDeath() {
        await this.delay(500);
        this.elements.deathOverlay.classList.remove("hidden");
    }

    async animateGrueAttack() {
        const overlay = this.elements.grueOverlay;
        overlay.classList.remove("hidden");

        const stages = ["grue-dark", "grue-eyes", "grue-fear", "grue-death"];
        for (let i = 0; i < stages.length; i++) {
            // Hide all stages
            stages.forEach((s) =>
                document.getElementById(s).classList.add("hidden")
            );
            // Show current stage
            document.getElementById(stages[i]).classList.remove("hidden");
            await this.delay(800);
        }

        await this.delay(500);
        overlay.classList.add("hidden");
        this.elements.deathOverlay.classList.remove("hidden");
    }

    async animateDoorUnlock() {
        this.elements.roomEmoji.textContent = "✨";
        await this.delay(500);
    }

    async animateHeal() {
        this.elements.health.style.filter = "brightness(2) hue-rotate(60deg)";
        await this.delay(300);
        this.elements.health.style.filter = "";
    }

    showError(emoji) {
        this.elements.errorFlash.textContent = emoji;
        this.elements.errorFlash.classList.remove("hidden");
        setTimeout(() => {
            this.elements.errorFlash.classList.add("hidden");
        }, 300);
    }

    hideAllOverlays() {
        this.elements.deathOverlay.classList.add("hidden");
        this.elements.grueOverlay.classList.add("hidden");
        this.elements.victoryOverlay.classList.add("hidden");
    }

    async restart() {
        await this.newGame();
        this.render();
    }

    render() {
        if (!this.state) return;

        // Status bar
        this.elements.location.textContent = "📍" + this.state.location;
        this.elements.health.textContent = "❤️".repeat(this.state.health) + 
            "🖤".repeat(this.state.max_health - this.state.health);
        this.elements.score.textContent = "💰" + this.state.score;

        // Room view
        this.elements.roomEmoji.textContent = this.state.location;
        this.elements.roomView.classList.toggle("dark", this.state.is_dark);

        // Visible items
        this.elements.visibleItems.innerHTML = this.state.room_items
            .map(
                (item) =>
                    `<span class="item ${
                        this.selectedItem === item ? "selected" : ""
                    }" data-item="${item}">${item}</span>`
            )
            .join("");

        // Enemies
        if (this.state.room_enemies.length > 0) {
            const enemy = this.state.room_enemies[0];
            this.elements.enemyDisplay.innerHTML = `
                <span class="enemy-emoji">${enemy.emoji}</span>
                <span class="enemy-health">${"❤️".repeat(enemy.health)}</span>
            `;
        } else {
            this.elements.enemyDisplay.innerHTML = "";
        }

        // Inventory
        this.elements.inventorySlots.innerHTML = this.state.inventory
            .map(
                (item) =>
                    `<span class="inv-item ${
                        this.selectedItem === item ? "selected" : ""
                    }" data-item="${item}">${item}</span>`
            )
            .join("");

        // Navigation buttons
        document.querySelectorAll(".nav-btn").forEach((btn) => {
            const dir = btn.dataset.dir;
            btn.disabled = !this.state.exits.includes(dir);
        });

        // Action buttons
        const takeBtn = document.querySelector('[data-action="take"]');
        const attackBtn = document.querySelector('[data-action="attack"]');
        const potionBtn = document.querySelector('[data-action="use-potion"]');
        const keyBtn = document.querySelector('[data-action="use-key"]');

        takeBtn.disabled =
            !this.selectedItem || !this.state.room_items.includes(this.selectedItem);
        attackBtn.disabled =
            !this.state.inventory.includes("🗡️") ||
            this.state.room_enemies.length === 0;
        potionBtn.disabled = !this.state.inventory.includes("🧪");
        keyBtn.disabled = !this.state.inventory.includes("🔑");

        // Victory check
        if (this.state.victory) {
            this.elements.victoryOverlay.classList.remove("hidden");
        }
    }

    delay(ms) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }
}

// Initialize game when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    window.game = new EmojiZorkGame();
});
