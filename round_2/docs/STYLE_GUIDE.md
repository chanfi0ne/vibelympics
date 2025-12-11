# Repojacker - UI/UX Style Guide

## Aesthetic Vision: "Terminal Security"

**Core Concept:** A cybersecurity command center meets retro terminal. The interface should feel like you're a security analyst at a high-tech operations center, running scans on suspicious packages. Think: the aesthetics of Mr. Robot meets the functionality of a modern security dashboard.

**Mood Keywords:**
- Vigilant
- Technical
- Precise
- Atmospheric
- Trustworthy
- Slightly ominous

---

## Color System

### Primary Palette

```css
:root {
  /* Backgrounds - Deep space darkness */
  --bg-void: #050508;           /* Deepest black - page background */
  --bg-primary: #0a0a0f;        /* Primary surface */
  --bg-secondary: #0f0f18;      /* Elevated surface */
  --bg-card: #14141f;           /* Card backgrounds */
  --bg-card-hover: #1a1a28;     /* Card hover state */
  
  /* Borders & Lines */
  --border-subtle: #1e1e2e;     /* Subtle separators */
  --border-default: #2a2a3a;    /* Default borders */
  --border-focus: #3a3a4a;      /* Focus states */
  
  /* Text */
  --text-primary: #e8e8ed;      /* Primary text */
  --text-secondary: #8888a0;    /* Secondary/muted text */
  --text-tertiary: #555566;     /* Disabled/hint text */
  
  /* Accent - Cyber Cyan */
  --accent-primary: #00fff2;    /* Primary accent - electric cyan */
  --accent-glow: #00fff240;     /* Glow effect (25% opacity) */
  --accent-subtle: #00fff215;   /* Subtle highlights */
  
  /* Severity Colors - The Threat Spectrum */
  --severity-critical: #ff0040;  /* Bright red - DANGER */
  --severity-critical-bg: #ff004015;
  --severity-critical-glow: #ff004060;
  
  --severity-high: #ff6b00;      /* Orange - WARNING */
  --severity-high-bg: #ff6b0015;
  --severity-high-glow: #ff6b0060;
  
  --severity-medium: #ffd000;    /* Yellow - CAUTION */
  --severity-medium-bg: #ffd00015;
  --severity-medium-glow: #ffd00060;
  
  --severity-low: #00ff88;       /* Green - MINOR */
  --severity-low-bg: #00ff8815;
  --severity-low-glow: #00ff8860;
  
  --severity-info: #00b4ff;      /* Blue - INFO */
  --severity-info-bg: #00b4ff15;
  --severity-info-glow: #00b4ff60;
  
  /* Status Colors */
  --status-verified: #00ff88;
  --status-unverified: #ff6b00;
  --status-failed: #ff0040;
}
```

### Color Usage Rules

