/* IncidentOps-AI - Incident Detail Page */
(function() {
  let incidentId = null;
  let refreshTimer = null;

  async function init() {
    incidentId = getQueryParam('id');
    if (!incidentId) { document.getElementById('main-content').innerHTML = '<div class="empty-state"><div class="empty-state-title">No incident ID</div></div>'; return; }
    try { const user = await api.me(); document.getElementById('user-info').innerHTML = '<div style="font-size:13px;color:var(--text-primary);font-weight:600">' + escapeHtml(user.username) + '</div>'; } catch (e) { return; }
    document.getElementById('logout-btn').addEventListener('click', async () => { try { await api.logout(); } catch (e) {} window.location.href = '/login/'; });
    await load();
    refreshTimer = setInterval(load, 10000);
  }

  async function load() {
    try {
      const [incident, investigations] = await Promise.all([api.getIncident(incidentId), api.getInvestigations({ incident: incidentId })]);
      const investigation = investigations.results && investigations.results[0];
      let approval = null, runbooks = [], llmCalls = [], similar = [];
      if (investigation) {
        const [approvalsResp, runbooksResp, llmResp, similarResp] = await Promise.all([
          api.getApprovals({ investigation: investigation.id }).catch(() => ({ results: [] })),
          fetch('/api/investigations/' + investigation.id + '/runbooks/', { credentials: 'include' }).then(r => r.ok ? r.json() : { runbooks: [] }).catch(() => ({ runbooks: [] })),
          fetch('/api/monitoring/llm-calls/?investigation=' + investigation.id, { credentials: 'include' }).then(r => r.ok ? r.json() : { results: [] }).catch(() => ({ results: [] })),
          fetch('/api/incidents/' + incidentId + '/similar/', { credentials: 'include' }).then(r => r.ok ? r.json() : { similar: [] }).catch(() => ({ similar: [] })),
        ]);
        approval = approvalsResp.results && approvalsResp.results[0];
        runbooks = runbooksResp.runbooks || [];
        llmCalls = llmResp.results || [];
        similar = similarResp.similar || [];
      }
      render(incident, investigation, approval, runbooks, llmCalls, similar);
      document.getElementById('last-updated').textContent = 'Updated ' + new Date().toLocaleTimeString();
    } catch (e) { console.error('Load failed:', e); document.getElementById('main-content').innerHTML = '<div class="empty-state"><div class="empty-state-title">Failed to load incident</div></div>'; }
  }

  function render(incident, investigation, approval, runbooks, llmCalls, similar) {
    document.getElementById('incident-title').textContent = 'Incident #' + incident.id;
    let html = '';
    html += '<div class="card" style="margin-bottom:16px"><h2 style="font-size:20px;margin-bottom:8px">' + escapeHtml(incident.title) + '</h2><div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">' + severityBadge(incident.severity) + statusBadge(incident.status) + (incident.service_name ? '<span class="badge" style="background:var(--bg-elevated);color:var(--text-secondary)">' + escapeHtml(incident.service_name) + '</span>' : '') + '</div><div style="font-size:13px;color:var(--text-muted)">Created ' + timeAgo(incident.created_at) + '</div>' + (incident.description ? '<div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border);color:var(--text-secondary)">' + escapeHtml(incident.description) + '</div>' : '') + '</div>';
    // Runbooks
    if (runbooks && runbooks.length > 0) {
      html += '<div class="card" style="margin-bottom:16px;border-left:4px solid var(--accent)"><div class="card-header"><h2 class="card-title">📖 Matched Runbooks (' + runbooks.length + ')</h2><span class="badge" style="background:var(--accent-bg);color:var(--accent-hover)">Knowledge Base</span></div><div style="font-size:12px;color:var(--text-muted);margin-bottom:12px">These runbooks from your team knowledge base match this incident. The AI agent consulted them during diagnosis.</div>';
      runbooks.forEach(function(rb) { html += '<div style="padding:14px;background:var(--bg-elevated);border-radius:8px;margin-bottom:10px"><div style="margin-bottom:6px"><div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-bottom:4px"><code style="background:var(--accent-bg);color:var(--accent-hover);padding:2px 6px;border-radius:4px;font-size:12px">' + escapeHtml(rb.code) + '</code> ' + escapeHtml(rb.title) + '</div><div style="font-size:11px;color:var(--text-muted)">Category: ' + escapeHtml(rb.category) + '  |  Match score: ' + rb.score + '</div></div><div style="margin-top:8px;padding:10px;background:var(--bg-primary);border-radius:6px;font-size:12px;color:var(--text-secondary);line-height:1.5">' + escapeHtml(rb.content) + '</div></div>'; });
      html += '</div>';
    }
    // LLM Trace
    if (llmCalls && llmCalls.length > 0) {
      var totalTokens = 0, totalLatency = 0, totalCost = 0;
      llmCalls.forEach(function(c) { totalTokens += (c.total_tokens || 0); totalLatency += (c.latency_ms || 0); totalCost += (c.estimated_cost_usd || 0); });
      html += '<div class="card" style="margin-bottom:16px;border-left:4px solid #8b5cf6">';
      html += '<div class="card-header"><h2 class="card-title">🔍 LLM Trace (' + llmCalls.length + ' call' + (llmCalls.length === 1 ? '' : 's') + ')</h2><span class="badge" style="background:rgba(139,92,246,0.15);color:#8b5cf6">Observability</span></div>';
      html += '<div style="font-size:12px;color:var(--text-muted);margin-bottom:12px">Token usage, latency, and cost for every LLM call in this investigation.</div>';
      html += '<table style="width:100%;font-size:13px;border-collapse:collapse"><thead><tr style="border-bottom:1px solid var(--border);color:var(--text-muted);font-size:11px;text-transform:uppercase"><th style="text-align:left;padding:8px 4px">Agent</th><th style="text-align:right;padding:8px 4px">Tokens</th><th style="text-align:right;padding:8px 4px">Latency</th><th style="text-align:right;padding:8px 4px">Cost</th></tr></thead><tbody>';
      llmCalls.forEach(function(c) { var agentLabel = c.agent_name.charAt(0).toUpperCase() + c.agent_name.slice(1); var status = c.success ? '' : ' <span style="color:#ef4444">✗</span>'; html += '<tr style="border-bottom:1px solid var(--border)"><td style="padding:8px 4px">' + escapeHtml(agentLabel) + status + '</td><td style="text-align:right;padding:8px 4px">' + (c.total_tokens || 0).toLocaleString() + '</td><td style="text-align:right;padding:8px 4px">' + ((c.latency_ms || 0) / 1000).toFixed(1) + 's</td><td style="text-align:right;padding:8px 4px">$' + (c.estimated_cost_usd || 0).toFixed(6) + '</td></tr>'; });
      html += '</tbody><tfoot><tr style="border-top:2px solid var(--border);font-weight:600"><td style="padding:8px 4px">Total</td><td style="text-align:right;padding:8px 4px">' + totalTokens.toLocaleString() + '</td><td style="text-align:right;padding:8px 4px">' + (totalLatency / 1000).toFixed(1) + 's</td><td style="text-align:right;padding:8px 4px">$' + totalCost.toFixed(6) + '</td></tr></tfoot></table>';
      html += '</div>';
    }
    // Similar Incidents (NEW)
    if (similar && similar.length > 0) {
      html += '<div class="card" style="margin-bottom:16px;border-left:4px solid #f59e0b">';
      html += '<div class="card-header"><h2 class="card-title">🔗 Similar Past Incidents (' + similar.length + ')</h2><span class="badge" style="background:rgba(245,158,11,0.15);color:#f59e0b">History</span></div>';
      html += '<div style="font-size:12px;color:var(--text-muted);margin-bottom:12px">Past incidents with similar symptoms or the same service. The agent can learn from these patterns.</div>';
      similar.forEach(function(s) {
        html += '<a href="/incident/?id=' + s.id + '" style="display:block;padding:12px;background:var(--bg-elevated);border-radius:8px;margin-bottom:8px;text-decoration:none;color:inherit"><div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:6px"><div style="flex:1"><div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-bottom:4px">#' + s.id + ' ' + escapeHtml(s.title) + '</div><div style="font-size:11px;color:var(--text-muted)">' + (s.service_name ? escapeHtml(s.service_name) + ' · ' : '') + escapeHtml(s.status) + '</div></div>' + severityBadge(s.severity) + '</div>' + (s.root_cause ? '<div style="font-size:12px;color:var(--text-secondary);margin-top:6px;padding-top:6px;border-top:1px solid var(--border)">Root cause: ' + escapeHtml(s.root_cause) + '</div>' : '') + '</a>';
      });
      html += '</div>';
    }
    // Investigation
    if (investigation) {
      html += '<div class="card" style="margin-bottom:16px"><div class="card-header"><h2 class="card-title">AI Investigation</h2></div><div style="margin-bottom:16px"><div style="font-size:12px;color:var(--text-muted);margin-bottom:4px">Root Cause</div><div style="font-size:16px;font-weight:600;margin-bottom:8px">' + escapeHtml(investigation.root_cause || 'Unknown') + '</div><div style="display:flex;align-items:center;gap:12px"><span style="font-size:12px;color:var(--text-muted)">Confidence</span><div style="flex:1;max-width:200px;height:8px;background:var(--bg-elevated);border-radius:4px;overflow:hidden"><div style="width:' + Math.round((investigation.confidence || 0) * 100) + '%;height:100%;background:var(--accent)"></div></div><span style="font-size:13px;font-weight:600">' + Math.round((investigation.confidence || 0) * 100) + '%</span></div></div>';
      if (investigation.steps && investigation.steps.length > 0) { html += '<div style="padding-top:16px;border-top:1px solid var(--border)"><div style="font-size:12px;color:var(--text-muted);margin-bottom:8px">Reasoning Steps</div><div style="display:flex;gap:6px;flex-wrap:wrap">'; investigation.steps.forEach(function(s) { html += '<span class="badge" style="background:var(--accent-bg);color:var(--accent-hover)">' + escapeHtml(s.name) + '</span>'; }); html += '</div></div>'; }
      html += '</div>';
    } else { html += '<div class="card" style="margin-bottom:16px"><div class="empty-state"><div class="empty-state-title">No investigation yet</div></div></div>'; }
    // Approval
    if (approval) {
      html += '<div class="card" style="margin-bottom:16px"><div class="card-header"><h2 class="card-title">Proposed Remediation</h2><span class="badge badge-' + escapeHtml(approval.status) + '">' + escapeHtml(approval.status) + '</span></div>';
      if (approval.proposed_actions && approval.proposed_actions.length > 0) { approval.proposed_actions.forEach(function(a, i) { html += '<div style="padding:16px;background:var(--bg-elevated);border-radius:8px;margin-bottom:12px"><div style="font-weight:600;margin-bottom:6px">Option ' + (i + 1) + '</div><div style="font-size:14px;margin-bottom:6px"><strong>' + escapeHtml(a.action || '') + '</strong> on <code>' + escapeHtml(a.target || '') + '</code></div>' + (a.reason ? '<div style="font-size:13px;color:var(--text-secondary)">' + escapeHtml(a.reason) + '</div>' : '') + '</div>'; }); }
      if (approval.status === 'pending') { html += '<div style="display:flex;gap:8px;margin-top:16px"><button class="btn btn-success" id="approve-btn">Approve</button><button class="btn btn-danger" id="reject-btn">Reject</button></div>'; } else { html += '<div style="font-size:13px;color:var(--text-muted);margin-top:12px">Decision: <strong>' + escapeHtml(approval.status) + '</strong></div>'; }
      html += '</div>';
    }
    // Timeline
    html += '<div class="card"><div class="card-header"><h2 class="card-title">Timeline</h2></div><div class="timeline"><div class="timeline-item"><div class="timeline-title">Incident created</div><div class="timeline-meta">' + formatDate(incident.created_at) + '</div></div>';
    if (investigation) {
      html += '<div class="timeline-item"><div class="timeline-title">Investigation started</div><div class="timeline-meta">' + formatDate(investigation.started_at) + '</div></div>';
      if (runbooks.length > 0) { html += '<div class="timeline-item"><div class="timeline-title">' + runbooks.length + ' runbook(s) matched</div><div class="timeline-meta">' + runbooks.map(function(r) { return r.code; }).join(', ') + '</div></div>'; }
      if (similar.length > 0) { html += '<div class="timeline-item"><div class="timeline-title">' + similar.length + ' similar incident(s) found</div><div class="timeline-meta">#' + similar.map(function(s) { return s.id; }).join(', #') + '</div></div>'; }
      if (llmCalls.length > 0) { html += '<div class="timeline-item"><div class="timeline-title">' + llmCalls.length + ' LLM call(s) traced</div><div class="timeline-meta">Total: $' + (llmCalls.reduce(function(s, c) { return s + (c.estimated_cost_usd || 0); }, 0)).toFixed(6) + '</div></div>'; }
      if (investigation.finished_at) { html += '<div class="timeline-item"><div class="timeline-title">Investigation completed</div><div class="timeline-meta">' + formatDate(investigation.finished_at) + '</div></div>'; }
    }
    if (approval) { html += '<div class="timeline-item"><div class="timeline-title">Approval requested</div><div class="timeline-meta">' + formatDate(approval.created_at) + '</div></div>'; }
    html += '</div></div>';
    document.getElementById('main-content').innerHTML = html;
    const approveBtn = document.getElementById('approve-btn');
    const rejectBtn = document.getElementById('reject-btn');
    if (approveBtn) { approveBtn.addEventListener('click', async () => { approveBtn.disabled = true; try { await api.approveApproval(approval.id); showToast('Approved', 'success'); setTimeout(load, 500); } catch (e) { showToast('Failed: ' + e.message, 'error'); approveBtn.disabled = false; } }); }
    if (rejectBtn) { rejectBtn.addEventListener('click', async () => { rejectBtn.disabled = true; try { await api.rejectApproval(approval.id); showToast('Rejected', 'success'); setTimeout(load, 500); } catch (e) { showToast('Failed: ' + e.message, 'error'); rejectBtn.disabled = false; } }); }
  }
  init();
})();