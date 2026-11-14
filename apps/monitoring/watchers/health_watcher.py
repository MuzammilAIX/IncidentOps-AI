"""Health watcher — checks service health every cycle."""
import time
from django.utils import timezone
from apps.monitoring.watchers.base import BaseWatcher
from apps.services.models import Service


class HealthWatcher(BaseWatcher):
    """Checks each service's health endpoint. Creates anomalies on failure."""

    def run(self) -> dict:
        services = Service.objects.filter(endpoint__isnull=False).exclude(endpoint="")
        results = {"checked": 0, "failed": 0, "anomalies": []}

        for service in services:
            results["checked"] += 1
            status = self._check_health(service.endpoint)
            if not status["healthy"]:
                results["failed"] += 1
                anomaly = self._create_anomaly(service, status)
                results["anomalies"].append(anomaly.id if anomaly else None)

        return results

    def _check_health(self, url: str) -> dict:
        try:
            import urllib.request
            start = time.time()
            with urllib.request.urlopen(url, timeout=5) as resp:
                elapsed = (time.time() - start) * 1000
                return {
                    "healthy": resp.status == 200,
                    "status_code": resp.status,
                    "response_ms": round(elapsed, 2),
                }
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    def _create_anomaly(self, service, status):
        from apps.monitoring.models import Anomaly
        return Anomaly.objects.create(
            service=service,
            anomaly_type="health_check_failed",
            severity="high" if "error" in status else "medium",
            score=1.0,
            details=status,
        )
