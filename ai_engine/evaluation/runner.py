'''Run AI evaluation against known scenarios.'''
import time
import yaml
from pathlib import Path

from apps.incidents.models import Incident
from apps.services.models import Service
from ai_engine.agents.triage_agent import triage
from ai_engine.agents.diagnosis_agent import diagnose
from ai_engine.tools.runbook_tool import search_runbooks

SCENARIOS_DIR = Path(__file__).parent / 'scenarios'
REPORT_PATH = Path('/app/frontend/evaluation_report.md')


def _semantic_match(expected, actual):
    if not actual:
        return False, 'empty'
    exp_lower = expected.lower()
    act_lower = actual.lower()
    if exp_lower == act_lower:
        return True, 'exact'
    kw_map = {
        'container_oom_killed': ['oom', 'out of memory', 'resource limit', 'memory limit', 'capacity'],
        'cpu_saturation': ['cpu saturation', 'cpu saturated', 'cpu throttl', 'high cpu', 'cpu utilization', 'cpu'],
        'memory_leak': ['memory leak', 'leaking memory', 'memory growth'],
        'container_crashed': ['container crash', 'container exited', 'crashed'],
    }
    for kw in kw_map.get(expected, [expected.replace('_', ' ')]):
        if kw in act_lower:
            return True, 'keyword:' + kw
    return False, 'no match'


def run_scenario(sp):
    with open(sp, encoding='utf-8') as f:
        s = yaml.safe_load(f)
    svc_name = s.get('service', 'test-service')
    svc, _ = Service.objects.get_or_create(name=svc_name, defaults={'kind': 'docker', 'endpoint': ''})
    inc = Incident.objects.create(title=s['description'], description=s['description'], severity=s.get('severity', 'high'), status='open', service=svc)
    start = time.time()
    try:
        alert = {'source': 'evaluation', 'scenario': s['name']}
        tr = triage(inc, alert)
        dg = diagnose(inc, tr, s.get('diagnostics', {}))
        elapsed = time.time() - start
        exp = s['expected_root_cause']
        act = dg.primary_root_cause
        matched, reason = _semantic_match(exp, act)
        rbs = search_runbooks(inc.title, svc_name, limit=3)
        result = {
            'scenario': s['name'], 'expected': exp, 'actual': act,
            'correct': matched, 'match_reason': reason,
            'confidence': dg.confidence, 'latency_seconds': round(elapsed, 2),
            'runbooks_matched': [r['code'] for r in rbs],
            'reasoning': dg.reasoning[:200],
        }
    except Exception as e:
        result = {
            'scenario': s['name'], 'expected': s['expected_root_cause'],
            'actual': 'ERROR: ' + str(e), 'correct': False, 'match_reason': 'error',
            'confidence': 0.0, 'latency_seconds': round(time.time() - start, 2),
            'runbooks_matched': [], 'reasoning': 'Error',
        }
    finally:
        inc.delete()
    return result


def run_all():
    scenarios = sorted(SCENARIOS_DIR.glob('*.yaml'))
    results = []
    for sp in scenarios:
        print('')
        print('=' * 60)
        print('Running: ' + sp.name)
        print('=' * 60)
        r = run_scenario(sp)
        results.append(r)
        print('  Expected: ' + r['expected'])
        print('  Actual:   ' + r['actual'])
        print('  Verdict:  ' + ('PASS (' + r['match_reason'] + ')' if r['correct'] else 'FAIL'))
        print('  Confidence: ' + str(round(r['confidence'] * 100)) + '%')
        print('  Latency: ' + str(r['latency_seconds']) + 's')
        print('  Runbooks: ' + (', '.join(r['runbooks_matched']) or 'none'))
    total = len(results)
    passed = sum(1 for r in results if r['correct'])
    acc = passed / total if total > 0 else 0.0
    lines = [
        '# IncidentOps-AI Evaluation Report', '',
        '- Total scenarios: ' + str(total),
        '- Passed: ' + str(passed),
        '- Root cause accuracy: ' + str(passed) + '/' + str(total) + ' (' + str(round(acc * 100)) + '%)',
        '', '## Results', '',
        '| Scenario | Expected | Actual | Correct | Confidence | Latency | Runbooks |',
        '|----------|----------|--------|---------|------------|---------|----------|',
    ]
    for r in results:
        short = r['actual'][:80].replace('|', '/') if len(r['actual']) > 80 else r['actual'].replace('|', '/')
        lines.append('| ' + r['scenario'] + ' | ' + r['expected'] + ' | ' + short + ' | ' + ('PASS' if r['correct'] else 'FAIL') + ' | ' + str(round(r['confidence'] * 100)) + '% | ' + str(r['latency_seconds']) + 's | ' + (', '.join(r['runbooks_matched']) or '-') + ' |')
    lines.extend(['', '## Detailed Results', ''])
    for r in results:
        lines.append('### ' + r['scenario'])
        lines.append('')
        lines.append('- Expected: ' + r['expected'])
        lines.append('- Actual: ' + r['actual'])
        lines.append('- Match: ' + r['match_reason'])
        lines.append('- Confidence: ' + str(round(r['confidence'] * 100)) + '%')
        lines.append('- Latency: ' + str(r['latency_seconds']) + 's')
        lines.append('- Runbooks: ' + (', '.join(r['runbooks_matched']) or 'none'))
        lines.append('- Reasoning: ' + r['reasoning'])
        lines.append('')
    try:
        REPORT_PATH.write_text(chr(10).join(lines), encoding='utf-8')
        print('Report: ' + str(REPORT_PATH))
    except Exception as e:
        print('Could not write report: ' + str(e))
    print('')
    print('=' * 60)
    print('SUMMARY')
    print('=' * 60)
    print('Total: ' + str(total))
    print('Passed: ' + str(passed))
    print('Accuracy: ' + str(round(acc * 100)) + '%')
    return {'total': total, 'passed': passed, 'accuracy': acc, 'results': results}
