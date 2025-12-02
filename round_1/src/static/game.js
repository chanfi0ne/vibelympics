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
            confettiContainer: document.getElementById("confetti-container"),
            ambientContainer: document.getElementById("ambient-container"),
            errorFlash: document.getElementById("error-flash"),
            retryBtn: document.getElementById("retry-btn"),
            playAgainBtn: document.getElementById("play-again-btn"),
            helpBtn: document.getElementById("help-btn"),
            helpOverlay: document.getElementById("help-overlay"),
            helpCloseBtn: document.getElementById("help-close-btn"),
        };

        // Confetti emoji options
        this.confettiEmojis = ["🎉", "🎊", "✨", "⭐", "💫", "🌟", "🏆", "👑", "💎", "🥳"];

        // Ambient particle configurations per room
        this.ambientConfig = {
            forest: { emoji: "🍃", count: 6, class: "particle-leaf", duration: [4, 7] },
            river: { emoji: "✨", count: 8, class: "particle-sparkle", duration: [2, 4] },
            cave: { emoji: "💧", count: 5, class: "particle-drop", duration: [2, 4] },
            temple: { emoji: "✨", count: 4, class: "particle-glow", duration: [3, 5] },
            throne: { emoji: "🔥", count: 6, class: "particle-fire", duration: [1, 2] },
            dungeon: { emoji: "💀", count: 3, class: "particle-glow", duration: [4, 6] },
        };

        this.ambientInterval = null;
        this.currentRoomId = null;

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

        // Keyboard controls
        document.addEventListener("keydown", (e) => this.handleKeyboard(e));

        // Help overlay
        this.elements.helpBtn.addEventListener("click", () => this.toggleHelp());
        this.elements.helpCloseBtn.addEventListener("click", () => this.hideHelp());
        this.elements.helpOverlay.addEventListener("click", (e) => {
            if (e.target === this.elements.helpOverlay) this.hideHelp();
        });

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

    /**
     * Handle keyboard input for game controls.
     */
    handleKeyboard(e) {
        // Escape closes help
        if (e.key === "Escape") {
            e.preventDefault();
            this.hideHelp();
            return;
        }

        // ? or / toggles help
        if (e.key === "?" || (e.key === "/" && !e.shiftKey)) {
            e.preventDefault();
            this.toggleHelp();
            return;
        }

        // Don't process game keys if help is open
        if (!this.elements.helpOverlay.classList.contains("hidden")) {
            return;
        }

        // Ignore if animating or game over (unless restart key)
        if (this.isAnimating) return;

        // Handle overlays - R to restart
        if (this.state?.game_over || this.state?.victory) {
            if (e.key.toLowerCase() === "r") {
                e.preventDefault();
                this.restart();
            }
            return;
        }

        // Arrow keys for movement
        const moveKeys = {
            ArrowUp: "⬆️",
            ArrowDown: "⬇️",
            ArrowLeft: "⬅️",
            ArrowRight: "➡️",
            w: "⬆️",
            s: "⬇️",
            a: "⬅️",
            d: "➡️",
        };

        if (moveKeys[e.key]) {
            e.preventDefault();
            this.handleMove(moveKeys[e.key]);
            return;
        }

        // Action keys
        switch (e.key.toLowerCase()) {
            case " ": // Space for look
            case "l":
                e.preventDefault();
                this.handleAction("look");
                break;
            case "e": // E for take (like "equip" or "examine")
            case "t":
                e.preventDefault();
                this.handleAction("take");
                break;
            case "f": // F for fight/attack
            case "x":
                e.preventDefault();
                this.handleAction("attack");
                break;
            case "p": // P for potion
            case "h": // H for heal
                e.preventDefault();
                this.handleAction("use-potion");
                break;
            case "k": // K for key
            case "u": // U for unlock
                e.preventDefault();
                this.handleAction("use-key");
                break;
            case "1":
            case "2":
            case "3":
            case "4":
            case "5":
            case "6":
            case "7":
            case "8":
            case "9":
                // Number keys select items (1-9)
                e.preventDefault();
                this.selectItemByIndex(parseInt(e.key) - 1);
                break;
        }
    }

    /**
     * Select an item by index (for keyboard shortcuts).
     */
    selectItemByIndex(index) {
        // Try room items first, then inventory
        const roomItems = this.state?.room_items || [];
        const inventory = this.state?.inventory || [];
        const allItems = [...roomItems, ...inventory];

        if (index >= 0 && index < allItems.length) {
            this.selectItem(allItems[index], index < roomItems.length ? "room" : "inventory");
        }
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
            case "item_taken_combat":
                // Player took damage while grabbing item
                await this.animateCombatItemPickup(event.data.item);
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

    async animateCombatItemPickup(item) {
        // Show damage first (enemy attacks while player is distracted)
        this.elements.roomEmoji.classList.add("shake");
        this.elements.health.classList.add("damage-flash");
        await this.delay(200);

        // Then show item pickup
        const itemEl = this.elements.visibleItems.querySelector(
            `[data-item="${item}"]`
        );
        if (itemEl) {
            itemEl.classList.add("item-pickup");
        }
        await this.delay(300);

        this.elements.roomEmoji.classList.remove("shake");
        this.elements.health.classList.remove("damage-flash");
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
        this.elements.helpOverlay.classList.add("hidden");
        this.clearConfetti();
        this.currentRoomId = null; // Reset to trigger particle refresh
    }

    toggleHelp() {
        this.elements.helpOverlay.classList.toggle("hidden");
    }

    hideHelp() {
        this.elements.helpOverlay.classList.add("hidden");
    }

    async restart() {
        await this.newGame();
        this.render();
    }

    /**
     * Sanitize emoji - only allow valid emoji characters.
     * Prevents XSS by rejecting non-emoji content.
     */
    sanitizeEmoji(str) {
        if (!str || typeof str !== "string") return "";
        // Only allow emoji characters (no HTML/JS)
        const emojiRegex = /^[\p{Emoji}\p{Emoji_Modifier}\p{Emoji_Component}\p{Emoji_Modifier_Base}\p{Emoji_Presentation}]+$/u;
        return emojiRegex.test(str) ? str : "❓";
    }

    /**
     * Create an item span element safely (no innerHTML).
     */
    createItemElement(item, className, isSelected) {
        const span = document.createElement("span");
        span.className = className + (isSelected ? " selected" : "");
        span.dataset.item = item;
        span.textContent = this.sanitizeEmoji(item);
        return span;
    }

    render() {
        if (!this.state) return;

        // Status bar (textContent is XSS-safe)
        this.elements.location.textContent = "📍" + this.sanitizeEmoji(this.state.location);
        this.elements.health.textContent = "❤️".repeat(this.state.health) + 
            "🖤".repeat(this.state.max_health - this.state.health);
        this.elements.score.textContent = "💰" + this.state.score;

        // Room view
        this.elements.roomEmoji.textContent = this.sanitizeEmoji(this.state.location);
        this.elements.roomView.classList.toggle("dark", this.state.is_dark);

        // Update ambient particles if room changed
        if (this.state.location_id !== this.currentRoomId) {
            this.currentRoomId = this.state.location_id;
            this.updateAmbientParticles(this.currentRoomId);
        }

        // Visible items (using DOM methods instead of innerHTML)
        this.elements.visibleItems.replaceChildren();
        this.state.room_items.forEach((item) => {
            const el = this.createItemElement(item, "item", this.selectedItem === item);
            this.elements.visibleItems.appendChild(el);
        });

        // Enemies (using DOM methods instead of innerHTML)
        this.elements.enemyDisplay.replaceChildren();
        if (this.state.room_enemies.length > 0) {
            const enemy = this.state.room_enemies[0];
            
            const emojiSpan = document.createElement("span");
            emojiSpan.className = "enemy-emoji";
            emojiSpan.textContent = this.sanitizeEmoji(enemy.emoji);
            
            const healthSpan = document.createElement("span");
            healthSpan.className = "enemy-health";
            healthSpan.textContent = "❤️".repeat(Math.min(enemy.health, 10));
            
            this.elements.enemyDisplay.appendChild(emojiSpan);
            this.elements.enemyDisplay.appendChild(healthSpan);
        }

        // Inventory (using DOM methods instead of innerHTML)
        this.elements.inventorySlots.replaceChildren();
        this.state.inventory.forEach((item) => {
            const el = this.createItemElement(item, "inv-item", this.selectedItem === item);
            this.elements.inventorySlots.appendChild(el);
        });

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
            this.showVictory();
        }
    }

    /**
     * Show victory screen with confetti animation.
     */
    showVictory() {
        this.elements.victoryOverlay.classList.remove("hidden");
        this.createConfetti();
    }

    /**
     * Create falling confetti emojis.
     */
    createConfetti() {
        const container = this.elements.confettiContainer;
        container.innerHTML = "";

        // Create 50 confetti pieces
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement("span");
            confetti.className = "confetti";
            confetti.textContent = this.confettiEmojis[
                Math.floor(Math.random() * this.confettiEmojis.length)
            ];

            // Random horizontal position
            confetti.style.left = Math.random() * 100 + "%";

            // Random animation duration (2-4 seconds)
            const duration = 2 + Math.random() * 2;
            confetti.style.animationDuration = duration + "s";

            // Random delay for staggered effect
            confetti.style.animationDelay = Math.random() * 2 + "s";

            // Random size variation
            confetti.style.fontSize = (1.5 + Math.random() * 1.5) + "rem";

            container.appendChild(confetti);
        }

        // Clean up confetti after animation
        setTimeout(() => {
            container.innerHTML = "";
        }, 6000);
    }

    /**
     * Clear confetti container.
     */
    clearConfetti() {
        if (this.elements.confettiContainer) {
            this.elements.confettiContainer.innerHTML = "";
        }
    }

    /**
     * Update ambient particles based on current room.
     */
    updateAmbientParticles(roomId) {
        // Clear existing particles
        this.clearAmbientParticles();

        const config = this.ambientConfig[roomId];
        if (!config) return;

        // Create particles
        this.createAmbientParticles(config);

        // Set up continuous particle generation
        this.ambientInterval = setInterval(() => {
            this.createAmbientParticles(config);
        }, 2000);
    }

    /**
     * Create ambient particles for a room.
     */
    createAmbientParticles(config) {
        const container = this.elements.ambientContainer;
        if (!container) return;

        // Limit total particles
        const existing = container.children.length;
        const toCreate = Math.min(config.count, 20 - existing);

        for (let i = 0; i < toCreate; i++) {
            const particle = document.createElement("span");
            particle.className = `ambient-particle ${config.class}`;
            particle.textContent = config.emoji;

            // Random position
            particle.style.left = Math.random() * 100 + "%";
            particle.style.top = Math.random() * 100 + "%";

            // Random duration within range
            const [minDur, maxDur] = config.duration;
            const duration = minDur + Math.random() * (maxDur - minDur);
            particle.style.animationDuration = duration + "s";

            // Random delay
            particle.style.animationDelay = Math.random() * 2 + "s";

            container.appendChild(particle);

            // Remove particle after animation
            setTimeout(() => {
                if (particle.parentNode) {
                    particle.remove();
                }
            }, (duration + 2) * 1000);
        }
    }

    /**
     * Clear ambient particles.
     */
    clearAmbientParticles() {
        if (this.ambientInterval) {
            clearInterval(this.ambientInterval);
            this.ambientInterval = null;
        }
        if (this.elements.ambientContainer) {
            this.elements.ambientContainer.innerHTML = "";
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
