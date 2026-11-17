# Business logic for this app

"""
Incident services: trigger AI investigation when an incident is created.
"""
import logging

logger = logging.getLogger(__name__)


def trigger_investigation(incident):
    """
    Run the AI investigation synchronously (inline).

    Creates the Investigation row, runs the LangGraph pipeline, persists
    the result, and returns the Investigation id. No Celery/Redis required.
    """
    from ai_engine.services.orchestrator import run_investigation
    from apps.investigations.services import persist_investigation

    payload = {
        "incident_id": incident.id,
        "service": {
            "id": incident.service_id,
            "name": getattr(incident.service, "name", "") if incident.service else "",
        },
        "alert": {
            "title": incident.title,
            "severity": incident.severity,
            "description": incident.description,
        },
    }

    try:
        ai_result = run_investigation(payload)
        inv = persist_investigation(incident, ai_result)
        logger.info("Investigation %s created for incident %s", inv.id, incident.id)
        return {"queued": False, "investigation_id": inv.id, "status": inv.status}
    except Exception as e:
        logger.exception("Investigation failed for incident %s", incident.id)
        return {"queued": False, "error": str(e)}
