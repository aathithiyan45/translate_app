// Voice Recognition Setup
const voiceInputBtn = document.getElementById('voice-input-btn');
const sourceTextArea = document.getElementById('source-text');

if ('webkitSpeechRecognition' in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = function() {
        voiceInputBtn.classList.add('recording');
        showStatusMessage('Listening...', 'info');
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        sourceTextArea.value = transcript;
        updateCharCount();
        showStatusMessage('Voice input received!', 'success');
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        showStatusMessage('Voice input failed. Please try again.', 'error');
        voiceInputBtn.classList.remove('recording');
    };

    recognition.onend = function() {
        voiceInputBtn.classList.remove('recording');
    };

    voiceInputBtn.addEventListener('click', function() {
        if (recognition.started) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });
} else {
    voiceInputBtn.style.display = 'none';
    console.log('Speech recognition not supported');
}

// Helper function to show status messages
function showStatusMessage(message, type) {
    const statusElement = document.getElementById('status-message');
    statusElement.textContent = message;
    statusElement.className = `status-message show ${type}`;
    
    setTimeout(() => {
        statusElement.classList.remove('show');
    }, 3000);
}

// Helper function to update character count
function updateCharCount() {
    const charCount = document.querySelector('.char-count');
    charCount.textContent = `${sourceTextArea.value.length} characters`;
}

// Translation functionality
const translateBtn = document.getElementById('translate-btn');
const targetLanguage = document.getElementById('target-language');
const translatedText = document.getElementById('translated-text');
const sourceText = document.getElementById('source-text');
const clearSourceBtn = document.getElementById('clear-source');
const copyTranslationBtn = document.getElementById('copy-translation');
const charCount = document.querySelector('.char-count');

// Update character count
sourceText.addEventListener('input', function() {
    charCount.textContent = `${this.value.length} characters`;
});

// Clear source text
clearSourceBtn.addEventListener('click', function() {
    sourceText.value = '';
    charCount.textContent = '0 characters';
});

// Copy translation
copyTranslationBtn.addEventListener('click', function() {
    if (translatedText.value) {
        navigator.clipboard.writeText(translatedText.value)
            .then(() => showStatusMessage('Translation copied!', 'success'))
            .catch(() => showStatusMessage('Failed to copy', 'error'));
    }
});

// Translation function
translateBtn.addEventListener('click', async function() {
    const text = sourceText.value.trim();
    if (!text) {
        showStatusMessage('Please enter text to translate', 'error');
        return;
    }

    try {
        translateBtn.disabled = true;
        translateBtn.innerHTML = '<span class="loading"></span> Translating...';

        const response = await fetch('/translate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
                text: text,
                target_language: targetLanguage.value
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            translatedText.value = data.translated_text;
            showStatusMessage('Translation complete!', 'success');
        } else {
            throw new Error(data.error || 'Translation failed');
        }
    } catch (error) {
        console.error('Translation error:', error);
        showStatusMessage(error.message || 'Translation failed', 'error');
    } finally {
        translateBtn.disabled = false;
        translateBtn.innerHTML = '<i class="fas fa-language"></i> Translate';
    }
});

// History functionality
const historyList = document.getElementById('history-list');
const clearHistoryBtn = document.getElementById('clear-history-btn');

// Clear all history
clearHistoryBtn?.addEventListener('click', async function() {
    if (confirm('Are you sure you want to clear all history?')) {
        try {
            const response = await fetch('/clear-history/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                }
            });

            if (response.ok) {
                historyList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-history"></i>
                        <p>No translation history yet</p>
                        <p>Your recent translations will appear here</p>
                    </div>
                `;
                showStatusMessage('History cleared', 'success');
            }
        } catch (error) {
            showStatusMessage('Failed to clear history', 'error');
        }
    }
});

// Delete individual history item
historyList?.addEventListener('click', async function(e) {
    const deleteBtn = e.target.closest('.delete-btn');
    if (deleteBtn) {
        e.preventDefault();
        const historyItem = deleteBtn.closest('.history-item');
        const original = historyItem.dataset.original;
        const timestamp = historyItem.querySelector('.timestamp').textContent;

        if (confirm('Are you sure you want to delete this translation?')) {
            try {
                const response = await fetch('/delete-history-item/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify({
                        original: original,
                        timestamp: timestamp
                    })
                });

                if (!response.ok) {
                    throw new Error('Failed to delete');
                }

                historyItem.remove();
                showStatusMessage('Translation deleted successfully', 'success');

                // Check if history is empty
                if (!historyList.querySelector('.history-item')) {
                    historyList.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-history"></i>
                            <p>No translation history yet</p>
                            <p>Your recent translations will appear here</p>
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Delete error:', error);
                showStatusMessage('Failed to delete translation', 'error');
            }
        }
    }
});

// Get CSRF token from cookies
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Add swap functionality
const swapBtn = document.getElementById('swap-languages');
swapBtn.addEventListener('click', function() {
    const currentText = sourceTextArea.value;
    sourceTextArea.value = translatedText.value;
    translatedText.value = currentText;
    updateCharCount();
});