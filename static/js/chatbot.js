/**
 * Rent Finder Pakistan - RENT FINDER AI Chatbot Client
 * Dual-Capability AI (Property Database Assistant + Global ChatGPT Assistant)
 */

document.addEventListener('DOMContentLoaded', () => {
  initChatbot();
});

function initChatbot() {
  const triggerBtn = document.getElementById('chatbot-trigger-btn');
  const chatModal = document.getElementById('chat-modal');
  const closeBtn = document.getElementById('chat-close-btn');
  const clearBtn = document.getElementById('chat-clear-btn');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const messagesContainer = document.getElementById('chat-messages');
  const suggestionsContainer = document.getElementById('chat-suggestions');

  if (!triggerBtn || !chatModal) return;

  // Generate or retrieve persistent Session ID
  let sessionId = localStorage.getItem('rentfinder_chat_session_id');
  if (!sessionId) {
    sessionId = 'session_' + Math.random().toString(36).substring(2, 12);
    localStorage.setItem('rentfinder_chat_session_id', sessionId);
  }

  // Toggle Chat Modal
  triggerBtn.addEventListener('click', () => {
    chatModal.classList.toggle('open');
    if (chatModal.classList.contains('open')) {
      chatInput.focus();
      scrollChatToBottom();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      chatModal.classList.remove('open');
    });
  }

  // Clear Chat History
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      sessionId = 'session_' + Math.random().toString(36).substring(2, 12);
      localStorage.setItem('rentfinder_chat_session_id', sessionId);
      messagesContainer.innerHTML = '';
      appendBotWelcomeMessage();
    });
  }

  // Quick Suggestion Chips
  if (suggestionsContainer) {
    suggestionsContainer.querySelectorAll('.chip-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const text = btn.dataset.prompt || btn.textContent.trim();
        chatInput.value = text;
        submitMessage(text);
      });
    });
  }

  // Handle Form Submit
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    submitMessage(text);
  });

  async function submitMessage(message) {
    // Append User Message
    appendMessage(message, 'user');
    chatInput.value = '';
    chatInput.disabled = true;

    // Show Typing Indicator
    const typingIndicator = showTypingIndicator();

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, sessionId: sessionId })
      });

      const data = await response.json();
      typingIndicator.remove();
      chatInput.disabled = false;
      chatInput.focus();

      if (data.success) {
        appendMessage(data.response, 'bot', data.properties);
      } else {
        appendMessage("Sorry, I encountered an issue processing your request. Please try again.", 'bot');
      }
    } catch (err) {
      console.error('Chat API Error:', err);
      typingIndicator.remove();
      chatInput.disabled = false;
      appendMessage("Network connection interrupted. Please try again.", 'bot');
    }
  }

  function appendMessage(text, role, properties = null) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;

    // Format Markdown bold, lists, and line breaks
    let formattedText = escapeHtml(text)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/### (.*?)\n/g, '<h4 style="margin: 0.5rem 0; font-size: 0.95rem; color: #10b981;">$1</h4>')
      .replace(/• (.*?)\n/g, '<li style="margin-left: 1rem; list-style-type: disc;">$1</li>')
      .replace(/\n/g, '<br>');

    bubble.innerHTML = formattedText;

    // Append matching property cards if returned by AI
    if (properties && properties.length > 0) {
      const cardsWrapper = document.createElement('div');
      cardsWrapper.className = 'chat-prop-cards';

      properties.forEach(p => {
        const card = document.createElement('a');
        card.href = p.url || `/properties/${p.id}`;
        card.target = '_blank';
        card.className = 'chat-prop-card';
        card.innerHTML = `
          <img src="${p.image}" alt="${escapeHtml(p.title)}" onerror="this.src='https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=300&q=80'">
          <div class="chat-prop-info">
            <div class="chat-prop-title">${escapeHtml(p.title)}</div>
            <div class="chat-prop-rent">PKR ${Number(p.monthly_rent).toLocaleString()} / mo</div>
            <small style="color: #94a3b8;">${escapeHtml(p.city)} • ${p.bedrooms} Beds • ${p.size}</small>
          </div>
        `;
        cardsWrapper.appendChild(card);
      });

      bubble.appendChild(cardsWrapper);
    }

    messagesContainer.appendChild(bubble);
    scrollChatToBottom();
  }

  function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'chat-bubble bot typing';
    indicator.innerHTML = `
      <div style="display: flex; gap: 4px; align-items: center; padding: 4px 0;">
        <span style="width: 7px; height: 7px; background: #10b981; border-radius: 50%; animation: pulse-dot 1s infinite alternate;"></span>
        <span style="width: 7px; height: 7px; background: #00c8ff; border-radius: 50%; animation: pulse-dot 1s infinite 0.2s alternate;"></span>
        <span style="width: 7px; height: 7px; background: #f59e0b; border-radius: 50%; animation: pulse-dot 1s infinite 0.4s alternate;"></span>
        <span style="font-size: 0.8rem; color: #94a3b8; margin-left: 6px;">Rent Finder AI is thinking...</span>
      </div>
    `;
    messagesContainer.appendChild(indicator);
    scrollChatToBottom();
    return indicator;
  }

  function scrollChatToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendBotWelcomeMessage() {
    appendMessage(
      "Salam! I am **Rent Finder AI**, powered by Google Gemini and our verified Pakistan property database.\n\nAsk me anything! Search rental properties (*'Show flats in Karachi under 50k'*, *'Houses in Lahore DHA'*), or ask general questions (*Science, Programming, Business, Translation*)!",
      'bot'
    );
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Initial welcome message if chat is empty
  if (messagesContainer.children.length === 0) {
    appendBotWelcomeMessage();
  }
}
