/* IncidentOps-AI Dashboard */

(function() {
  function redirectToLogin() {
    if (!window.location.pathname.startsWith('/login/')) {
      window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
    }
  }

  async function init() {
    try {
      const user = await api.me();
      document.getElementById('user-info').innerHTML =
        '<div style="font-size:13px;color:var(--text-primary);font-weight:600">' +
        escapeHtml(user.username) + '</div>' +
        '<div style="font-size:11px;color:var(--text-muted)">Signed in</div>';
    } catch (e) {
      if (e.status === 401 || e.status === 403) { redirectToLogin(); return; }
      console.warn('Not authenticated:', e);
      return;
    }

    document.getElementById('logout-btn').addEventListener('click', async () => {
      try { await api.logout(); } catch (e) { /* ignore */ }
      window.location.href = '/login/';
    });

    await refresh();
    setInterval(refresh, 10000);
  }
  async function refresh() {
    try {
      await Promise.all([loadStats(), loadIncidents(), loadApprovals()]);
      document.getElementById('last-updated').textContent =
        'Updated ' + new Date().toLocaleTimeString();
    } catch (e) {
      if (e.status === 401 || e.status === 403) { redirectToLogin(); return; }
      console.error('Refresh failed:', e);
    }
  }

  async function loadStats() {
    try {
      const [all, open, pending] = await Promise.all([
        api.getIncidents({ page_size: 100 }),
        api.getIncidents({ status: 'open', page_size: 100 }),
        api.getApprovals({ status: 'pending', page_size: 100 }),
      ]);
      document.getElementById('stat-total').textContent = all.count || 0;
      document.getElementById('stat-active').textContent = open.count || 0;
      document.getElementById('stat-pending').textContent = pending.count || 0;
      document.getElementById('stat-investigating').textContent = '-';
    } catch (e) {
      if (e.status === 401 || e.status === 403) throw e;
      console.error('Stats failed:', e);
    }
  }

  async function loadIncidents() {
    const container = document.getElementById('incidents-list');
    if (!container) return;
    try {
      const data = await api.getIncidents({ page_size: 5, ordering: '-created_at' });
      if (!data.results || data.results.length === 0) {
        showEmpty(container, 'No incidents yet');
        return;
      }
      container.innerHTML = data.results.map(renderIncidentCard).join('');
    } catch (e) {
      if (e.status === 401 || e.status === 403) throw e;
      console.error('Incidents failed:', e);
      container.innerHTML = '<div class="empty-state"><div class="empty-state-title">Failed to load</div></div>';
    }
  }

  async function loadApprovals() {
    const container = document.getElementById('approvals-list');
    if (!container) return;
    try {
      const data = await api.getApprovals({ status: 'pending', page_size: 5 });
      if (!data.results || data.results.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-state-title">No pending approvals</div></div>';
        return;
      }
      container.innerHTML = data.results.map(function(a) {
        const actions = a.proposed_actions || [];
        const text = actions.length > 0 ? actions.map(function(x) { return x.action; }).join(', ') : 'No actions';
        return '<div style="padding:12px;background:var(--bg-elevated);border-radius:8px;margin-bottom:8px">' +
          '<div style="font-size:13px;font-weight:600;margin-bottom:6px">' + escapeHtml(text) + '</div>' +
          '<div style="font-size:11px;color:var(--text-muted);margin-bottom:8px">Investigation #' + escapeHtml(String(a.investigation)) + '</div>' +
          '<a href="/approvals/" class="btn btn-success btn-sm">Review</a>' +
          '</div>';
      }).join('');
    } catch (e) {
      if (e.status === 401 || e.status === 403) throw e;
      console.error('Approvals failed:', e);
    }
  }

  init();
})();
