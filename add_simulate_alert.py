"""Add Simulate Alert form to dashboard."""

# 1. Add form to index.html (before </body>)
path = '/app/frontend/index.html'
content = open(path).read()

if 'simulate-alert-form' not in content:
    form = '''
  <div class="card" id="simulate-alert-form" style="margin-bottom:16px;border-left:4px solid #f59e0b">
    <div class="card-header">
      <h2 class="card-title">\\U0001F9EA Simulate Alert</h2>
      <span class="badge" style="background:rgba(245,158,11,0.15);color:#f59e0b">Demo</span>
    </div>
    <div style="font-size:12px;color:var(--text-muted);margin-bottom:12px">Trigger an incident like Prometheus / Grafana / Datadog would. The AI investigates automatically.</div>
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px">
      <div style="flex:1;min-width:180px">
        <label style="display:block;font-size:12px;color:var(--text-muted);margin-bottom:4px">Service</label>
        <select id="sim-service" class="form-select" style="width:100%">
          <option value="">Unknown</option>
        </select>
      </div>
      <div style="flex:1;min-width:120px">
        <label style="display:block;font-size:12px;color:var(--text-muted);margin-bottom:4px">Severity</label>
        <select id="sim-severity" class="form-select" style="width:100%">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>
      <div style="flex:2;min-width:200px">
        <label style="display:block;font-size:12px;color:var(--text-muted);margin-bottom:4px">Alert name</label>
        <input type="text" id="sim-name" class="form-input" placeholder="HighErrorRate" style="width:100%" value="HighErrorRate">
      </div>
      <div style="flex:1;min-width:120px">
        <label style="display:block;font-size:12px;color:var(--text-muted);margin-bottom:4px">&nbsp;</label>
        <button class="btn btn-primary" id="sim-submit" style="width:100%">Send Alert</button>
      </div>
    </div>
    <div id="sim-result" style="font-size:12px;color:var(--text-muted)"></div>
  </div>
'''
    # Insert before the closing </main> tag
    content = content.replace('</main>', form + '\n    </main>', 1)
    open(path, 'w').write(content)
    print('index.html: Added Simulate Alert form')
else:
    print('index.html: Already has form')

# 2. Add logic to dashboard.js
path = '/app/frontend/js/dashboard.js'
content = open(path).read()

if 'sim-submit' not in content:
    # Add handler setup inside init() after loading
    old = "    await refresh();\n    setInterval(refresh, 10000);"
    new = """    // Simulate alert handler
    var simBtn = document.getElementById('sim-submit');
    if (simBtn) {
      simBtn.addEventListener('click', sendSimulatedAlert);
      // Load services for dropdown
      try {
        const services = await api.get('/api/services/');
        const sel = document.getElementById('sim-service');
        (services.results || []).forEach(function(s) {
          const opt = document.createElement('option');
          opt.value = s.name;
          opt.textContent = s.name;
          sel.appendChild(opt);
        });
      } catch (e) {}
    }

""" + old
    content = content.replace(old, new, 1)
    
    # Add the sendSimulatedAlert function
    send_func = """
  async function sendSimulatedAlert() {
    var service = document.getElementById('sim-service').value;
    var severity = document.getElementById('sim-severity').value;
    var name = document.getElementById('sim-name').value.trim() || 'HighErrorRate';
    var resultEl = document.getElementById('sim-result');
    var btn = document.getElementById('sim-submit');
    btn.disabled = true;
    btn.textContent = 'Sending...';
    resultEl.textContent = '';
    try {
      var resp = await fetch('/api/monitoring/webhooks/generic/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service: service,
          severity: severity,
          name: name,
          description: 'Simulated alert from dashboard',
          type: 'simulated_alert'
        })
      });
      var data = await resp.json();
      if (resp.ok) {
        resultEl.innerHTML = '<span style="color:#10b981">\\u2705 Incident #' + data.incident_id + ' created' + (data.investigation_triggered ? ', investigation queued' : '') + '</span>';
        showToast('Alert sent. Investigation running...', 'success');
        setTimeout(refresh, 3000);
      } else {
        throw new Error(data.error || 'Failed');
      }
    } catch (e) {
      resultEl.innerHTML = '<span style="color:#ef4444">\\u274C ' + e.message + '</span>';
    } finally {
      btn.disabled = false;
      btn.textContent = 'Send Alert';
    }
  }

"""
    content = content.replace('  async function init() {', send_func + '  async function init() {', 1)
    open(path, 'w').write(content)
    print('dashboard.js: Added handler')
else:
    print('dashboard.js: Already has handler')

print('\\nDone')
