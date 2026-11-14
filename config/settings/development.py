from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# -------------------------------------------------------------
# LOCAL DEV OVERRIDES - runserver on Windows
# Force localhost so "db" and "redis" service names from .env
# don't get resolved outside Docker.
# Local Postgres is on 5432 (confirmed via Get-NetTCPConnection).
# -------------------------------------------------------------

DATABASES["default"]["HOST"] = "localhost"
DATABASES["default"]["PORT"] = "5432"

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
