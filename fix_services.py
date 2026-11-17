"""Replace /api/services/ with hardcoded fallback."""
path = '/app/frontend/js/dashboard.js'
content = open(path).read()

old = """      // Load services for dropdown
      try {
        const services = await api.get('/api/services/');
        const sel = document.getElementById('sim-service');
        (services.results || []).forEach(function(s) {
          const opt = document.createElement('option');
          opt.value = s.name;
          opt.textContent = s.name;
          sel.appendChild(opt);
        });
      } catch (e) {}"""

new = """      // Load services for dropdown (hardcoded)
      const sel = document.getElementById('sim-service');
      ['payment-service', 'api-gateway', 'auth-service', 'notification-worker'].forEach(function(name) {
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name;
        sel.appendChild(opt);
      });"""

if old in content:
    content = content.replace(old, new, 1)
    open(path, 'w').write(content)
    print('Fixed')
else:
    print('Pattern not found')
