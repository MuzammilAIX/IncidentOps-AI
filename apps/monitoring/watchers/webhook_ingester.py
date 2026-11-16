"""Webhook ingester — receives alerts from Prometheus/Grafana."""
from apps.monitoring.watchers.base import BaseWatcher


class WebhookIngester(BaseWatcher):
    """Not a scheduled watcher — this is called by HTTP endpoints."""

    def run(self) -> dict:
        return {"info": "WebhookIngester is called via HTTP, not scheduled."}

    @staticmethod
    def ingest_prometheus(payload: dict) -> int:
        """Process Prometheus AlertManager payload. Returns anomaly count."""
        from apps.monitoring.models import Anomaly
        from apps.services.models import Service

        count = 0
        for alert in payload.get("alerts", []):
            labels = alert.get("labels", {})
            service_name = labels.get("service") or labels.get("job", "unknown")
            service = Service.objects.filter(name=service_name).first()
            if not service:
                continue

            Anomaly.objects.create(
                service=service,
                anomaly_type=f"prometheus_{labels.get('alertname', 'alert')}",
                severity="critical" if labels.get("severity") == "critical" else "high",
                score=1.0,
                details=alert,
            )
            count += 1
        return count

    @staticmethod
    def ingest_grafana(payload: dict) -> int:
        """Process Grafana alert payload."""
        return WebhookIngester.ingest_prometheus({"alerts": payload.get("alerts", [])})

    @staticmethod
    def ingest_generic(payload: dict) -> int:
        """Generic webhook — creates anomaly as-is."""
        from apps.monitoring.models import Anomaly
        from apps.services.models import Service

        service_name = payload.get("service", "unknown")
        service = Service.objects.filter(name=service_name).first()
        if not service:
            return 0

        Anomaly.objects.create(
            service=service,
            anomaly_type=payload.get("type", "generic_alert"),
            severity=payload.get("severity", "medium"),
            score=payload.get("score", 1.0),
            details=payload,
        )
        return 1


    @staticmethod
    def ingest_as_incident(payload: dict) -> dict:
        """Create an Incident (not just Anomaly) from an external alert."""
        from apps.monitoring.models import Anomaly
        from apps.incidents.models import Incident
        from apps.services.models import Service

        service_name = payload.get("service", "unknown")
        service = Service.objects.filter(name=service_name).first()

        severity = payload.get("severity", "medium")
        if severity not in ("low", "medium", "high", "critical"):
            severity = "medium"

        title = payload.get("name") or payload.get("title") or "External alert"
        description = payload.get("description") or payload.get("summary") or ""

        incident = Incident.objects.create(
            title=title,
            description=description,
            severity=severity,
            status="open",
            service=service,
        )

        if service:
            Anomaly.objects.create(
                service=service,
                anomaly_type=payload.get("type", "external_webhook"),
                severity=severity,
                score=payload.get("score", 1.0),
                details=payload,
                incident=incident,
            )

        return {"incident_id": incident.id, "service": service_name}
