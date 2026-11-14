/* IncidentOps-AI API Client */

function getCookie(name) {
  const value = '; ' + document.cookie;
  const parts = value.split('; ' + name + '=');
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

const api = {
  async _fetch(url, options = {}) {
    options.credentials = 'include';
    options.headers = options.headers || {};

    if (options.method && options.method !== 'GET') {
      options.headers['Content-Type'] = 'application/json';
      const csrf = getCookie('csrftoken');
      if (csrf) options.headers['X-CSRFToken'] = csrf;
    }

    const response = await fetch(url, options);

    if (response.status === 401 || response.status === 403) {
      if (!window.location.pathname.startsWith('/login/')) {
        window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
      }
      throw new Error('Not authenticated');
    }

    if (!response.ok) {
      const text = await response.text();
      throw new Error('HTTP ' + response.status + ': ' + text.slice(0, 200));
    }

    if (response.status === 204) return null;
    return response.json();
  },

  async get(url) {
    return this._fetch(url, { method: 'GET' });
  },

  async post(url, data) {
    return this._fetch(url, { method: 'POST', body: JSON.stringify(data) });
  },

  async patch(url, data) {
    return this._fetch(url, { method: 'PATCH', body: JSON.stringify(data) });
  },

  async delete(url) {
    return this._fetch(url, { method: 'DELETE' });
  },

  // ─── Auth ──────────────────────────────
  async login(username, password) {
    return this.post('/api/auth/login/', { username, password });
  },

  async logout() {
    return this.post('/api/auth/logout/', {});
  },

  async me() {
    return this.get('/api/auth/me/');
  },

  // ─── Incidents ─────────────────────────
  async getIncidents(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.get('/api/incidents/' + (qs ? '?' + qs : ''));
  },

  async getIncident(id) {
    return this.get('/api/incidents/' + id + '/');
  },

  async createIncident(data) {
    return this.post('/api/incidents/', data);
  },

  async updateIncident(id, data) {
    return this.patch('/api/incidents/' + id + '/', data);
  },

  // ─── Investigations ────────────────────
  async getInvestigations(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.get('/api/investigations/' + (qs ? '?' + qs : ''));
  },

  async getInvestigation(id) {
    return this.get('/api/investigations/' + id + '/');
  },

  // ─── Approvals ─────────────────────────
  async getApprovals(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.get('/api/approvals/' + (qs ? '?' + qs : ''));
  },

  async getApproval(id) {
    return this.get('/api/approvals/' + id + '/');
  },

  async approveApproval(id) {
    return this.post('/api/approvals/' + id + '/approve/', {});
  },

  async rejectApproval(id) {
    return this.post('/api/approvals/' + id + '/reject/', {});
  },
};

window.api = api;
