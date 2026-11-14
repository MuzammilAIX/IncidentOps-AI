import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.incidents.models import Incident
from apps.investigations.services import persist_investigation
from ai_engine.services.orchestrator import run_investigation
from simulator.scenarios.crash_scenario import run_crash_scenario

# Simulate the crash that caused this incident
run_crash_scenario('web-api')
print('✅ Simulated container crash')

# Get incident #11
inc = Incident.objects.get(id=11)
print('✅ Incident:', inc.id, '|', inc.title)

# Run AI
result = run_investigation({
    'incident_id': str(inc.id),
    'service': {'id': 'web-api', 'name': 'web-api'},
    'alert': {'severity': inc.severity},
})
print('✅ AI root cause:', result.get('root_cause'))
print('✅ AI confidence:', result.get('confidence'))

# Save investigation
inv = persist_investigation(inc, result)
print('✅ Investigation saved:', inv.id)
print('✅ Steps:', [s.name for s in inv.steps.all()])

# Check approval
from apps.approvals.models import ApprovalRequest
appr = ApprovalRequest.objects.filter(investigation=inv).first()
if appr:
    print('✅ Approval created:', appr.id, '| status:', appr.status)
else:
    print('⚠️ No approval created')