1. **Backgrounds:** Always use the deep blacks. Never pure black (#000) - too harsh.
2. **Text:** Primary for important content, secondary for labels/metadata.
3. **Accents:** Cyan for interactive elements, actions, and highlights.
4. **Severity:** ONLY for risk indicators. Never decorative.
5. **Glow Effects:** Use sparingly for emphasis. A little goes a long way.

---

## Typography

### Font Stack

```css
:root {
  /* Primary - Monospace for that terminal feel */
  --font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', 'Consolas', monospace;
  
  /* Display - For headers and hero text */
  --font-display: 'Orbitron', 'Rajdhani', 'Share Tech Mono', sans-serif;
  
  /* Fallback system mono */
  --font-system-mono: ui-monospace, 'Cascadia Code', 'Source Code Pro', monospace;
}
```

### Type Scale

```css
/* Display - Logo and Hero */
.text-display {
  font-family: var(--font-display);
  font-size: 2.5rem;      /* 40px */
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

/* Heading 1 - Section titles */
.text-h1 {
  font-family: var(--font-mono);
  font-size: 1.5rem;      /* 24px */
  font-weight: 600;
  letter-spacing: 0.05em;
}

/* Heading 2 - Card titles */
.text-h2 {
  font-family: var(--font-mono);
  font-size: 1.125rem;    /* 18px */
  font-weight: 600;
  letter-spacing: 0.02em;
}

/* Body - Primary content */
.text-body {
  font-family: var(--font-mono);
  font-size: 0.875rem;    /* 14px */
  font-weight: 400;
  line-height: 1.6;
}

/* Small - Metadata, labels */
.text-small {
  font-family: var(--font-mono);
  font-size: 0.75rem;     /* 12px */
  font-weight: 400;
  letter-spacing: 0.02em;
}

/* Code - Inline code snippets */
.text-code {
  font-family: var(--font-mono);
  font-size: 0.8125rem;   /* 13px */
  background: var(--bg-secondary);
  padding: 0.125em 0.375em;
  border-radius: 3px;
}
```

### Typography Rules

1. **All caps:** Use for labels, badges, and section headers.
2. **Letter spacing:** Increase for uppercase text (0.05-0.15em).
3. **Line height:** Generous (1.5-1.7) for readability on dark backgrounds.
4. **Never use:** Serif fonts, decorative scripts, or anything "friendly."

---

## Component Styles

### Cards

```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 1.5rem;
  
  /* Subtle inner glow */
  box-shadow: 
    inset 0 1px 0 0 rgba(255,255,255,0.03),
    0 4px 24px -8px rgba(0,0,0,0.5);
  
  transition: all 0.2s ease;
}

.card:hover {
  border-color: var(--border-default);
  background: var(--bg-card-hover);
}

/* Card with accent glow (for important items) */
.card-accent {
  border-color: var(--accent-primary);
  box-shadow: 
    0 0 20px -5px var(--accent-glow),
    inset 0 1px 0 0 rgba(0,255,242,0.1);
}
```

### Buttons

```css
/* Primary action button */
.btn-primary {
  background: transparent;
  border: 1px solid var(--accent-primary);
  color: var(--accent-primary);
  font-family: var(--font-mono);
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  
  transition: all 0.15s ease;
  
  /* Glow effect */
  box-shadow: 
    0 0 10px -3px var(--accent-glow),
    inset 0 0 20px -10px var(--accent-glow);
}

.btn-primary:hover {
  background: var(--accent-primary);
  color: var(--bg-void);
  box-shadow: 
    0 0 25px -5px var(--accent-primary),
    inset 0 0 20px -10px rgba(255,255,255,0.3);
}

.btn-primary:active {
  transform: scale(0.98);
}
```

### Input Fields

```css
.input {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 6px;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 1rem;
  padding: 1rem 1.25rem;
  width: 100%;
  
  transition: all 0.2s ease;
}

.input::placeholder {
  color: var(--text-tertiary);
}

.input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 
    0 0 0 3px var(--accent-subtle),
    0 0 20px -5px var(--accent-glow);
}

/* Scanning animation on input focus */
.input:focus::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
  animation: scan 1.5s ease-in-out infinite;
}
```

### Severity Badges

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-family: var(--font-mono);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0.25rem 0.625rem;
  border-radius: 3px;
}

.badge-critical {
  background: var(--severity-critical-bg);
  color: var(--severity-critical);
  border: 1px solid var(--severity-critical);
  box-shadow: 0 0 10px -3px var(--severity-critical-glow);
  animation: pulse-critical 2s ease-in-out infinite;
}

.badge-high {
  background: var(--severity-high-bg);
  color: var(--severity-high);
  border: 1px solid var(--severity-high);
}

.badge-medium {
  background: var(--severity-medium-bg);
  color: var(--severity-medium);
  border: 1px solid var(--severity-medium);
}

.badge-low {
  background: var(--severity-low-bg);
  color: var(--severity-low);
  border: 1px solid var(--severity-low);
}

.badge-info {
  background: var(--severity-info-bg);
  color: var(--severity-info);
  border: 1px solid var(--severity-info);
}
```

---

## Risk Score Display

The centerpiece of the UI. Should feel like a threat level indicator.

```
┌─────────────────────────────────┐
│                                 │
│         ╔═══════════╗           │
│         ║           ║           │
│         ║    23     ║           │
│         ║           ║           │
│         ╚═══════════╝           │
│                                 │
│      ▰▰▰▰▰▱▱▱▱▱▱▱▱▱▱▱           │
│                                 │
│        ░░ LOW RISK ░░           │
│                                 │
└─────────────────────────────────┘
```

### Score Ring Animation

```css
.score-ring {
  /* SVG circle with stroke-dasharray animation */
  stroke: var(--severity-low);
  stroke-width: 8;
  stroke-linecap: round;
  fill: none;
  
  /* Animate from 0 to calculated value */
  animation: draw-ring 1.5s ease-out forwards;
}

