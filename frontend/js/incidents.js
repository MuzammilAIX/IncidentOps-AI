/* IncidentOps-AI - Incidents list page */

(function() {
  let currentPage = 1;
  const pageSize = 20;

  async function init() {
    try {
      const user = await api.me();
      document.getElementById('user-info').innerHTML =
        '<div style="font-size:13px;color:var(--text-primary);font-weight:600">' +
        escapeHtml(user.username) + '</div>';
    } catch (e) {
      return;
    }

    document.getElementById('logout-btn').addEventListener('click', async () => {
      try { await api.logout(); } catch (e) {}
      window.location.href = '/login/';
    });

    document.getElementById('filter-search').addEventListener('input', debounce(resetAndLoad, 300));
    document.getElementById('filter-severity').addEventListener('change', resetAndLoad);
    document.getElementById('filter-status').addEventListener('change', resetAndLoad);
    document.getElementById('clear-filters').addEventListener('click', function() {
      document.getElementById('filter-search').value = '';
      document.getElementById('filter-severity').value = '';
      document.getElementById('filter-status').value = '';
      resetAndLoad();
    });

    await loadIncidents();
  }

  function resetAndLoad() {
    currentPage = 1;
    loadIncidents();
  }
  async function loadIncidents() {
    const container = document.getElementById('incidents-container');
    showLoading(container);
    try {
      const params = { page: currentPage, page_size: pageSize, ordering: '-created_at' };
      const search = document.getElementById('filter-search').value.trim();
      const severity = document.getElementById('filter-severity').value;
      const status = document.getElementById('filter-status').value;
      if (search) params.search = search;
      if (severity) params.severity = severity;
      if (status) params.status = status;

      const data = await api.getIncidents(params);
      document.getElementById('result-count').textContent =
        (data.count || 0) + ' incident' + (data.count === 1 ? '' : 's');

      if (!data.results || data.results.length === 0) {
        showEmpty(container, 'No incidents match your filters');
        document.getElementById('pagination').innerHTML = '';
        return;
      }

      container.innerHTML = data.results.map(renderIncidentCard).join('');
      renderPagination(data);
    } catch (e) {
      console.error('Load failed:', e);
      container.innerHTML = '<div class="empty-state"><div class="empty-state-title">Failed to load incidents</div></div>';
    }
  }

  function renderPagination(data) {
    const container = document.getElementById('pagination');
    container.innerHTML = '';
    if (!data.previous && !data.next) return;
    if (data.previous) {
      const prev = document.createElement('button');
      prev.className = 'btn btn-ghost btn-sm';
      prev.textContent = '\u2190 Previous';
      prev.onclick = function() { currentPage--; loadIncidents(); };
      container.appendChild(prev);
    }
    const info = document.createElement('span');
    info.style.cssText = 'padding:6px 12px;color:var(--text-muted);font-size:13px';
    info.textContent = 'Page ' + currentPage;
    container.appendChild(info);
    if (data.next) {
      const next = document.createElement('button');
      next.className = 'btn btn-ghost btn-sm';
      next.textContent = 'Next \u2192';
      next.onclick = function() { currentPage++; loadIncidents(); };
      container.appendChild(next);
    }
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
