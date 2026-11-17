/* IncidentOps-AI - Approvals Queue */

(function() {
  async function init() {
    try {
      const user = await api.me();
      document.getElementById('user-info').innerHTML =
        '<div style="font-size:13px;color:var(--text-primary);font-weight:600">' +
        escapeHtml(user.username) + '</div>';
    } catch (e) { return; }

    document.getElementById('logout-btn').addEventListener('click', async () => {
      try { await api.logout(); } catch (e) {}
      window.location.href = '/login/';
    });

    document.getElementById('filter-status').addEventListener('change', loadApprovals);

    await loadApprovals();
    setInterval(loadApprovals, 10000);
  }

  async function loadApprovals() {
    const container = document.getElementById('approvals-container');
    showLoading(container);
    try {
      const status = document.getElementById('filter-status').value;
      const params = { page_size: 50 };
      if (status) params.status = status;

      const data = await api.getApprovals(params);
      document.getElementById('result-count').textContent =
        (data.count || 0) + ' approval' + (data.count === 1 ? '' : 's');

      if (!data.results || data.results.length === 0) {
        showEmpty(container, 'No approvals to show');
        return;
      }

      container.innerHTML = data.results.map(renderApproval).join('');
      wireButtons();
    } catch (e) {
      console.error('Load failed:', e);
      container.innerHTML = '<div class="empty-state"><div class="empty-state-title">Failed to load</div></div>';
    }
  }

  function renderApproval(a) {
    const actions = a.proposed_actions || [];
    let actionsHtml = '';
    actions.forEach(function(action, i) {
      actionsHtml += '<div style="padding:12px;background:var(--bg-elevated);border-radius:8px;margin-bottom:8px">' +
        '<div style="font-weight:600;margin-bottom:4px">Option ' + (i + 1) + ' ' +
          (action.risk ? '<span class="badge badge-' + escapeHtml(action.risk) + '">' + escapeHtml(action.risk) + '</span>' : '') +
        '</div>' +
        '<div style="font-size:13px"><strong>' + escapeHtml(action.action || '') + '</strong> on <code>' + escapeHtml(action.target || '') + '</code></div>' +
        (action.reason ? '<div style="font-size:12px;color:var(--text-secondary);margin-top:4px">' + escapeHtml(action.reason) + '</div>' : '') +
      '</div>';
    });

    let buttonsHtml = '';
    if (a.status === 'pending') {
      buttonsHtml = '<div style="display:flex;gap:8px;margin-top:12px">' +
        '<button class="btn btn-success btn-sm approve-btn" data-id="' + a.id + '">Approve</button>' +
        '<button class="btn btn-danger btn-sm reject-btn" data-id="' + a.id + '">Reject</button>' +
      '</div>';
    } else {
      buttonsHtml = '<div style="margin-top:12px;font-size:12px;color:var(--text-muted)">' +
        'Decision: <strong>' + escapeHtml(a.status) + '</strong>' +
        (a.decided_by_username ? ' by ' + escapeHtml(a.decided_by_username) : '') +
      '</div>';
    }

    return '<div class="card" style="margin-bottom:12px">' +
      '<div class="card-header">' +
        '<div>' +
          '<div style="font-size:14px;font-weight:600">' + escapeHtml(a.incident_title || 'Incident') + '</div>' +
          '<div style="font-size:12px;color:var(--text-muted)">Investigation #' + escapeHtml(String(a.investigation)) + ' - ' + timeAgo(a.created_at) + '</div>' +
        '</div>' +
        '<span class="badge badge-' + escapeHtml(a.status) + '">' + escapeHtml(a.status) + '</span>' +
      '</div>' +
      actionsHtml +
      buttonsHtml +
    '</div>';
  }

  function wireButtons() {
    document.querySelectorAll('.approve-btn').forEach(function(btn) {
      btn.addEventListener('click', async function() {
        btn.disabled = true;
        try {
          await api.approveApproval(btn.dataset.id);
          showToast('Approved', 'success');
          setTimeout(loadApprovals, 500);
        } catch (e) {
          showToast('Failed: ' + e.message, 'error');
          btn.disabled = false;
        }
      });
    });

    document.querySelectorAll('.reject-btn').forEach(function(btn) {
      btn.addEventListener('click', async function() {
        btn.disabled = true;
        try {
          await api.rejectApproval(btn.dataset.id);
          showToast('Rejected', 'success');
          setTimeout(loadApprovals, 500);
        } catch (e) {
          showToast('Failed: ' + e.message, 'error');
          btn.disabled = false;
        }
      });
    });
  }

  init();
})();
