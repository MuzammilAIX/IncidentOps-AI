
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("incidentops")
app.config_from_object("django.conf:settings", namespace="CELERY")

# FIX #16: tasks/ is a top-level package, not a Django app.
# Tell Celery to look there explicitly.
app.autodiscover_tasks(["tasks"], related_name=None)
app.autodiscover_tasks()

# Explicit imports so the worker registers tasks even without autodiscover
# (helps in dev where tasks/ is not yet an installed app).
import tasks.investigations  # noqa: F401, E402
import tasks.monitoring      # noqa: F401, E402
import tasks.remediation     # noqa: F401, E402
