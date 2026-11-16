"""Add feedback panel to incident.js."""
path = '/app/frontend/js/incident.js'
content = open(path).read()

if 'feedback-panel' in content or 'Was this diagnosis' in content:
    print('Already has feedback panel')
    raise SystemExit(0)

# 1. Add feedback fetch to load() — after similar fetch
old = "fetch('/api/incidents/' + incidentId + '/similar/', { credentials: 'include' }).then(r => r.ok ? r.json() : { similar: [] }).catch(() => ({ similar: [] })),"
new = old + "\n          fetch('/api/investigations/' + investigation.id + '/feedback/', { credentials: 'include' }).then(r => r.ok ? r.json() : { results: [] }).catch(() => ({ results: [] })),"
content = content.replace(old, new, 1)

# 2. Add feedback variable
content = content.replace(
    'let approval = null, runbooks = [], llmCalls = [], similar = [];',
    'let approval = null, runbooks = [], llmCalls = [], similar = [], feedback = [];',
    1
)

# 3. Assign feedback result (must be after the Promise.all destructuring)
old_destructure = "const [approvalsResp, runbooksResp, llmResp, similarResp] = await Promise.all(["
new_destructure = "const [approvalsResp, runbooksResp, llmResp, similarResp, feedbackResp] = await Promise.all(["
content = content.replace(old_destructure, new_destructure, 1)

# 4. Assign feedback after similar
content = content.replace(
    'similar = similarResp.similar || [];',
    'similar = similarResp.similar || [];\n        feedback = feedbackResp.results || [];',
    1
)

# 5. Update render call
content = content.replace(
    'render(incident, investigation, approval, runbooks, llmCalls, similar);',
    'render(incident, investigation, approval, runbooks, llmCalls, similar, feedback);',
    1
)

# 6. Update render signature
content = content.replace(
    'function render(incident, investigation, approval, runbooks, llmCalls, similar) {',
    'function render(incident, investigation, approval, runbooks, llmCalls, similar, feedback) {',
    1
)

# 7. Add feedback panel before Timeline section
feedback_panel = '''    // Feedback panel (NEW)
    if (investigation) {
      var hasFeedback = feedback && feedback.length > 0;
      html += '<div class="card" style="margin-bottom:16px;border-left:4px solid #10b981">';
      html += '<div class="card-header"><h2 class="card-title">\\U0001F4AC Was this diagnosis correct?</h2>';
      if (hasFeedback) {
        html += '<span class="badge" style="background:rgba(16,185,129,0.15);color:#10b981">Feedback recorded</span>';
      }
      html += '</div>';
      if (hasFeedback) {
        var fb = feedback[0];
        var verdictLabel = {correct: '\\u2705 Correct', partial: '\\uD83E\\uDD14 Partial', wrong: '\\u274C Wrong', unclear: '\\u2753 Unclear'}[fb.verdict] || fb.verdict;
        html += '<div style="padding:12px;background:var(--bg-elevated);border-radius:8px">';
        html += '<div style="font-weight:600;margin-bottom:4px">' + verdictLabel + '</div>';
        if (fb.comment) { html += '<div style="font-size:13px;color:var(--text-secondary)">' + escapeHtml(fb.comment) + '</div>'; }
        html += '<div style="font-size:11px;color:var(--text-muted);margin-top:6px">By ' + escapeHtml(fb.user_username || 'anonymous') + '</div>';
        html += '</div>';
      } else {
        html += '<div style="font-size:12px;color:var(--text-muted);margin-bottom:12px">Help improve future diagnoses. Was this AI investigation helpful?</div>';
        html += '<div style="display:flex;gap:8px;flex-wrap:wrap" id="feedback-buttons">';
        html += '<button class="btn btn-success" data-verdict="correct" style="flex:1;min-width:120px">\\U0001F44D Correct</button>';
        html += '<button class="btn btn-ghost" data-verdict="partial" style="flex:1;min-width:120px">\\U0001F914 Partial</button>';
        html += '<button class="btn btn-danger" data-verdict="wrong" style="flex:1;min-width:120px">\\U0001F44E Wrong</button>';
        html += '</div>';
        html += '<div style="margin-top:12px"><input type="text" class="form-input" id="feedback-comment" placeholder="Optional: what was the actual root cause?" style="font-size:13px"></div>';
      }
      html += '</div>';
    }
'''
old_inv = """    if (investigation) {
      html += '<div class="card" style="margin-bottom:16px"><div class="card-header"><h2 class="card-title">AI Investigation</h2></div>"""
new_inv = feedback_panel + """    if (investigation) {
      html += '<div class="card" style="margin-bottom:16px"><div class="card-header"><h2 class="card-title">AI Investigation</h2></div>"""
content = content.replace(old_inv, new_inv, 1)

# 8. Add feedback button click handlers
old_btns = """    const approveBtn = document.getElementById('approve-btn');
    const rejectBtn = document.getElementById('reject-btn');"""
new_btns = """    // Wire feedback buttons
    var fbButtons = document.querySelectorAll('#feedback-buttons button');
    fbButtons.forEach(function(btn) {
      btn.addEventListener('click', async function() {
        var verdict = btn.getAttribute('data-verdict');
        var comment = (document.getElementById('feedback-comment') || {}).value || '';
        fbButtons.forEach(function(b) { b.disabled = true; });
        try {
          await fetch('/api/investigations/' + investigation.id + '/feedback/', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ verdict: verdict, comment: comment })
          });
          showToast('Feedback recorded!', 'success');
          setTimeout(load, 500);
        } catch (e) {
          showToast('Failed: ' + e.message, 'error');
          fbButtons.forEach(function(b) { b.disabled = false; });
        }
      });
    });

    const approveBtn = document.getElementById('approve-btn');
    const rejectBtn = document.getElementById('reject-btn');"""
content = content.replace(old_btns, new_btns, 1)

open(path, 'w').write(content)
print('Feedback panel added')
print('Has feedback-panel code:', 'feedback-buttons' in content)
