# Business logic for this app

"""
Incident services: trigger AI investigation when an incident is created.
"""


def trigger_investigation(incident):
    """Queue the AI investigation task for the given incident."""
    from tasks.investigations import run_investigation_task

    try:
        result = run_investigation_task.delay(incident.id)
        return {"queued": True, "task_id": str(result.id)}
    except Exception as e:
        # Celery / Redis may not be running in dev — don't crash the API
        return {"queued": False, "error": str(e)}
