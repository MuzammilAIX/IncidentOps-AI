
from celery import shared_task


@shared_task
def run_investigation_task(incident_id: str):
    from ai_engine.services.orchestrator import run_investigation
    result = run_investigation({"incident_id": incident_id})
    return result
