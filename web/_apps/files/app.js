/**
 * Manas-Yantra — Inner Sanctum of Knowledge
 * Frontend chat logic
 */

// --- Session Management ---
let sessionId;

function generateSessionId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'sess-' + Math.random().toString(36).substring(2) + Date.now().toString(36);
}

// --- DOM Elements (assigned inside DOMContentLoaded) ---
let chatContainer, userInput, sendBtn, resetLink;

// --- Add a message to the chat ---
function addMessage(text, sender) {
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('message', sender); // sender = 'ai' or 'user'

  if (sender === 'ai') {
    // Show typing indicator first
    msgDiv.textContent = '· · ·';
    msgDiv.classList.add('typing');
    chatContainer.appendChild(msgDiv);
    scrollToBottom();

    // Replace with actual text after a delay
    const delay = 400 + Math.random() * 400;
    setTimeout(() => {
      msgDiv.classList.remove('typing');
      // Render newlines as line breaks
      msgDiv.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');
      scrollToBottom();
    }, delay);
  } else {
    msgDiv.textContent = text;
    chatContainer.appendChild(msgDiv);
    scrollToBottom();
  }

  return msgDiv;
}

// --- Escape HTML to prevent XSS ---
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// --- Scroll chat to bottom ---
function scrollToBottom() {
  chatContainer.scrollTo({
    top: chatContainer.scrollHeight,
    behavior: 'smooth'
  });
}

// --- Send message to backend ---
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  // Display user message
  addMessage(text, 'user');
  userInput.value = '';

  // Disable input while waiting
  setInputEnabled(false);

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, session_id: sessionId })
    });

    if (!res.ok) {
      throw new Error('Server error: ' + res.status);
    }

    const data = await res.json();
    addMessage(data.response, 'ai');

    // Update session_id if server assigned one
    if (data.session_id) {
      sessionId = data.session_id;
    }
  } catch (err) {
    addMessage('The sanctum trembles... An error has occurred. Try again.', 'ai');
    console.error('Chat error:', err);
  }

  setInputEnabled(true);
  userInput.focus();
}

// --- Enable/disable input controls ---
function setInputEnabled(enabled) {
  userInput.disabled = !enabled;
  sendBtn.disabled = !enabled;
  if (!enabled) {
    sendBtn.style.opacity = '0.5';
  } else {
    sendBtn.style.opacity = '1';
  }
}

// --- Reset chat (Return to the Gate) ---
function resetChat() {
  chatContainer.innerHTML = '';
  sessionId = generateSessionId();
  loadWelcomeMessage();
}

// --- Load initial welcome message from server ---
async function loadWelcomeMessage() {
  setInputEnabled(false);
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: '', session_id: sessionId })
    });
    const data = await res.json();
    addMessage(data.response, 'ai');
    if (data.session_id) {
      sessionId = data.session_id;
    }
  } catch (err) {
    addMessage(
      'Welcome, O Seeker, to the Manas-Yantra, the Inner Sanctum of Knowledge. ' +
      'Here, the ancient wisdom of the Pancha Koshas awaits those who dare to explore the depths of consciousness. ' +
      'What is it that you seek?',
      'ai'
    );
  }
  setInputEnabled(true);
  userInput.focus();
}

// --- Event Listeners ---
// (registered inside DOMContentLoaded below)

// --- Initialize on page load ---
document.addEventListener('DOMContentLoaded', () => {
  // Assign DOM elements
  chatContainer = document.getElementById('chat-container');
  userInput     = document.getElementById('user-input');
  sendBtn       = document.getElementById('send-btn');
  resetLink     = document.getElementById('reset-link');

  // Init session
  sessionId = generateSessionId();

  // Attach events
  sendBtn.addEventListener('click', sendMessage);
  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  resetLink.addEventListener('click', (e) => {
    e.preventDefault();
    resetChat();
  });

  // Load welcome message
  loadWelcomeMessage();
});
