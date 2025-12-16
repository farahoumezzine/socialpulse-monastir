/**
 * SocialPulse Monastir - Dashboard JavaScript
 * Auteur:  Farah Oumezzine
 * 2025
 */

// Configuration
const API_URL = 'http://localhost:5000';

// Elements
const textInput = document.getElementById('textInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const modelSelect = document.getElementById('modelSelect');
const resultSection = document. getElementById('resultSection');
const batchInput = document.getElementById('batchInput');
const batchAnalyzeBtn = document.getElementById('batchAnalyzeBtn');
const batchResultSection = document.getElementById('batchResultSection');
const historyList = document.getElementById('historyList');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const apiStatus = document.getElementById('apiStatus');

// History
let history = JSON.parse(localStorage.getItem('socialpulse_history') || '[]');

// ============================================================
// API Functions
// ============================================================

async function checkApiStatus() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'ok') {
            apiStatus.textContent = '🟢 En ligne';
            apiStatus.className = 'status-indicator online';
        } else {
            throw new Error('API not ok');
        }
    } catch (error) {
        apiStatus.textContent = '🔴 Hors ligne';
        apiStatus.className = 'status-indicator offline';
    }
}

async function analyzeSentiment(text, model) {
    const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text, model })
    });
    
    return await response.json();
}

async function analyzeBatch(texts, model) {
    const response = await fetch(`${API_URL}/predict/batch`, {
        method: 'POST',
        headers:  {
            'Content-Type':  'application/json'
        },
        body: JSON.stringify({ texts, model })
    });
    
    return await response. json();
}

// ============================================================
// UI Functions
// ============================================================

function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function displayResult(data) {
    if (!data. success) {
        alert('Erreur:  ' + data.error);
        return;
    }
    
    // Show result section
    resultSection.classList.remove('hidden');
    
    // Sentiment display
    const emojiMap = {
        'positive': '😊',
        'negative': '😞',
        'neutral': '😐'
    };
    
    document.getElementById('sentimentEmoji').textContent = emojiMap[data.sentiment] || '😐';
    
    const sentimentLabel = document.getElementById('sentimentLabel');
    sentimentLabel.textContent = data.sentiment. toUpperCase();
    sentimentLabel.className = 'sentiment-label ' + data. sentiment;
    
    // Confidence
    document.getElementById('confidenceValue').textContent = data.confidence + '%';
    document.getElementById('progressFill').style.width = data. confidence + '%';
    
    // Probabilities
    const probs = data.probabilities;
    
    document.getElementById('probPositive').style.width = (probs.positive || 0) + '%';
    document.getElementById('probPositiveValue').textContent = (probs.positive || 0) + '%';
    
    document.getElementById('probNeutral').style.width = (probs.neutral || 0) + '%';
    document.getElementById('probNeutralValue').textContent = (probs.neutral || 0) + '%';
    
    document.getElementById('probNegative').style.width = (probs.negative || 0) + '%';
    document.getElementById('probNegativeValue').textContent = (probs.negative || 0) + '%';
    
    // Model used
    document.getElementById('modelUsed').textContent = data.model_used === 'bert' ? 'BERT (CAMeLBERT)' : 'Naive Bayes';
    
    // Add to history
    addToHistory(data.text, data.sentiment);
    
    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

function displayBatchResults(data) {
    if (!data.success) {
        alert('Erreur: ' + data.error);
        return;
    }
    
    // Show batch result section
    batchResultSection. classList.remove('hidden');
    
    // Summary
    document.getElementById('summaryPositive').textContent = data.summary.positive;
    document.getElementById('summaryNeutral').textContent = data.summary.neutral;
    document.getElementById('summaryNegative').textContent = data.summary.negative;
    
    // Table
    const tbody = document.getElementById('batchResultsBody');
    tbody.innerHTML = '';
    
    data.results. forEach((result, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>${escapeHtml(result.text)}</td>
            <td>
                <span class="history-sentiment ${result.sentiment}">
                    ${result.emoji} ${result.sentiment}
                </span>
            </td>
            <td>${result.confidence}%</td>
        `;
        tbody.appendChild(tr);
    });
    
    // Scroll to results
    batchResultSection.scrollIntoView({ behavior: 'smooth' });
}

function addToHistory(text, sentiment) {
    // Add to beginning
    history. unshift({ text, sentiment, timestamp: Date.now() });
    
    // Limit to 20 items
    if (history.length > 20) {
        history = history.slice(0, 20);
    }
    
    // Save to localStorage
    localStorage.setItem('socialpulse_history', JSON.stringify(history));
    
    // Update UI
    renderHistory();
}

function renderHistory() {
    if (history.length === 0) {
        historyList.innerHTML = '<p class="empty-history">Aucune analyse effectuée</p>';
        return;
    }
    
    historyList.innerHTML = history.map(item => `
        <div class="history-item">
            <span class="history-text">${escapeHtml(item.text)}</span>
            <span class="history-sentiment ${item.sentiment}">
                ${item.sentiment}
            </span>
        </div>
    `).join('');
}

function clearHistory() {
    history = [];
    localStorage.removeItem('socialpulse_history');
    renderHistory();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================
// Event Listeners
// ============================================================

analyzeBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    
    if (! text) {
        alert('Veuillez entrer un texte à analyser');
        return;
    }
    
    const model = modelSelect.value;
    
    showLoading();
    
    try {
        const data = await analyzeSentiment(text, model);
        displayResult(data);
    } catch (error) {
        alert('Erreur de connexion à l\'API.  Vérifiez que le serveur est démarré.');
        console.error(error);
    } finally {
        hideLoading();
    }
});

clearBtn.addEventListener('click', () => {
    textInput.value = '';
    resultSection.classList.add('hidden');
});

batchAnalyzeBtn.addEventListener('click', async () => {
    const text = batchInput.value.trim();
    
    if (!text) {
        alert('Veuillez entrer des textes à analyser');
        return;
    }
    
    const texts = text.split('\n').filter(t => t.trim());
    
    if (texts. length === 0) {
        alert('Veuillez entrer au moins un texte');
        return;
    }
    
    const model = modelSelect.value;
    
    showLoading();
    
    try {
        const data = await analyzeBatch(texts, model);
        displayBatchResults(data);
    } catch (error) {
        alert('Erreur de connexion à l\'API. Vérifiez que le serveur est démarré.');
        console.error(error);
    } finally {
        hideLoading();
    }
});

clearHistoryBtn.addEventListener('click', () => {
    if (confirm('Êtes-vous sûr de vouloir effacer l\'historique ?')) {
        clearHistory();
    }
});

// Allow Enter key to submit (with Ctrl)
textInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        analyzeBtn.click();
    }
});

// ============================================================
// Initialization
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    checkApiStatus();
    renderHistory();
    
    // Check API status every 30 seconds
    setInterval(checkApiStatus, 30000);
});