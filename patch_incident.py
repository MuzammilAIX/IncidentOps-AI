"""Patch incident.js to add similar incidents panel."""
path = '/app/frontend/js/incident.js'
content = open(path).read()

if 'Similar Past Incidents' in content:
    print('Already has similar panel - skipping')
    raise SystemExit(0)

# 1. Add `similar` to variable declarations
content = content.replace(
    'let approval = null, runbooks = [], llmCalls = [];',
    'let approval = null, runbooks = [], llmCalls = [], similar = [];',
    1
)

# 2. Add similar fetch to Promise.all
old_fetch = "fetch('/api/monitoring/llm-calls/?investigation=' + investigation.id, { credentials: 'include' }).then(r => r.ok ? r.json() : { results: [] }).catch(() => ({ results: [] })),"
new_fetch = old_fetch + "\n          fetch('/api/incidents/' + incidentId + '/similar/', { credentials: 'include' }).then(r => r.ok ? r.json() : { similar: [] }).catch(() => ({ similar: [] })),"
content = content.replace(old_fetch, new_fetch, 1)

# 3. Add similar assignment
content = content.replace(
    'llmCalls = llmResp.results || [];',
    'llmCalls = llmResp.results || [];\n        similar = similarResp.similar || [];',
    1
)

# 4. Update render call
content = content.replace(
    'render(incident, investigation, approval, runbooks, llmCalls);',
    'render(incident, investigation, approval, runbooks, llmCalls, similar);',
    1
)

# 5. Update render signature
content = content.replace(
    'function render(incident, investigation, approval, runbooks, llmCalls) {',
    'function render(incident, investigation, approval, runbooks, llmCalls, similar) {',
    1
)

# 6. Add similar card before AI Investigation section
similar_card = """    if (similar && similar.length > 0) {
      html += '<div class="card" style="margin-bottom:16px;border-left:4px solid #f59e0b">';
      html += '<div class="card-header"><h2 class="card-title">\\U0001F517 Similar Past Incidents (' + similar.length + ')</h2><span class="badge" style="background:rgba(245,158,11,0.15);color:#f59e0b">History</span></div>';
      html += '<div style="font-size:12px;color:var(--text-muted);margin-bottom:12px">Past incidents with similar symptoms or the same service.</div>';
      similar.forEach(function(s) {
        html += '<a href="/incident/?id=' + s.id + '" style="display:block;padding:12px;background:var(--bg-elevated);border-radius:8px;margin-bottom:8px;text-decoration:none;color:inherit"><div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px"><div style="flex:1"><div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-bottom:4px">#' + s.id + ' ' + escapeHtml(s.title) + '</div><div style="font-size:11px;color:var(--text-muted)">' + (s.service_name ? escapeHtml(s.service_name) + ' \\u00B7 ' : '') + escapeHtml(s.status) + '</div></div>' + severityBadge(s.severity) + '</div></a>';
      });
      html += '</div>';
    }
"""
old_inv = """    if (investigation) {
      html += '<div class="card" style="margin-bottom:16px"><div class="card-header"><h2 class="card-title">AI Investigation</h2></div>"""
new_inv = similar_card + """    if (investigation) {
      html += '<div class="card" style="margin-bottom:16px"><div class="card-header"><h2 class="card-title">AI Investigation</h2></div>"""
content = content.replace(old_inv, new_inv, 1)

# 7. Add similar timeline entry
old_tl = "if (llmCalls.length > 0) { html += '<div class=\"timeline-item\"><div class=\"timeline-title\">' + llmCalls.length + ' LLM call(s) traced</div>"
new_tl = "if (similar.length > 0) { html += '<div class=\"timeline-item\"><div class=\"timeline-title\">' + similar.length + ' similar incident(s) found</div><div class=\"timeline-meta\">#' + similar.map(function(s) { return s.id; }).join(', #') + '</div></div>'; }\n      " + old_tl
content = content.replace(old_tl, new_tl, 1)

open(path, 'w').write(content)
print('Updated incident.js successfully')
print('Has similar panel:', 'Similar Past Incidents' in content)
print('Has similar variable:', 'similar = similarResp' in content)
