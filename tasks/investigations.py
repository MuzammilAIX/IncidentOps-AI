
"""
Celery task: run AI investigation for an incident.
"""
from celery import shared_task


@shared_task(bind=True, max_retries=3)
def run_investigation_task(self, incident_id: int):
    """Run the AI investigation for the given incident."""
    from apps.incidents.models import Incident
    from apps.investigations.services import persist_investigation
    from ai_engine.services.orchestrator import run_investigation

    try:
        incident = Incident.objects.get(id=incident_id)
    except Incident.DoesNotExist:
        return {"error": f"Incident {incident_id} not found"}

    payload = {
        "incident_id": str(incident.id),
        "service": {
            "id": incident.service.id if incident.service else None,
            "name": incident.service.name if incident.service else "unknown",
        },
        "alert": {"severity": incident.severity},
    }

    try:
        result = run_investigation(payload)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)

    investigation = persist_investigation(incident, result)
    return {
        "investigation_id": investigation.id,
        "root_cause": investigation.root_cause,
        "confidence": investigation.confidence,
    }
