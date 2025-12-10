# Repojacker Frontend

Terminal-themed React frontend for the Repojacker npm supply chain security auditor.

## Features

- **Terminal Security Aesthetic**: Dark backgrounds, cyan accents, monospace fonts, glow effects
- **Interactive Risk Visualization**: Animated score display with radar chart analysis
- **Real-time Package Scanning**: Live API integration with loading states
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Smooth Animations**: Framer Motion for professional transitions

## Tech Stack

- React 18
- Vite
- Tailwind CSS
- Recharts (radar visualization)
- Framer Motion (animations)

## Development

```bash
# Install dependencies
npm install

# Run development server (proxies /api to localhost:8000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Docker Build

```bash
# Build image
docker build -t repojacker-frontend .

# Run container
docker run -p 80:80 repojacker-frontend
```

## Project Structure

```
src/
├── App.jsx              # Main application component
├── components/
│   ├── SearchBar.jsx    # Package search input
│   ├── RiskScore.jsx    # Animated score display
│   ├── RiskRadar.jsx    # Radar chart visualization
│   ├── FindingsList.jsx # Expandable findings list
│   ├── MetadataCard.jsx # Package metadata display
│   └── Loading.jsx      # Terminal loading animation
├── hooks/
│   └── useAudit.js      # API integration hook
├── index.css            # Global styles + Tailwind
└── main.jsx             # React entry point
```

## API Integration

The `useAudit` hook manages communication with the backend:

```javascript
const { loading, result, error, auditPackage, reset } = useAudit();

// Trigger audit
await auditPackage('package-name');
```

Expects backend endpoint: `POST /api/audit` with body `{"package_name": "..."}`

## Styling

Custom Tailwind theme extends default with security-themed colors:

- **Backgrounds**: void (#050508), primary (#0a0a0f), secondary (#0f0f18)
- **Accent**: Cyan (#00fff2) with glow variants
- **Severity**: Critical (red), High (orange), Medium (yellow), Low (green), Info (blue)

Utility classes: `btn-glow`, `card`, `input-terminal`, `badge-*`, `text-glow-*`

## Environment

Development server proxies `/api/*` to `http://localhost:8000` (backend).
Production nginx proxies to `http://backend:8000` (Docker network).