@keyframes draw-ring {
  from {
    stroke-dashoffset: 283; /* Full circumference */
  }
  to {
    stroke-dashoffset: calc(283 - (283 * var(--score) / 100));
  }
}

/* Score number count-up */
.score-value {
  font-family: var(--font-display);
  font-size: 4rem;
  font-weight: 700;
  
  /* Tabular numbers for smooth animation */
  font-variant-numeric: tabular-nums;
}
```

---

## Risk Radar Chart

Spider/radar chart showing the four security dimensions.

```
              AUTHENTICITY
                   ▲
                  ╱│╲
                 ╱ │ ╲
                ╱  │  ╲
               ╱   │   ╲
   REPUTATION ◄────┼────► MAINTENANCE
               ╲   │   ╱
                ╲  │  ╱
                 ╲ │ ╱
                  ╲│╱
                   ▼
               SECURITY
```

### Radar Styling

```css
.radar-chart {
  /* Grid lines - subtle */
  .radar-grid {
    stroke: var(--border-subtle);
    stroke-width: 1;
    fill: none;
  }
  
  /* Data polygon */
  .radar-data {
    fill: var(--accent-subtle);
    stroke: var(--accent-primary);
    stroke-width: 2;
    
    /* Draw animation */
    animation: radar-reveal 1s ease-out forwards;
  }
  
  /* Data points */
  .radar-point {
    fill: var(--accent-primary);
    r: 4;
    
    /* Glow effect */
    filter: drop-shadow(0 0 4px var(--accent-primary));
  }
  
  /* Axis labels */
  .radar-label {
    font-family: var(--font-mono);
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    fill: var(--text-secondary);
  }
}
```

---

## Animations

### Keyframes Library

```css
/* Scanning line effect */
@keyframes scan {
  0%, 100% {
    transform: translateX(-100%);
    opacity: 0;
  }
  50% {
    transform: translateX(100%);
    opacity: 1;
  }
}

/* Pulse for critical items */
@keyframes pulse-critical {
  0%, 100% {
    box-shadow: 0 0 10px -3px var(--severity-critical-glow);
  }
  50% {
    box-shadow: 0 0 20px -3px var(--severity-critical);
  }
}

/* Glow pulse for accent elements */
@keyframes glow-pulse {
  0%, 100% {
    box-shadow: 0 0 10px -3px var(--accent-glow);
  }
  50% {
    box-shadow: 0 0 25px -3px var(--accent-primary);
  }
}

/* Fade in up - for staggered content */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Terminal cursor blink */
@keyframes cursor-blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

/* Radar reveal */
@keyframes radar-reveal {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Number count up (use with JS) */
@keyframes count-up {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
```

### Animation Timing

```css
:root {
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-out-back: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --duration-reveal: 800ms;
}
```

---

## Special Effects

### Scanline Overlay (Subtle CRT Effect)

```css
.scanlines::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.1) 0px,
    rgba(0, 0, 0, 0.1) 1px,
    transparent 1px,
    transparent 2px
  );
  opacity: 0.15;
  z-index: 9999;
}
```

### Noise Texture (Subtle Grain)

```css
.noise::after {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  opacity: 0.02;
  z-index: 9998;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%' height='100%' filter='url(%23noise)'/%3E%3C/svg%3E");
}
```

### Glowing Border Effect

```css
.glow-border {
  position: relative;
}

