(function () {
  if (window.__assistantWidgetLoaded) return;
  window.__assistantWidgetLoaded = true;

  const CSS = `
  .aw-fab {
    position: fixed; right: 24px; bottom: 24px; width: 56px; height: 56px;
    border-radius: 50%; background: var(--accent, #d4af37); color: #1a1100;
    display: flex; align-items: center; justify-content: center; font-size: 24px;
    cursor: pointer; box-shadow: 0 6px 20px rgba(0,0,0,.35), 0 0 20px rgba(212,175,55,.3);
    z-index: 9998; transition: transform .15s ease;
  }
  .aw-fab:hover { transform: scale(1.06); }
  .aw-overlay {
    position: fixed; right: 24px; bottom: 92px; width: 380px; height: 560px;
    max-height: calc(100vh - 120px); background: var(--bg-elevated, #141414);
    border: 1px solid var(--border, #2a2a2a); border-top: 2px solid var(--accent, #d4af37);
    border-radius: 12px; display: none; flex-direction: column; z-index: 9999;
    overflow: hidden; box-shadow: 0 12px 40px rgba(0,0,0,.6);
  }
  .aw-overlay.open { display: flex; }
  .aw-header { padding: 12px 16px; border-bottom: 1px solid var(--border, #2a2a2a);
    display: flex; justify-content: space-between; align-items: center;
    font-weight: 600; color: var(--accent-hover, #f5d76e); }
  .aw-close { cursor: pointer; opacity: .7; }
  .aw-close:hover { opacity: 1; }
  .aw-messages { flex: 1; overflow-y: auto; padding: 12px; font-size: 14px; color: #f5f5f5; }
  .aw-msg { margin-bottom: 10px; padding: 8px 10px; border-radius: 8px; white-space: pre-wrap; }
  .aw-msg.user { background: rgba(212,175,55,.14); }
  .aw-msg.bot { background: #0a0a0a; }
  .aw-input { display: flex; border-top: 1px solid var(--border, #2a2a2a); align-items: center; }
  .aw-input textarea {
    flex: 1; border: 0; background: transparent; color: inherit; padding: 10px;
    resize: none; font: inherit; outline: none; max-height: 80px;
  }
  .aw-mic {
    border: 0; background: transparent; color: var(--accent, #d4af37);
    padding: 0 10px; cursor: pointer; display: flex; align-items: center;
    justify-content: center; height: 38px; width: 38px;
    transition: opacity .15s;
  }
  .aw-mic:hover { opacity: .8; }
  .aw-mic svg { width: 20px; height: 20px; display: block; }
  .aw-mic.listening { color: #dc2626; animation: aw-pulse 1s infinite ease-in-out; }
  @keyframes aw-pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.15); opacity: .6; }
  }
  .aw-send { border: 0; background: var(--accent, #d4af37); color: #1a1100;
    padding: 0 16px; cursor: pointer; font-weight: 700; height: 100%; }
  .aw-send:disabled { opacity: .5; cursor: not-allowed; }
  `;

  const style = document.createElement("style");
  style.textContent = CSS;
  document.head.appendChild(style);

  const fab = document.createElement("div");
  fab.className = "aw-fab";
  fab.title = "Ask AI Assistant";
  fab.innerHTML = "💬";
  document.body.appendChild(fab);

  // Professional SVG microphone icon (Feather-style)
  const MIC_SVG = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
         stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      <line x1="12" y1="19" x2="12" y2="23"></line>
      <line x1="8" y1="23" x2="16" y2="23"></line>
    </svg>`;

  const overlay = document.createElement("div");
  overlay.className = "aw-overlay";
  overlay.innerHTML = `
    <div class="aw-header">
      <span>💬 AI Assistant</span>
      <span class="aw-close" title="Close">✕</span>
    </div>
    <div class="aw-messages" id="aw-messages">
      <div class="aw-msg bot">Hi! Ask me about incidents, runbooks, or systems.</div>
    </div>
    <div class="aw-input">
      <textarea id="aw-textarea" rows="1" placeholder="Type or use mic... (Enter to send)"></textarea>
      <button class="aw-mic" id="aw-mic" type="button" title="Voice input" aria-label="Voice input">${MIC_SVG}</button>
      <button class="aw-send" id="aw-send" type="button">➤</button>
    </div>
  `;
  document.body.appendChild(overlay);

  const messagesEl = overlay.querySelector("#aw-messages");
  const textarea = overlay.querySelector("#aw-textarea");
  const sendBtn = overlay.querySelector("#aw-send");
  const micBtn = overlay.querySelector("#aw-mic");

  let conversationId = null;
  let busy = false;
  let recognition = null;

  function getCookie(name) {
    const m = document.cookie.match(new RegExp("(^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[2]) : null;
  }

  async function api(path, options) {
    const headers = Object.assign(
      { "Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest" },
      options && options.headers ? options.headers : {}
    );
    const csrf = getCookie("csrftoken");
    if (csrf) headers["X-CSRFToken"] = csrf;
    const token = localStorage.getItem("access_token") || localStorage.getItem("token");
    if (token) headers["Authorization"] = "Bearer " + token;

    const res = await fetch(path, Object.assign({}, options, {
      headers, credentials: "include",
    }));
    const text = await res.text();
    let data;
    try { data = text ? JSON.parse(text) : {}; } catch (e) { data = { raw: text }; }
    if (!res.ok) {
      const msg = data.detail || data.error || ("HTTP " + res.status);
      throw new Error(msg);
    }
    return data;
  }

  function addMessage(role, text) {
    const div = document.createElement("div");
    div.className = "aw-msg " + role;
    div.textContent = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
  }

  async function ensureConversation() {
    if (conversationId) return conversationId;
    const data = await api("/api/assistant/", {
      method: "POST",
      body: JSON.stringify({ title: "Widget chat" }),
    });
    conversationId = data.id;
    return conversationId;
  }

  async function send() {
    if (busy) return;
    const text = textarea.value.trim();
    if (!text) return;
    textarea.value = "";
    addMessage("user", text);

    busy = true;
    sendBtn.disabled = true;
    const pending = addMessage("bot", "…thinking");

    try {
      const cid = await ensureConversation();
      const data = await api("/api/assistant/" + cid + "/send/", {
        method: "POST",
        body: JSON.stringify({ message: text }),
      });
      const am = data.assistant_message || {};
      const content = am.content || "(no response)";
      let summary = content;
      const action = data.action || am.action_taken;
      if (action && action !== "answer" && action !== "none") {
        summary = "🔧 " + action + "\n" + content;
      }
      pending.textContent = summary;
      messagesEl.scrollTop = messagesEl.scrollHeight;
      // NOTE: text-to-speech removed — replies are text-only.
    } catch (e) {
      pending.textContent = "⚠️ " + e.message;
    } finally {
      busy = false;
      sendBtn.disabled = false;
    }
  }

  function setListening(on) {
    if (on) {
      micBtn.classList.add("listening");
      micBtn.title = "Listening... click to stop";
    } else {
      micBtn.classList.remove("listening");
      micBtn.title = "Voice input";
    }
  }

  function initVoice() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      micBtn.style.display = "none";
      return;
    }
    recognition = new SR();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    micBtn.addEventListener("click", () => {
      if (recognition.__listening) {
        recognition.stop();
        return;
      }
      try {
        recognition.start();
        recognition.__listening = true;
        setListening(true);
      } catch (e) {
        console.warn("Voice start failed:", e);
        setListening(false);
      }
    });

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript.trim();
      if (transcript) {
        textarea.value = transcript;
        send();
      }
    };

    recognition.onend = () => {
      recognition.__listening = false;
      setListening(false);
    };

    recognition.onerror = (event) => {
      recognition.__listening = false;
      setListening(false);
      if (event.error === "not-allowed") {
        console.warn("Microphone permission denied");
      }
    };
  }

  initVoice();

  fab.addEventListener("click", () => {
    overlay.classList.toggle("open");
    if (overlay.classList.contains("open")) textarea.focus();
  });
  overlay.querySelector(".aw-close").addEventListener("click", () => overlay.classList.remove("open"));
  sendBtn.addEventListener("click", send);
  textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  });
})();
