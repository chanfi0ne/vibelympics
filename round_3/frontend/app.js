// PURPOSE: Frontend JavaScript for PARANOID SBOM Roast Generator
// Handles API calls, session management, and UI updates

const API_BASE = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : '';  // Same origin in production

// Session management
let sessionId = localStorage.getItem('paranoid_session') || crypto.randomUUID();
localStorage.setItem('paranoid_session', sessionId);

// DOM elements
const inputType = document.getElementById('input-type');
const inputContent = document.getElementById('input-content');
const roastBtn = document.getElementById('roast-btn');
const randomBtn = document.getElementById('random-btn');
const results = document.getElementById('results');
const errorBox = document.getElementById('error-box');
const errorMessage = document.getElementById('error-message');
const loading = document.getElementById('loading');
const roastSummary = document.getElementById('roast-summary').querySelector('p');
const caption = document.getElementById('caption');
const findingsList = document.getElementById('findings-list');
const sbomJson = document.getElementById('sbom-json');
const memeImage = document.getElementById('meme-image');

// Paranoia display
const levelName = document.getElementById('level-name');
const paranoiaMessage = document.getElementById('paranoia-message');
const levelDots = [
    document.getElementById('level-0'),
    document.getElementById('level-1'),
    document.getElementById('level-2')
];

// Random terrible examples for "Roast Me" button
const TERRIBLE_EXAMPLES = {
    package_json: `{
  "dependencies": {
    "lodash": "^4.17.11",
    "moment": "^2.24.0",
    "request": "^2.88.0",
    "left-pad": "^1.3.0",
    "event-stream": "^3.3.4",
    "colors": "^1.4.0",
    "express": "^4.17.1",
    "jquery": "^3.5.0",
    "react": "^16.8.0",
    "webpack": "^4.41.0"
  },
  "devDependencies": {
    "mocha": "^5.2.0",
    "chai": "^4.2.0"
  }
}`,
    requirements_txt: `flask==1.0.0
requests==2.20.0
django==2.0.0
pillow==5.0.0
numpy==1.14.0
pandas==0.23.0
sqlalchemy==1.2.0
celery==4.1.0
redis==2.10.0
boto3==1.7.0
urllib3==1.24.0
pyyaml==3.12`
};

function updateParanoiaDisplay(paranoia) {
    if (!paranoia) return;

    const level = paranoia.level || 0;
    const name = paranoia.level_name || 'CHILL';
    const message = paranoia.message || '';

    // Update level name and color
    levelName.textContent = name;
    levelName.className = 'ml-2';

    if (level === 0) {
        levelName.classList.add('text-terminal-green');
    } else if (level === 1) {
        levelName.classList.add('text-terminal-amber');
    } else {
        levelName.classList.add('text-terminal-red', 'glow-red');
    }

    // Update dots
    levelDots.forEach((dot, i) => {
        dot.className = 'w-4 h-4 rounded';
        if (i <= level) {
            if (level === 0) dot.classList.add('bg-terminal-green');
            else if (level === 1) dot.classList.add('bg-terminal-amber');
            else dot.classList.add('bg-terminal-red');
        } else {
            dot.classList.add('bg-gray-700');
        }
    });

    // Update message
    paranoiaMessage.textContent = message;
}

function showError(message) {
    errorMessage.textContent = message;
    errorBox.classList.remove('hidden');
    results.classList.add('hidden');
    loading.classList.add('hidden');
}

function showResults(data) {
    errorBox.classList.add('hidden');
    loading.classList.add('hidden');
    results.classList.remove('hidden');

    // Meme image
    memeImage.src = `${API_BASE}${data.meme_url}`;

    // Roast summary
    roastSummary.textContent = data.roast_summary;

    // Caption
    caption.textContent = data.caption;

    // Findings
    findingsList.innerHTML = '';
    for (const finding of data.findings) {
        const div = document.createElement('div');
        div.className = 'flex items-center gap-2 p-2 rounded bg-terminal-text/5';

        const severityColors = {
            critical: 'text-terminal-red',
            high: 'text-terminal-red',
            medium: 'text-terminal-amber',
            low: 'text-terminal-green',
            info: 'text-terminal-blue'
        };
        const color = severityColors[finding.severity] || 'text-terminal-text';

        div.innerHTML = `
            <span class="uppercase text-xs ${color}">[${finding.severity}]</span>
            <span class="text-sm">${finding.detail}</span>
        `;
        findingsList.appendChild(div);
    }

    // SBOM
    if (data.sbom) {
        sbomJson.textContent = JSON.stringify(data.sbom, null, 2);
    }

    // Update paranoia
    updateParanoiaDisplay(data.paranoia);
}

async function doRoast() {
    const type = inputType.value;
    const content = inputContent.value.trim();

    if (!content) {
        showError('Your input is empty. Much like your security strategy.');
        return;
    }

    // Show loading
    loading.classList.remove('hidden');
    results.classList.add('hidden');
    errorBox.classList.add('hidden');
    roastBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/roast`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-Id': sessionId
            },
            body: JSON.stringify({
                input_type: type,
                content: content,
                include_sbom: true
            })
        });

        const data = await response.json();

        if (!response.ok) {
            // Handle special error codes
            if (response.status === 451) {
                showError(`HTTP 451 - ${data.detail}`);
            } else if (response.status === 503) {
                showError(data.detail);
            } else {
                showError(data.detail || 'Something went wrong.');
            }
            return;
        }

        showResults(data);

    } catch (err) {
        showError(`Network error: ${err.message}. Is the backend running?`);
    } finally {
        roastBtn.disabled = false;
        loading.classList.add('hidden');
    }
}

function loadRandomExample() {
    const type = inputType.value;
    if (TERRIBLE_EXAMPLES[type]) {
        inputContent.value = TERRIBLE_EXAMPLES[type];
    } else {
        inputContent.value = 'lodash@4.17.11';
        inputType.value = 'single_package';
    }
}

// Fetch initial paranoia state
async function fetchParanoiaState() {
    try {
        const response = await fetch(`${API_BASE}/paranoia`, {
            headers: { 'X-Session-Id': sessionId }
        });
        if (response.ok) {
            const data = await response.json();
            updateParanoiaDisplay(data);
        }
    } catch (err) {
        console.log('Could not fetch paranoia state:', err);
    }
}

// Event listeners
roastBtn.addEventListener('click', doRoast);
randomBtn.addEventListener('click', loadRandomExample);

// Allow Ctrl+Enter to submit
inputContent.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        doRoast();
    }
});

// Initialize
fetchParanoiaState();
