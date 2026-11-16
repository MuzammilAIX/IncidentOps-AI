/* IncidentOps-AI Utility Helpers */

function timeAgo(isoString) {
  if (!isoString) return 'N/A';
  const date = new Date(isoString);
  const now = new Date();
  const diff = Math.floor((now - date) / 1000);
  if (diff < 60) return diff + 's ago';
  if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
  if (diff < 604800) return Math.floor(diff / 86400) + 'd ago';
  return date.toLocaleDateString();
}

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function truncate(str, maxLength) {
  if (!str) return '';
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + '...';
}
function severityBadge(severity) {
  const s = (severity || 'low').toLowerCase();
  return '<span class="badge badge-' + s + '">' + escapeHtml(s) + '</span>';
}

function statusBadge(status) {
  const s = (status || 'open').toLowerCase();
  return '<span class="badge badge-' + s + '">' + escapeHtml(s) + '</span>';
}

function showLoading(element) {
  if (element) {
    element.innerHTML = '<div class="loading-overlay"><span class="spinner"></span> Loading...</div>';
  }
}

function showEmpty(element, message) {
  if (element) {
    element.innerHTML = '<div class="empty-state">' +
      '<div class="empty-state-icon">📭</div>' +
      '<div class="empty-state-title">' + escapeHtml(message || 'Nothing here') + '</div>' +
      '</div>';
  }
}

function showToast(message, type) {
  type = type || 'success';
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(function() { toast.remove(); }, 3000);
}

function renderIncidentCard(incident) {
  const aiInfo = incident.ai_root_cause
    ? '<div class="incident-card-ai">🤖 ' + escapeHtml(truncate(incident.ai_root_cause, 100)) + '</div>'
    : '';
  return '<a href="/incident/?id=' + incident.id + '" class="incident-card">' +
    '<div class="incident-card-body">' +
      '<div class="incident-card-title">' + escapeHtml(incident.title) + '</div>' +
      '<div class="incident-card-meta">' +
        severityBadge(incident.severity) +
        statusBadge(incident.status) +
        '<span>' + timeAgo(incident.created_at) + '</span>' +
        (incident.service_name ? '<span>📦 ' + escapeHtml(incident.service_name) + '</span>' : '') +
      '</div>' +
      aiInfo +
    '</div>' +
  '</a>';
}

// ─── URL helpers ───────────────────────────────────────
function getQueryParam(name) {
  const params = new URLSearchParams(window.location.search);
  return params.get(name);
}

// ─── Common helpers ──────────────────────────────────
function escapeHtml(s) {
  if (s == null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const diff = Math.floor((Date.now() - d.getTime()) / 1000);
  if (diff < 60) return diff + 's ago';
  if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
  return Math.floor(diff / 86400) + 'd ago';
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleString();
}

function severityBadge(sev) {
  return '<span class="badge badge-' + escapeHtml(sev) + '">' + escapeHtml(sev) + '</span>';
}

function statusBadge(status) {
  return '<span class="badge badge-' + escapeHtml(status) + '">' + escapeHtml(status) + '</span>';
}

function showToast(msg, type) {
  const el = document.createElement('div');
  el.style.cssText = 'position:fixed;bottom:20px;right:20px;padding:12px 20px;background:' + (type === 'error' ? '#dc2626' : '#10b981') + ';color:white;border-radius:6px;z-index:9999;font-size:14px';
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(function() { el.remove(); }, 3000);
}

function showLoading(container) {
  if (container) container.innerHTML = '<div class="loading-overlay"><span class="spinner"></span> Loading...</div>';
}

function showEmpty(container, msg) {
  if (container) container.innerHTML = '<div class="empty-state"><div class="empty-state-title">' + escapeHtml(msg) + '</div></div>';
}

function renderIncidentCard(inc) {
  const sev = inc.severity || 'medium';
  const st = inc.status || 'open';
  return '<div class="incident-card" onclick="window.location.href=\'/incident/?id=' + inc.id + '\'"><div style="display:flex;justify-content:space-between;margin-bottom:6px"><h3 style="font-size:14px;font-weight:600">' + escapeHtml(inc.title) + '</h3></div><div style="display:flex;gap:6px;flex-wrap:wrap">' + severityBadge(sev) + statusBadge(st) + (inc.service_name ? '<span class="badge" style="background:var(--bg-elevated);color:var(--text-secondary)">' + escapeHtml(inc.service_name) + '</span>' : '') + '</div><div style="font-size:11px;color:var(--text-muted);margin-top:6px">' + timeAgo(inc.created_at) + '</div></div>';
}
