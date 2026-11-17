/* IncidentOps-AI - Runbooks browser */
(function() {
  async function init() {
    try {
      const user = await api.me();
      document.getElementById('user-info').innerHTML = '<div style="font-size:13px;color:var(--text-primary);font-weight:600">' + escapeHtml(user.username) + '</div>';
    } catch (e) { return; }

    document.getElementById('logout-btn').addEventListener('click', async () => {
      try { await api.logout(); } catch (e) {}
      window.location.href = '/login/';
    });

    document.getElementById('filter-search').addEventListener('input', debounce(load, 300));
    document.getElementById('filter-category').addEventListener('change', load);

    await load();
  }

  async function load() {
    const container = document.getElementById('runbooks-container');
    showLoading(container);

    const search = document.getElementById('filter-search').value.trim();
    const category = document.getElementById('filter-category').value;

    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (category) params.set('category', category);

    try {
      const resp = await fetch('/api/monitoring/runbooks/?' + params.toString(), { credentials: 'include' });
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      const data = await resp.json();
      document.getElementById('result-count').textContent = data.count + ' runbook' + (data.count === 1 ? '' : 's');

      if (!data.results || data.results.length === 0) {
        showEmpty(container, 'No runbooks match your filters');
        return;
      }

      container.innerHTML = data.results.map(renderRunbook).join('');
    } catch (e) {
      console.error('Load failed:', e);
      container.innerHTML = '<div class="empty-state"><div class="empty-state-title">Failed to load runbooks</div></div>';
    }
  }

  function renderRunbook(rb) {
    const keywordBadges = (rb.keywords || []).map(function(k) {
      return '<span class="badge" style="background:var(--bg-elevated);color:var(--text-secondary);font-size:10px">' + escapeHtml(k) + '</span>';
    }).join(' ');

    return '<div class="card" style="margin-bottom:12px;border-left:4px solid var(--accent)">' +
      '<div class="card-header">' +
        '<div>' +
          '<div style="font-size:15px;font-weight:600;margin-bottom:4px">' +
            '<code style="background:var(--accent-bg);color:var(--accent-hover);padding:3px 8px;border-radius:4px;font-size:12px;margin-right:8px">' + escapeHtml(rb.code) + '</code>' +
            escapeHtml(rb.title) +
          '</div>' +
          '<div style="font-size:11px;color:var(--text-muted)">' +
            'Category: ' + escapeHtml(rb.category) +
            (rb.service_hint ? ' - Service: ' + escapeHtml(rb.service_hint) : '') +
          '</div>' +
        '</div>' +
      '</div>' +
      (keywordBadges ? '<div style="margin:8px 0;display:flex;gap:4px;flex-wrap:wrap">' + keywordBadges + '</div>' : '') +
      '<div style="margin-top:8px;padding:10px;background:var(--bg-primary);border-radius:6px;font-size:12px;color:var(--text-secondary);line-height:1.6;white-space:pre-wrap">' +
        escapeHtml(rb.content) +
      '</div>' +
    '</div>';
  }

  function debounce(fn, delay) {
    let timer;
    return function() {
      clearTimeout(timer);
      timer = setTimeout(fn, delay);
    };
  }

  init();
})();