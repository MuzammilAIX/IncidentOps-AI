
"""Monitoring services — anomaly → incident conversion."""
from django.utils import timezone
from apps.monitoring.models import Anomaly


SEVERITY_TO_INCIDENT = {
    "critical": "critical",
    "high": "high",
    "medium": "medium",
    "low": "low",
}


def convert_anomaly_to_incident(anomaly: Anomaly):
    """Create an Incident from a severe anomaly (deduplicate by fingerprint)."""
    from apps.incidents.models import Incident

    if anomaly.incident_id:
        return anomaly.incident

    if anomaly.severity not in ("high", "critical"):
        return None

    incident = Incident.objects.create(
        title=f"[{anomaly.severity}] {anomaly.anomaly_type} on {anomaly.service.name}",
        description=(
            f"Auto-detected by {anomaly.anomaly_type} watcher.\n"
            f"Service: {anomaly.service.name}\n"
            f"Score: {anomaly.score}\n"
            f"Details: {anomaly.details}"
        ),
        severity=SEVERITY_TO_INCIDENT.get(anomaly.severity, "medium"),
        status="open",
        service=anomaly.service,
    )
    anomaly.incident = incident
    anomaly.save(update_fields=["incident"])
    return incident


def process_new_anomalies() -> dict:
    """Convert all unlinked high/critical anomalies to incidents."""
    unlinked = Anomaly.objects.filter(
        incident__isnull=True,
        severity__in=("high", "critical"),
    )
    created = []
    for anomaly in unlinked:
        incident = convert_anomaly_to_incident(anomaly)
        if incident:
            created.append(incident.id)
    return {"converted": len(created), "incident_ids": created}