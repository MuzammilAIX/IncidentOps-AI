"""Metric watcher — polls Prometheus and compares against baselines."""
from statistics import mean, stdev
from apps.monitoring.watchers.base import BaseWatcher
from apps.services.models import Service


class MetricWatcher(BaseWatcher):
    """Polls Prometheus metrics, detects deviations from rolling baselines."""

    METRIC_QUERIES = {
        "cpu_usage": 'rate(container_cpu_usage_seconds_total{{name="{name}"}}[5m])',
        "memory_usage": 'container_memory_usage_bytes{{name="{name}"}}',
        "error_rate": 'rate(http_requests_total{{service="{name}",status=~"5.."}}[5m])',
    }

    def run(self) -> dict:
        from integrations.prometheus.client import PrometheusConnector
        prom = PrometheusConnector()
        if not prom.health_check():
            return {"skipped": "Prometheus unavailable"}

        services = Service.objects.filter(kind="docker")
        results = {"checked": 0, "anomalies": []}

        for service in services:
            results["checked"] += 1
            for metric_name, template in self.METRIC_QUERIES.items():
                query = template.format(name=service.name)
                data = prom.query(query)
                values = self._extract_values(data)
                if values:
                    anomaly = self._check_baseline(service, metric_name, values)
                    if anomaly:
                        results["anomalies"].append(anomaly.id)

        return results

    def _extract_values(self, data: dict) -> list:
        try:
            return [float(r["value"][1]) for r in data.get("result", [])]
        except Exception:
            return []

    def _check_baseline(self, service, metric_name, values):
        from apps.monitoring.models import Baseline, Anomaly
        current = mean(values)
        baseline, _ = Baseline.objects.get_or_create(
            service=service, metric_name=metric_name,
            defaults={"mean": current, "stddev": 0, "sample_count": 0},
        )

        if baseline.sample_count < 5:
            baseline.mean = current
            baseline.stddev = 0
            baseline.sample_count += 1
            baseline.save()
            return None

        threshold = baseline.mean + (3 * max(baseline.stddev, 0.01))
        if current > threshold:
            return Anomaly.objects.create(
                service=service,
                anomaly_type=f"{metric_name}_spike",
                severity="high" if current > threshold * 1.5 else "medium",
                score=current / threshold,
                details={"current": current, "mean": baseline.mean, "threshold": threshold},
            )

        baseline.sample_count += 1
        baseline.save()
        return None
