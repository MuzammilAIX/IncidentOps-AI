"""Build AI Assistant chat UI."""

# ═══════════════════════════════════════════════════════════════
# 1. Create frontend/assistant.html
# ═══════════════════════════════════════════════════════════════
assistant_html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Assistant - IncidentOps-AI</title>
  <link rel="stylesheet" href="/static/css/styles.css">
  <style>
    .assistant-layout { display: grid; grid-template-columns: 260px 1fr; height: calc(100vh - 0px); }
    .assistant-sidebar { background: var(--bg-elevated); border-right: 1px solid var(--border); display: flex; flex-direction: column; }
    .assistant-sidebar-header { padding: 16px; border-bottom: 1px solid var(--border); }
    .assistant-sidebar-header button { width: 100%; }
    .conversation-list { flex: 1; overflow-y: auto; padding: 8px; }
    .conv-item { padding: 10px 12px; border-radius: 6px; cursor: pointer; margin-bottom: 4px; font-size: 13px; color: var(--text-secondary); }
    .conv-item:hover { background: var(--bg-primary); }
    .conv-item.active { background: var(--accent-bg); color: var(--accent-hover); font-weight: 600; }
    .conv-item-title { font-weight: 600; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .conv-item-meta { font-size: 11px; color: var(--text-muted); }
    .chat-main { display: flex; flex-direction: column; height: 100vh; }
    .chat-header { padding: 16px 24px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
    .chat-header h1 { font-size: 18px; font-weight: 600; }
    .chat-messages { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
    .chat-message { max-width: 80%; padding: 12px 16px; border-radius: 12px; line-height: 1.5; font-size: 14px; }
    .chat-message.user { align-self: flex-end; background: var(--accent); color: white; }
    .chat-message.assistant { align-self: flex-start; background: var(--bg-elevated); color: var(--text-primary); border: 1px solid var(--border); }
    .chat-message.assistant .action-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-bottom: 8px; background: var(--accent-bg); color: var(--accent-hover); }
    .chat-message .incident-link { display: inline-block; margin-top: 8px; padding: 6px 12px; background: var(--accent); color: white; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 600; }
    .chat-message .runbook-item { padding: 8px 12px; background: var(--bg-primary); border-radius: 6px; margin-top: 6px; font-size: 12px; }
    .chat-message .incident-item { padding: 8px 12px; background: var(--bg-primary); border-radius: 6px; margin-top: 6px; font-size: 12px; }
    .chat-input-area { padding: 16px 24px; border-top: 1px solid var(--border); display: flex; gap: 12px; }
    .chat-input-area textarea { flex: 1; min-height: 44px; max-height: 120px; padding: 12px; background: var(--bg-elevated); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-family: inherit; font-size: 14px; resize: none; }
    .chat-input-area button { padding: 0 20px; }
    .typing-indicator { display: flex; gap: 4px; padding: 12px 16px; }
    .typing-indicator span { width: 8px; height: 8px; background: var(--text-muted); border-radius: 50%; animation: typing 1.4s infinite; }
    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typing { 0%, 60%, 100% { transform: translateY(0); opacity: 0.5; } 30% { transform: translateY(-8px); opacity: 1; } }
    .empty-chat { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--text-muted); }
    .empty-chat h2 { font-size: 24px; margin-bottom: 12px; color: var(--text-primary); }
    .empty-chat p { font-size: 14px; max-width: 400px; text-align: center; line-height: 1.6; }
    .empty-chat .example-questions { margin-top: 24px; display: flex; flex-direction: column; gap: 8px; }
    .empty-chat .example-q { padding: 10px 16px; background: var(--bg-elevated); border-radius: 8px; cursor: pointer; font-size: 13px; text-align: left; }
    .empty-chat .example-q:hover { background: var(--accent-bg); }
  </style>
</head>
<body>
  <div class="assistant-layout">
    <aside class="assistant-sidebar">
      <div class="sidebar-logo" style="padding:16px;border-bottom:1px solid var(--border)">
        <div class="sidebar-logo-icon">🚨</div>
        <span>IncidentOps-AI</span>
      </div>
      <div class="assistant-sidebar-header">
        <button class="btn btn-primary" id="new-chat-btn">+ New Chat</button>
      </div>
      <div class="conversation-list" id="conversation-list"></div>
      <div style="padding:12px;border-top:1px solid var(--border)">
        <a href="/" class="btn btn-ghost btn-sm" style="width:100%;text-align:center">← Back to Dashboard</a>
      </div>
    </aside>
    <div class="chat-main">
      <header class="chat-header">
        <h1 id="chat-title">💬 AI Assistant</h1>
        <span id="last-updated" style="font-size:12px;color:var(--text-muted)"></span>
      </header>
      <main class="chat-messages" id="chat-messages">
        <div class="empty-chat">
          <h2>How can I help?</h2>
          <p>Describe a problem, ask about runbooks, or search past incidents.</p>
          <div class="example-questions">
            <div class="example-q" data-q="Payment API returning 500 errors">"Payment API returning 500 errors"</div>
            <div class="example-q" data-q="What's the runbook for payment errors?">"What's the runbook for payment errors?"</div>
            <div class="example-q" data-q="Have we seen payment issues before?">"Have we seen payment issues before?"</div>
            <div class="example-q" data-q="What is IncidentOps-AI?">"What is IncidentOps-AI?"</div>
          </div>
        </div>
      </main>
      <div class="chat-input-area">
        <textarea id="chat-input" placeholder="Type a message... (Enter to send, Shift+Enter for newline)"></textarea>
        <button class="btn btn-primary" id="send-btn">Send ▶</button>
      </div>
    </div>
  </div>
  <script src="/static/js/api.js?v=18"></script>
  <script src="/static/js/utils.js?v=18"></script>
  <script src="/static/js/assistant.js?v=18"></script>
</body>
</html>
'''
path = '/app/frontend/assistant.html'
open(path, 'w').write(assistant_html)
print('Created assistant.html')

# ═══════════════════════════════════════════════════════════════
# 2. Create frontend/js/assistant.js
# ═══════════════════════════════════════════════════════════════
assistant_js = '''/* IncidentOps-AI Assistant chat */

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
      document.getElementById('chat-title').textContent = '💬 ' + (data.title || 'New chat');
      await loadConversations();
    } catch (e) { console.error(e); }
  }

  async function loadConversation(id) {
    currentConversationId = id;
    try {
      const resp = await fetch('/api/assistant/' + id + '/', { credentials: 'include' });
      const conv = await resp.json();
      document.getElementById('chat-title').textContent = '💬 ' + (conv.title || 'Chat');
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
        html += '<div><a class="incident-link" href="/incident/?id=' + actionResult.incident_id + '">View incident #' + actionResult.incident_id + ' →</a></div>';
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
'''
path = '/app/frontend/js/assistant.js'
open(path, 'w').write(assistant_js)
print('Created assistant.js')

# ═══════════════════════════════════════════════════════════════
# 3. Add URL route in config/urls.py
# ═══════════════════════════════════════════════════════════════
path = '/app/config/urls.py'
content = open(path).read()
if '/assistant/' not in content or 'template_name="assistant.html"' not in content:
    old = 'path("runbooks/", TemplateView.as_view(template_name="runbooks.html"), name="runbooks"),'
    new = old + '\n    path("assistant/", TemplateView.as_view(template_name="assistant.html"), name="assistant"),'
    if old in content:
        content = content.replace(old, new, 1)
        open(path, 'w').write(content)
        print('Added /assistant/ URL route')
    else:
        print('ERROR: Could not find runbooks route to insert after')
else:
    print('Already has /assistant/ route')

# ═══════════════════════════════════════════════════════════════
# 4. Add sidebar link to all HTML files (except login, runbooks, assistant)
# ═══════════════════════════════════════════════════════════════
import glob
for path in glob.glob('/app/frontend/*.html'):
    if 'login.html' in path or 'assistant.html' in path:
        continue
    content = open(path).read()
    if 'href="/assistant/"' in content:
        continue
    # Add after Incidents link (or before Runbooks)
    old = '<a href="/runbooks/" class="nav-item'
    if old in content:
        new = '''<a href="/assistant/" class="nav-item">
          <span class="nav-item-icon">💬</span>
          <span>Assistant</span>
        </a>
        ''' + old
        content = content.replace(old, new, 1)
        open(path, 'w').write(content)
        print('Added sidebar to:', path)

print('\\nDone')
