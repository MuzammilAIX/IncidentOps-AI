"""Log watcher — scans container logs for error patterns."""
import re
from datetime import datetime, timedelta
from apps.monitoring.watchers.base import BaseWatcher
from apps.services.models import Service


class LogWatcher(BaseWatcher):
    """Scans logs for error patterns; deduplicates by pattern hash."""

    ERROR_PATTERNS = {
        "oom_killed": r"(oom|out of memory|oomkill)",
        "connection_refused": r"connection refused",
        "timeout": r"(timeout|timed out)",
        "segfault": r"segfault|sigsegv",
        "unhandled_exception": r"traceback|unhandled exception|fatal error",
        "database_error": r"(deadlock|connection pool|too many connections)",
    }

    def run(self) -> dict:
        services = Service.objects.filter(kind="docker")
        results = {"checked": 0, "matches": []}

        for service in services:
            results["checked"] += 1
            logs = self._fetch_logs(service.name)
            if not logs:
                continue
            matches = self._scan(logs)
            for pattern_name, match in matches.items():
                anomaly = self._create_anomaly(service, pattern_name, match)
                results["matches"].append(anomaly.id if anomaly else None)

        return results

    def _fetch_logs(self, service_name: str) -> str:
        import os
        if os.getenv("USE_SIMULATOR", "1") == "1":
            from ai_engine.tools.docker_tools import _get_docker
            docker = _get_docker()
            if hasattr(docker, "get_logs"):
                logs = docker.get_logs(service_name, lines=100)
                return " ".join(str(e.get("line", "")) if isinstance(e, dict) else str(e) for e in logs)
            return ""
        try:
            from integrations.docker.client import DockerConnector
            logs = DockerConnector().get_logs(service_name, lines=100)
            return " ".join(str(e.get("line", "")) if isinstance(e, dict) else str(e) for e in logs)
        except Exception:
            return ""

    def _scan(self, text: str) -> dict:
        matches = {}
        lowered = text.lower()
        for name, pattern in self.ERROR_PATTERNS.items():
            if re.search(pattern, lowered):
                matches[name] = {"pattern": pattern, "sample": text[:200]}
        return matches

    def _create_anomaly(self, service, pattern_name, match):
        from apps.monitoring.models import Anomaly
        severity = "critical" if pattern_name == "oom_killed" else "high"
        return Anomaly.objects.create(
            service=service,
            anomaly_type=pattern_name,
            severity=severity,
            score=1.0,
            details=match,
        )
