
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("incidentops")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(["tasks"], related_name=None)
app.autodiscover_tasks()

import tasks.investigations  # noqa: F401, E402
import tasks.monitoring      # noqa: F401, E402
import tasks.remediation     # noqa: F401, E402

# Beat schedule — real-time watchers
app.conf.beat_schedule = {
    "health-watcher": {
        "task": "apps.monitoring.tasks.run_health_watcher",
        "schedule": 60.0,
    },
    "metric-watcher": {
        "task": "apps.monitoring.tasks.run_metric_watcher",
        "schedule": 30.0,
    },
    "log-watcher": {
        "task": "apps.monitoring.tasks.run_log_watcher",
        "schedule": 30.0,
    },
    "process-anomalies": {
        "task": "apps.monitoring.tasks.process_anomalies",
        "schedule": 15.0,
    },
}