"""Celery tasks for monitoring."""
from celery import shared_task


@shared_task
def run_health_watcher():
    from apps.monitoring.watchers.health_watcher import HealthWatcher
    return HealthWatcher().safe_run()


@shared_task
def run_metric_watcher():
    from apps.monitoring.watchers.metric_watcher import MetricWatcher
    return MetricWatcher().safe_run()


@shared_task
def run_log_watcher():
    from apps.monitoring.watchers.log_watcher import LogWatcher
    return LogWatcher().safe_run()


@shared_task
def process_anomalies():
    from apps.monitoring.services import process_new_anomalies
    return process_new_anomalies()
