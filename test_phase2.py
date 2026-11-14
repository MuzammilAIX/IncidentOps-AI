import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.incidents.models import Incident
from apps.services.models import Service
from simulator.scenarios.crash_scenario import run_crash_scenario
from ai_engine.services.orchestrator import run_investigation

run_crash_scenario('web-api')
svc = Service.objects.filter(name='web-api').first()
inc = Incident.objects.create(
    title='OOM in production',
    description='web-api container OOM-killed under load',
    severity='critical',
    service=svc,
)

result = run_investigation({
    'incident_id': str(inc.id),
    'service': {'id': svc.name if svc else 'unknown'},
    'alert': {'severity': 'critical'},
})

print()
print('LLM used:', result.get('llm_used'))
print('Steps:', result.get('steps'))
print('Root cause:', result.get('root_cause'))
print('Confidence:', result.get('confidence'))
print('Actions:', len(result.get('remediation', {}).get('actions', [])))
print()
for a in result.get('remediation', {}).get('actions', []):
    action = a.get('action')
    target = a.get('target')
    risk = a.get('risk')
    print('-', action, 'on', target, '(risk:', risk, ')')
