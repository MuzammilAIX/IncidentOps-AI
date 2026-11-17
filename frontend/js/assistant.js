/* IncidentOps-AI Assistant chat */

(function() {
  let currentConversationId = null;

  async function init() {
    try {
      const user = await api.me();
    } catch (e) { window.location.href = '/login/'; return; }

    document.getElementById('new-chat-btn').addEventListener('click', newChat);
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    document.getElementById('chat-input').addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    document.querySelectorAll('.example-q').forEach(function(el) {
      el.addEventListener('click', function() {
        document.getElementById('chat-input').value = el.getAttribute('data-q');
        document.getElementById('chat-input').focus();
      });
    });

    await loadConversations();
  }

  async function loadConversations() {
    try {
      const resp = await fetch('/api/assistant/', { credentials: 'include' });
      if (!resp.ok) return;
      const data = await resp.json();
      const list = document.getElementById('conversation-list');
      list.innerHTML = '';
      const conversations = data.results || data || [];
      conversations.forEach(function(c) {
        const div = document.createElement('div');
        div.className = 'conv-item' + (c.id === currentConversationId ? ' active' : '');
        div.innerHTML = '<div class="conv-item-title">' + escapeHtml(c.title || 'Untitled') + '</div><div class="conv-item-meta">' + (c.message_count || 0) + ' messages</div>';
        div.addEventListener('click', function() { loadConversation(c.id); });
        list.appendChild(div);
      });
    } catch (e) { console.error(e); }
  }

  async function newChat() {
    try {
      const resp = await fetch('/api/assistant/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ title: 'New conversation' })
      });
      const data = await resp.json();
      currentConversationId = data.id;
      document.getElementById('chat-messages').innerHTML = '<div class="empty-chat"><h2>New conversation</h2><p>Type a message to get started.</p></div>';
      document.getElementById('chat-title').textContent = '[?] ' + (data.title || 'New chat');
      await loadConversations();
    } catch (e) { console.error(e); }
  }

  async function loadConversation(id) {
    currentConversationId = id;
    try {
      const resp = await fetch('/api/assistant/' + id + '/', { credentials: 'include' });
      const conv = await resp.json();
      document.getElementById('chat-title').textContent = '[?] ' + (conv.title || 'Chat');
      const messages = document.getElementById('chat-messages');
      messages.innerHTML = '';
      (conv.messages || []).forEach(function(m) {
        renderMessage(m.role, m.content, m.action_taken, m.action_result);
      });
      scrollBottom();
      await loadConversations();
    } catch (e) { console.error(e); }
  }

  async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    if (!currentConversationId) {
      await newChat();
    }

    input.value = '';
    renderMessage('user', message);
    showTyping();

    try {
      const resp = await fetch('/api/assistant/' + currentConversationId + '/send/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify({ message: message })
      });
      hideTyping();
      const data = await resp.json();
      if (data.assistant_message) {
        renderMessage('assistant', data.assistant_message.content, data.assistant_message.action_taken, data.assistant_message.action_result);
      }
      scrollBottom();
      await loadConversations();
    } catch (e) {
      hideTyping();
      renderMessage('assistant', 'Error: ' + e.message);
    }
  }

  function renderMessage(role, content, actionTaken, actionResult) {
    const messages = document.getElementById('chat-messages');
    const emptyState = messages.querySelector('.empty-chat');
    if (emptyState) emptyState.remove();

    const div = document.createElement('div');
    div.className = 'chat-message ' + role;

    let html = '';
    if (role === 'assistant' && actionTaken) {
      const labels = {create_incident: 'Incident Created', search_runbooks: 'Runbooks Found', search_incidents: 'Incidents Found', answer: 'Answer'};
      html += '<div class="action-badge">' + (labels[actionTaken] || actionTaken) + '</div>';
    }
    html += escapeHtml(content || '');

    if (actionResult) {
      if (actionTaken === 'create_incident' && actionResult.incident_id) {
        html += '<div><a class="incident-link" href="/incident/?id=' + actionResult.incident_id + '">View incident #' + actionResult.incident_id + ' -></a></div>';
      } else if (actionTaken === 'search_runbooks' && actionResult.runbooks) {
        actionResult.runbooks.forEach(function(r) {
          html += '<div class="runbook-item"><code>' + escapeHtml(r.code) + '</code> ' + escapeHtml(r.title) + '</div>';
        });
      } else if (actionTaken === 'search_incidents' && actionResult.incidents) {
        actionResult.incidents.forEach(function(i) {
          html += '<div class="incident-item"><a href="/incident/?id=' + i.id + '" style="color:var(--accent)">#' + i.id + '</a> ' + escapeHtml(i.title) + ' <span class="badge">' + escapeHtml(i.severity) + '</span></div>';
        });
      }
    }

    div.innerHTML = html;
    messages.appendChild(div);
  }

  function showTyping() {
    const messages = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'chat-message assistant typing-indicator-wrapper';
    div.id = 'typing-indicator';
    div.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    messages.appendChild(div);
    scrollBottom();
  }

  function hideTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
  }

  function scrollBottom() {
    const el = document.getElementById('chat-messages');
    el.scrollTop = el.scrollHeight;
  }

  init();
})();
