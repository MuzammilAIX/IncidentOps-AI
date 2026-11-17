"""Add Create Incident + Trigger Investigation + Simulate Alert UI."""
import re

# ═══════════════════════════════════════════════════════════════
# 1. Add "Create Incident" button to incidents.html
# ═══════════════════════════════════════════════════════════════
path = '/app/frontend/incidents.html'
content = open(path).read()

if 'create-incident-btn' not in content:
    # Find the header-actions div
    old = '<div class="header-actions">\n          <span id="result-count"'
    new = '<div class="header-actions">\n          <button class="btn btn-primary" id="create-incident-btn">+ Create Incident</button>\n          <span id="result-count"'
    content = content.replace(old, new, 1)
    
    # Add modal HTML before </body>
    modal = '''
  <!-- Create Incident Modal -->
  <div id="create-incident-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:1000;align-items:center;justify-content:center">
    <div style="background:var(--bg-elevated);border-radius:12px;padding:24px;max-width:500px;width:90%;border:1px solid var(--border)">
      <h2 style="font-size:20px;font-weight:600;margin-bottom:16px">Create New Incident</h2>
      <div style="margin-bottom:12px">
        <label style="display:block;font-size:12px;color:var(--text-muted);margin-bottom:4px">Title</label>
        <input type="text" id="inc-title" class="form-input" placeholder="e.g. Database returning timeout errors" style="width:100%">
      </div>
      <div style="margin-bottom:12px">
        <label style="display:block;font-size:12px;color:var(--text-muted);margin-bottom:4px">Description</label>
        <textarea id="inc-description" class="form-input" placeholder="Details..." style="width:100%;min-height:60px"></textarea>
      </div>
      <div style="display:flex;gap:12px;margin-bottom:16px">
        <div style="flex:1">
          <label style="display:block;font-size:12px;color:var(--text-muted);margin-bottom:4px">Severity</label>
          <select id="inc-severity" class="form-select" style="width:100%">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <div style="flex:1">
          <label style="display:block;font-size:12px;color:var(--text-muted);margin-bottom:4px">Service</label>
          <select id="inc-service" class="form-select" style="width:100%">
            <option value="">None</option>
          </select>
        </div>
      </div>
      <div style="display:flex;gap:8px;justify-content:flex-end">
        <button class="btn btn-ghost" id="cancel-incident">Cancel</button>
        <button class="btn btn-primary" id="submit-incident">Create + Investigate</button>
      </div>
    </div>
  </div>
'''
    content = content.replace('</body>', modal + '</body>', 1)
    open(path, 'w').write(content)
    print('incidents.html: Added Create button + modal')
else:
    print('incidents.html: Already has button')

# ═══════════════════════════════════════════════════════════════
# 2. Add "Create Incident" logic to incidents.js
# ═══════════════════════════════════════════════════════════════
path = '/app/frontend/js/incidents.js'
content = open(path).read()

if 'create-incident-btn' not in content:
    # Add handler inside init() after logout-btn
    old = "    document.getElementById('logout-btn').addEventListener('click', async () => {\n      try { await api.logout(); } catch (e) {}\n      window.location.href = '/login/';\n    });"
    new = old + """

    // Create incident button
    document.getElementById('create-incident-btn').addEventListener('click', openCreateModal);
    document.getElementById('cancel-incident').addEventListener('click', closeCreateModal);
    document.getElementById('submit-incident').addEventListener('click', submitCreateIncident);

    // Load services for dropdown
    try {
      const services = await api.get('/api/services/');
      const sel = document.getElementById('inc-service');
      (services.results || []).forEach(function(s) {
        const opt = document.createElement('option');
        opt.value = s.id;
        opt.textContent = s.name;
        sel.appendChild(opt);
      });
    } catch (e) {}
"""
    content = content.replace(old, new, 1)
    
    # Add modal functions before the final init() call
    modal_funcs = """
  function openCreateModal() {
    document.getElementById('create-incident-modal').style.display = 'flex';
    document.getElementById('inc-title').focus();
  }
  function closeCreateModal() {
    document.getElementById('create-incident-modal').style.display = 'none';
    document.getElementById('inc-title').value = '';
    document.getElementById('inc-description').value = '';
  }
  async function submitCreateIncident() {
    const title = document.getElementById('inc-title').value.trim();
    if (!title) { showToast('Title is required', 'error'); return; }
    const data = {
      title: title,
      description: document.getElementById('inc-description').value.trim(),
      severity: document.getElementById('inc-severity').value,
      service: document.getElementById('inc-service').value || null,
    };
    try {
      await api.post('/api/incidents/', data);
      showToast('Incident created. Investigation running...', 'success');
      closeCreateModal();
      setTimeout(resetAndLoad, 1500);
    } catch (e) {
      showToast('Failed: ' + e.message, 'error');
    }
  }

"""
    content = content.replace('  init();', modal_funcs + '  init();', 1)
    open(path, 'w').write(content)
    print('incidents.js: Added Create logic')
else:
    print('incidents.js: Already has logic')

# ═══════════════════════════════════════════════════════════════
# 3. Add "Trigger Investigation" button to incident.js (when no investigation)
# ═══════════════════════════════════════════════════════════════
path = '/app/frontend/js/incident.js'
content = open(path).read()

if 'trigger-investigation-btn' not in content:
    # Replace the empty state with a button
    old = """    } else { html += '<div class="card" style="margin-bottom:16px"><div class="empty-state"><div class="empty-state-title">No investigation yet</div></div></div>'; }"""
    new = """    } else { html += '<div class="card" style="margin-bottom:16px"><div class="empty-state"><div class="empty-state-title">No investigation yet</div><button class="btn btn-primary" id="trigger-investigation-btn" style="margin-top:12px">\\U0001F504 Trigger AI Investigation</button></div></div>'; }"""
    content = content.replace(old, new, 1)
    
    # Add click handler
    old_btns = """    const approveBtn = document.getElementById('approve-btn');
    const rejectBtn = document.getElementById('reject-btn');"""
    new_btns = """    var triggerBtn = document.getElementById('trigger-investigation-btn');
    if (triggerBtn) {
      triggerBtn.addEventListener('click', async function() {
        triggerBtn.disabled = true;
        triggerBtn.textContent = 'Queuing...';
        try {
          await fetch('/api/incidents/' + incidentId + '/investigate/', {
            method: 'POST', credentials: 'include',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: '{}'
          });
          showToast('Investigation queued. Refreshing in 10s...', 'success');
          setTimeout(load, 10000);
        } catch (e) {
          showToast('Failed: ' + e.message, 'error');
          triggerBtn.disabled = false;
          triggerBtn.textContent = '\\U0001F504 Trigger AI Investigation';
        }
      });
    }

""" + old_btns
    content = content.replace(old_btns, new_btns, 1)
    open(path, 'w').write(content)
    print('incident.js: Added Trigger button')
else:
    print('incident.js: Already has trigger button')

print('\\nAll patches applied')