.glow-border::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(
    135deg,
    var(--accent-primary) 0%,
    transparent 50%,
    var(--accent-primary) 100%
  );
  -webkit-mask: 
    linear-gradient(#fff 0 0) content-box, 
    linear-gradient(#fff 0 0);
  mask: 
    linear-gradient(#fff 0 0) content-box, 
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0.5;
}
```

---

## Layout Structure

### Page Grid

```css
.app-container {
  min-height: 100vh;
  background: var(--bg-void);
  
  /* Subtle radial gradient for depth */
  background-image: radial-gradient(
    ellipse at 50% 0%,
    var(--bg-secondary) 0%,
    var(--bg-void) 70%
  );
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  
  display: grid;
  gap: 1.5rem;
}

/* Results grid */
.results-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1.5rem;
}

/* Findings list */
.findings-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
```

---

## Logo Treatment

```
██████╗ ███████╗██████╗  ██████╗      ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██╔══██╗██╔════╝██╔══██╗██╔═══██╗     ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██████╔╝█████╗  ██████╔╝██║   ██║     ██║███████║██║     █████╔╝ █████╗  ██████╔╝
██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║██   ██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║███████╗██║     ╚██████╔╝╚█████╔╝██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝  ╚════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```

**Compact ASCII variant:**
```
┌─────────────────────────────────────┐
│  ╦═╗╔═╗╔═╗╔═╗ ╦╔═╗╔═╗╦╔═╔═╗╦═╗     │
│  ╠╦╝║╣ ╠═╝║ ║ ║╠═╣║  ╠╩╗║╣ ╠╦╝     │
│  ╩╚═╚═╝╩  ╚═╝╚╝╩ ╩╚═╝╩ ╩╚═╝╩╚═     │
└─────────────────────────────────────┘
```

**Stylized text treatment:**
```
▓█████▄ ▓█████  ██▓███   ▒█████      ██▓▄▄▄       ▄████▄   ██ ▄█▀▓█████  ██▀███  
▒██▀ ██▌▓█   ▀ ▓██░  ██▒▒██▒  ██▒   ▓██▒████▄    ▒██▀ ▀█   ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒
░██   █▌▒███   ▓██░ ██▓▒▒██░  ██▒   ▒██▒██  ▀█▄  ▒▓█    ▄ ▓███▄░ ▒███   ▓██ ░▄█ ▒
```

**CSS Implementation:**

```css
.logo {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  
  /* Gradient text - cyan to white */
  background: linear-gradient(
    135deg,
    var(--accent-primary) 0%,
    var(--text-primary) 50%,
    var(--accent-primary) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  
  /* Subtle glow */
  filter: drop-shadow(0 0 10px var(--accent-glow));
}

/* Split treatment: REPO in cyan, JACKER in white */
.logo-repo {
  color: var(--accent-primary);
  text-shadow: 0 0 20px var(--accent-glow);
}

.logo-jacker {
  color: var(--text-primary);
}

/* Tagline */
.logo-tagline {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

/* ░░ REPOJACKER ░░ */
/* "Detect supply chain threats before they detect you" */
```

**Logo Variants:**

1. **Full:** `REPOJACKER` (all caps, spaced)
2. **Split:** `REPO`<span style="color:cyan">JACKER</span> (emphasis on "jacker")
3. **Icon:** `[RJ]` or `⚠️` with glitch effect
4. **Terminal:** `> repojacker_` with blinking cursor

---

## Responsive Breakpoints

```css
/* Mobile first */
@media (max-width: 640px) {
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .score-value {
    font-size: 3rem;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
}

@media (min-width: 1400px) {
  .main-content {
    max-width: 1400px;
  }
}
```

---

## Do's and Don'ts

### DO ✓
- Use the accent cyan sparingly for maximum impact
- Maintain high contrast for accessibility
- Let content breathe with generous spacing
- Use animations purposefully (loading, transitions, attention)
- Keep severity colors strictly for risk indicators

### DON'T ✗
- Use rounded corners larger than 8px
- Add decorative gradients or patterns
- Use bright colors on large surfaces
- Animate everything (it becomes noise)
- Use white backgrounds anywhere
- Add shadows that look like "floating cards"

---

## Reference Mood Board

**Visual References:**
- Mr. Robot UI screens
- Bloomberg Terminal
- Cyberpunk 2077 interfaces
- NASA mission control displays
- Metasploit/Kali Linux terminals
- Socket.dev dark mode
- Linear app (spacing and typography)

**The Feeling:**
When a user sees this interface, they should feel like they're running a legitimate security scan. The tool should inspire confidence through its precision and technical aesthetic. It's not playful, it's not corporate—it's a tool built by security people, for security people.
