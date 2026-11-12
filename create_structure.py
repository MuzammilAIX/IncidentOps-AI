"""
IncidentOps-AI bootstrap script — FIXED.
Creates the entire project structure in one command.
Run: python bootstrap.py
"""

import os
from pathlib import Path

ROOT = Path(__file__).parent
CREATED = []


def make_dir(path: str):
    p = ROOT / path
    p.mkdir(parents=True, exist_ok=True)
    CREATED.append(("dir", str(p)))


def make_file(path: str, content: str = ""):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text(content)
        CREATED.append(("file", str(p)))


# ─────────────────────────────────────────────────────────────
# 1. CONFIG
# ─────────────────────────────────────────────────────────────
make_dir("config/settings")

# FIX #7: Do NOT import celery here — circular import.
# Keep config/__init__.py minimal. Celery is loaded on demand.
make_file("config/__init__.py", "")

make_file("config/celery.py", '''
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
''')

make_file("config/asgi.py", '''
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
application = get_asgi_application()
''')

make_file("config/wsgi.py", '''
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
application = get_wsgi_application()
''')

make_file("config/urls.py", '''
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/incidents/", include("apps.incidents.urls")),
    path("api/investigations/", include("apps.investigations.urls")),
    path("api/approvals/", include("apps.approvals.urls")),
]
''')

make_file("config/settings/__init__.py", "")

make_file("config/settings/base.py", '''
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.accounts",
    "apps.teams",
    "apps.services",
    "apps.incidents",
    "apps.monitoring",
    "apps.investigations",
    "apps.approvals",
    "apps.remediation",
    "apps.audit",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "incidentops"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

AUTH_USER_MODEL = "accounts.User"   # FIX #1 / #4 — model defined in apps/accounts/models.py below
AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
''')

make_file("config/settings/development.py", '''
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
''')

make_file("config/settings/production.py", '''
from .base import *

DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
''')

# ─────────────────────────────────────────────────────────────
# 2. DJANGO APPS
# ─────────────────────────────────────────────────────────────
DJANGO_APPS = [
    "accounts", "teams", "services", "incidents", "monitoring",
    "investigations", "approvals", "remediation", "audit",
]

APP_TEMPLATES = {
    "admin.py": 'from django.contrib import admin\n',
    "apps.py": '''
from django.apps import AppConfig

class {class_name}Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.{app_name}"
    label = "{app_name}"
''',
    "models.py": 'from django.db import models  # noqa: F401\n',
    "serializers.py": 'from rest_framework import serializers  # noqa: F401\n',
    "views.py": 'from rest_framework import viewsets  # noqa: F401\n',
    "urls.py": '''
from django.urls import path

urlpatterns = []
''',
    "services.py": "# Business logic for this app\n",
    "selectors.py": "# Read-only query helpers\n",
    "permissions.py": "# Custom access control rules\n",
}

make_dir("apps")
make_file("apps/__init__.py")

for app in DJANGO_APPS:
    base = f"apps/{app}"
    make_dir(base)
    make_dir(f"{base}/migrations")
    make_dir(f"{base}/tests")

    make_file(f"{base}/__init__.py")
    make_file(f"{base}/migrations/__init__.py")
    make_file(f"{base}/tests/__init__.py")

    class_name = app.capitalize()
    for filename, template in APP_TEMPLATES.items():
        content = template.replace("{class_name}", class_name).replace("{app_name}", app)
        make_file(f"{base}/{filename}", content)

# FIX #1 / #4 — Define the custom User model (required by AUTH_USER_MODEL)
make_file("apps/accounts/models.py", '''
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model — required because AUTH_USER_MODEL = "accounts.User".
    Must be defined BEFORE running `manage.py migrate`.
    """
    display_name = models.CharField(max_length=150, blank=True)
    timezone = models.CharField(max_length=64, default="UTC")

    def __str__(self):
        return self.username
''')

make_file("apps/accounts/admin.py", '''
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Profile", {"fields": ("display_name", "timezone")}),
    )
''')

# Minimal starter models so migrations don't fail on empty apps
make_file("apps/teams/models.py", '''
from django.db import models
from django.conf import settings


class Team(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=32, default="member")

    class Meta:
        unique_together = ("team", "user")
''')

make_file("apps/services/models.py", '''
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=150, unique=True)
    kind = models.CharField(max_length=64, default="docker")  # docker | prometheus | k8s
    endpoint = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
''')

make_file("apps/incidents/models.py", '''
from django.db import models
from django.conf import settings


class Incident(models.Model):
    SEVERITY = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")]
    STATUS = [("open", "Open"), ("investigating", "Investigating"), ("resolved", "Resolved")]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=16, choices=SEVERITY, default="medium")
    status = models.CharField(max_length=16, choices=STATUS, default="open")
    service = models.ForeignKey("services.Service", on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.severity}] {self.title}"
''')

make_file("apps/monitoring/models.py", '''
from django.db import models


class Alert(models.Model):
    service = models.ForeignKey("services.Service", on_delete=models.CASCADE, related_name="alerts")
    name = models.CharField(max_length=255)
    severity = models.CharField(max_length=16, default="medium")
    firing = models.BooleanField(default=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
''')

make_file("apps/investigations/models.py", '''
from django.db import models


class Investigation(models.Model):
    STATUS = [("running", "Running"), ("done", "Done"), ("failed", "Failed")]

    incident = models.ForeignKey("incidents.Incident", on_delete=models.CASCADE, related_name="investigations")
    status = models.CharField(max_length=16, choices=STATUS, default="running")
    root_cause = models.TextField(blank=True)
    confidence = models.FloatField(default=0.0)
    findings = models.JSONField(default=list, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Investigation<{self.incident_id}>"


class InvestigationStep(models.Model):
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE, related_name="steps")
    name = models.CharField(max_length=64)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
''')

make_file("apps/approvals/models.py", '''
from django.db import models
from django.conf import settings


class ApprovalRequest(models.Model):
    STATUS = [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")]

    investigation = models.ForeignKey(
        "investigations.Investigation", on_delete=models.CASCADE, related_name="approvals"
    )
    proposed_actions = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=16, choices=STATUS, default="pending")
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
''')

make_file("apps/remediation/models.py", '''
from django.db import models


class RemediationExecution(models.Model):
    STATUS = [("pending", "Pending"), ("running", "Running"), ("done", "Done"), ("failed", "Failed")]

    approval = models.OneToOneField(
        "approvals.ApprovalRequest", on_delete=models.CASCADE, related_name="execution"
    )
    status = models.CharField(max_length=16, choices=STATUS, default="pending")
    log = models.JSONField(default=list, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
''')

make_file("apps/audit/models.py", '''
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=128)
    target_type = models.CharField(max_length=64)
    target_id = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
''')

# ─────────────────────────────────────────────────────────────
# 3. AI ENGINE
# ─────────────────────────────────────────────────────────────
make_dir("ai_engine")

make_file("ai_engine/__init__.py")
make_file("ai_engine/graph.py", '''
"""
Main LangGraph workflow.
Flow: triage -> collect_diagnostics -> analyze -> propose_remediation
"""
from langgraph.graph import StateGraph, END
from .state import InvestigationState
from .nodes import triage, collect_diagnostics, analyze, propose_remediation


def build_graph():
    g = StateGraph(InvestigationState)
    g.add_node("triage", triage.run)
    g.add_node("collect", collect_diagnostics.run)
    g.add_node("analyze", analyze.run)
    g.add_node("propose", propose_remediation.run)

    g.set_entry_point("triage")
    g.add_edge("triage", "collect")
    g.add_edge("collect", "analyze")
    g.add_edge("analyze", "propose")
    g.add_edge("propose", END)

    return g.compile()
''')

make_file("ai_engine/state.py", '''
from typing import TypedDict, Optional


class InvestigationState(TypedDict, total=False):
    incident_id: str
    service: dict
    alert: dict
    diagnostics: dict
    findings: list
    root_cause: Optional[str]
    confidence: Optional[float]
    remediation: Optional[dict]
    steps: list
''')

make_dir("ai_engine/nodes")
make_file("ai_engine/nodes/__init__.py")
for node in ["triage", "collect_diagnostics", "analyze", "propose_remediation"]:
    make_file(f"ai_engine/nodes/{node}.py", f'''
def run(state: dict) -> dict:
    """{node.replace("_", " ").title()} step."""
    state.setdefault("steps", []).append("{node}")
    return state
''')

make_dir("ai_engine/tools")
make_file("ai_engine/tools/__init__.py")
make_file("ai_engine/tools/registry.py", '''
"""Central registry of AI tools available to the agent."""

ALL_TOOLS = []


def register(tool):
    ALL_TOOLS.append(tool)
    return tool
''')

# FIX #5 — DockerConnector now has the methods the tools call
make_file("ai_engine/tools/docker_tools.py", '''
from langchain_core.tools import tool
from integrations.docker.client import DockerConnector


@tool
def get_container_status(service_id: str) -> dict:
    """Return Docker container status for a service."""
    return DockerConnector().get_status(service_id)


@tool
def get_container_logs(service_id: str, lines: int = 100) -> list:
    """Return recent Docker logs for a service."""
    return DockerConnector().get_logs(service_id, lines=lines)
''')

# FIX #6 — PrometheusConnector has query + get_alerts
make_file("ai_engine/tools/prometheus_tools.py", '''
from langchain_core.tools import tool
from integrations.prometheus.client import PrometheusConnector


@tool
def query_metric(query: str) -> dict:
    """Run a PromQL query and return the result."""
    return PrometheusConnector().query(query)


@tool
def get_active_alerts() -> list:
    """Return currently firing alerts."""
    return PrometheusConnector().get_alerts()
''')

make_file("ai_engine/tools/logs_tools.py", '''
from langchain_core.tools import tool


@tool
def search_logs(service_id: str, pattern: str) -> list:
    """Search service logs for a pattern."""
    return []
''')

make_dir("ai_engine/prompts")
make_file("ai_engine/prompts/__init__.py")
make_file("ai_engine/prompts/system.md", "# System Prompt\n\nYou are an expert SRE investigator.\n")
make_file("ai_engine/prompts/triage.md", "# Triage Prompt\n\nClassify the incident.\n")
make_file("ai_engine/prompts/analysis.md", "# Analysis Prompt\n\nDetermine the root cause.\n")
make_file("ai_engine/prompts/remediation.md", "# Remediation Prompt\n\nPropose safe fixes.\n")

make_dir("ai_engine/schemas")
make_file("ai_engine/schemas/__init__.py")
make_file("ai_engine/schemas/investigation_result.py", '''
from pydantic import BaseModel
from typing import Optional, List


class InvestigationResult(BaseModel):
    incident_id: str
    root_cause: Optional[str] = None
    confidence: float = 0.0
    findings: List[dict] = []
''')
make_file("ai_engine/schemas/remediation_plan.py", '''
from pydantic import BaseModel
from typing import List


class RemediationAction(BaseModel):
    action: str
    target: str
    risk: str = "low"


class RemediationPlan(BaseModel):
    actions: List[RemediationAction] = []
''')

make_dir("ai_engine/policies")
make_file("ai_engine/policies/__init__.py")
make_file("ai_engine/policies/safety.py", '''
"""AI safety rules — block dangerous actions."""

FORBIDDEN_ACTIONS = {
    "delete_database",
    "drop_table",
    "rm_rf",
    "shutdown_cluster",
}


def is_action_allowed(action: str) -> bool:
    return action not in FORBIDDEN_ACTIONS
''')
make_file("ai_engine/policies/execution_rules.py", '''
"""Execution rules — what AI can and cannot do."""

ALLOWED_ACTIONS = {
    "restart_container",
    "scale_replicas",
    "rollback_deployment",
}


def requires_approval(action: str) -> bool:
    return True  # everything state-changing needs approval
''')

make_dir("ai_engine/evaluation/scenarios")
make_file("ai_engine/evaluation/__init__.py")
make_file("ai_engine/evaluation/runner.py", '''
"""Run AI evaluation against known scenarios."""


def run_all():
    return {"total": 0, "passed": 0, "accuracy": 0.0}
''')
make_file("ai_engine/evaluation/scenarios/__init__.py")
make_file("ai_engine/evaluation/scenarios/container_crash.yaml", "name: container_crash\nexpected_root_cause: container_oom_killed\n")
make_file("ai_engine/evaluation/scenarios/high_cpu.yaml", "name: high_cpu\nexpected_root_cause: cpu_saturation\n")
make_file("ai_engine/evaluation/scenarios/memory_leak.yaml", "name: memory_leak\nexpected_root_cause: memory_leak\n")

make_dir("ai_engine/services")
make_file("ai_engine/services/__init__.py")
make_file("ai_engine/services/orchestrator.py", '''
"""Glue between Django and the LangGraph AI workflow."""
from ai_engine.graph import build_graph


def run_investigation(payload: dict) -> dict:
    graph = build_graph()
    result = graph.invoke(payload)
    return result
''')

# ─────────────────────────────────────────────────────────────
# 4. INTEGRATIONS  (FIX #5 / #6 — add missing methods)
# ─────────────────────────────────────────────────────────────
make_dir("integrations")
make_file("integrations/__init__.py")
make_file("integrations/base.py", '''
from abc import ABC, abstractmethod


class BaseConnector(ABC):
    @abstractmethod
    def health_check(self) -> bool: ...

    @abstractmethod
    def get_status(self, service_id: str) -> dict: ...
''')

make_file("integrations/docker/__init__.py")
make_file("integrations/docker/client.py", '''
"""Connector to Docker."""
from integrations.base import BaseConnector


class DockerConnector(BaseConnector):
    def health_check(self) -> bool:
        return True

    def get_status(self, service_id: str) -> dict:
        return {"service_id": service_id, "state": "unknown"}

    def get_logs(self, service_id: str, lines: int = 100) -> list:
        return []
''')

make_file("integrations/prometheus/__init__.py")
make_file("integrations/prometheus/client.py", '''
"""Connector to Prometheus."""
from integrations.base import BaseConnector


class PrometheusConnector(BaseConnector):
    def health_check(self) -> bool:
        return True

    def get_status(self, service_id: str) -> dict:
        return {"service_id": service_id, "state": "unknown"}

    def query(self, promql: str) -> dict:
        return {"query": promql, "result": []}

    def get_alerts(self) -> list:
        return []
''')

for name in ["grafana", "cloudwatch", "kubernetes"]:
    make_file(f"integrations/{name}/__init__.py")
    make_file(f"integrations/{name}/client.py", f'''
"""Connector to {name}."""
from integrations.base import BaseConnector


class {name.capitalize()}Connector(BaseConnector):
    def health_check(self) -> bool:
        return True

    def get_status(self, service_id: str) -> dict:
        return {{"service_id": service_id, "state": "unknown"}}
''')

# ─────────────────────────────────────────────────────────────
# 5. TASKS (Celery)
# ─────────────────────────────────────────────────────────────
make_dir("tasks")
make_file("tasks/__init__.py")
make_file("tasks/investigations.py", '''
from celery import shared_task


@shared_task
def run_investigation_task(incident_id: str):
    from ai_engine.services.orchestrator import run_investigation
    result = run_investigation({"incident_id": incident_id})
    return result
''')
make_file("tasks/monitoring.py", '''
from celery import shared_task


@shared_task
def poll_alerts():
    # fetch alerts -> create incidents -> trigger investigations
    return {"polled": 0}
''')
make_file("tasks/remediation.py", '''
from celery import shared_task


@shared_task
def execute_remediation_task(plan_id: str):
    return {"plan_id": plan_id, "status": "pending"}
''')

# ─────────────────────────────────────────────────────────────
# 6. SIMULATOR
# ─────────────────────────────────────────────────────────────
make_dir("simulator")

make_file("simulator/__init__.py")
make_dir("simulator/services")
make_file("simulator/services/__init__.py")
make_file("simulator/services/fake_docker.py", '''
"""Fake Docker client for local testing."""


class FakeDocker:
    def __init__(self):
        self.containers = {}

    def get_status(self, service_id: str) -> dict:
        return self.containers.get(service_id, {"state": "running"})
''')

make_dir("simulator/scenarios")
make_file("simulator/scenarios/__init__.py")
make_file("simulator/scenarios/runner.py", '''
"""Run a named simulation scenario."""


def run_scenario(name: str):
    return {"scenario": name, "status": "started"}
''')

make_dir("simulator/failures")
make_file("simulator/failures/__init__.py")
make_file("simulator/failures/crash.py", 'def inject(service_id: str):\n    return {"service_id": service_id, "failure": "crash"}\n')
make_file("simulator/failures/cpu_spike.py", 'def inject(service_id: str, percent: int = 99):\n    return {"service_id": service_id, "failure": "cpu_spike", "percent": percent}\n')
make_file("simulator/failures/memory_leak.py", 'def inject(service_id: str):\n    return {"service_id": service_id, "failure": "memory_leak"}\n')

make_dir("simulator/generators")
make_file("simulator/generators/__init__.py")
make_file("simulator/generators/alert_generator.py", 'def generate_alert(service_id: str, severity: str = "high"):\n    return {"service_id": service_id, "severity": severity}\n')
make_file("simulator/generators/metric_generator.py", 'import random\n\n\ndef generate_metric(name: str):\n    return {"name": name, "value": random.random()}\n')

# ─────────────────────────────────────────────────────────────
# 7. TESTS
# ─────────────────────────────────────────────────────────────
make_dir("tests")
make_file("tests/__init__.py")
make_file("tests/conftest.py", '''
import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="tester", password="test123"
    )
''')

for t in ["unit", "integration", "ai_engine", "security", "evaluation"]:
    make_dir(f"tests/{t}")
    make_file(f"tests/{t}/__init__.py")

# ─────────────────────────────────────────────────────────────
# 8. INFRA
# ─────────────────────────────────────────────────────────────
make_dir("infra/docker")
make_file("infra/docker/entrypoint.sh", '#!/bin/sh\nset -e\nexec "$@"\n')

make_dir("infra/nginx")
make_file("infra/nginx/nginx.conf", '''
worker_processes 1;
events { worker_connections 1024; }
http {
    server {
        listen 80;
        location / { proxy_pass http://web:8000; }
    }
}
''')

make_dir("infra/prometheus")
make_file("infra/prometheus/prometheus.yml", '''
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: incidentops
    static_configs:
      - targets: ["web:8000"]
''')

make_dir("infra/grafana/dashboards")
make_file("infra/grafana/dashboards/.gitkeep")

# ─────────────────────────────────────────────────────────────
# 9. SCRIPTS
# ─────────────────────────────────────────────────────────────
make_dir("scripts")
make_file("scripts/__init__.py")
make_file("scripts/setup.py", '"""One-time project setup."""\n\n\ndef main():\n    print("Run: python manage.py migrate && python manage.py createsuperuser")\n\n\nif __name__ == "__main__":\n    main()\n')
make_file("scripts/init_db.py", '"""Initialize database."""\n\n\ndef main():\n    print("Run: python manage.py migrate")\n\n\nif __name__ == "__main__":\n    main()\n')
make_file("scripts/seed_demo_data.py", '"""Insert demo data."""\n\n\ndef main():\n    print("Seeding demo data...")\n\n\nif __name__ == "__main__":\n    main()\n')

# ─────────────────────────────────────────────────────────────
# 10. DOCS
# ─────────────────────────────────────────────────────────────
make_dir("docs")
make_file("docs/architecture.md", "# Architecture\n\nSix-layer design.\n")
make_file("docs/ai_workflow.md", "# AI Workflow\n\ntriage -> collect -> analyze -> propose.\n")
make_file("docs/api.md", "# API\n\nDRF endpoints.\n")
make_file("docs/deployment.md", "# Deployment\n\nDocker Compose.\n")

# ─────────────────────────────────────────────────────────────
# 11. ROOT FILES
# ─────────────────────────────────────────────────────────────
make_file(".env.example", '''
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=incidentops
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=
''')

# FIX #12 — create a working .env so `docker compose up` works immediately
make_file(".env", '''
SECRET_KEY=dev-insecure-key-change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=incidentops
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=
''')

make_file(".gitignore", '''
__pycache__/
*.py[cod]
.venv/
.env
db.sqlite3
.idea/
.vscode/
.DS_Store
''')

make_file(".dockerignore", '''
.venv/
__pycache__/
.git/
.env
''')

# FIX #8 / #10 — proper Dockerfile with uv lock + gunicorn
make_file("Dockerfile", '''
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first (cache layer)
COPY pyproject.toml uv.lock* ./

# Install dependencies (frozen if lock exists, otherwise resolve)
RUN uv sync --no-dev

# Copy the rest of the project
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
''')

make_file("docker-compose.yml", '''
version: "3.9"

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: incidentops
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports: ["6379:6379"]

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes: [".:/app"]
    ports: ["8000:8000"]
    depends_on: [db, redis]
    env_file: .env

  worker:
    build: .
    command: celery -A config worker -l info
    volumes: [".:/app"]
    depends_on: [db, redis]
    env_file: .env

volumes:
  pgdata:
''')

make_file("manage.py", '''
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
''')

# FIX #8 / #9 — add gunicorn, langchain-openai, dj-database-url (optional), pytest-django etc.
make_file("pyproject.toml", '''
[project]
name = "incidentops-ai"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "django>=5.0",
    "djangorestframework>=3.15",
    "celery>=5.3",
    "redis>=5.0",
    "psycopg[binary]>=3.1",
    "python-dotenv>=1.0",
    "gunicorn>=21.2",
    "langgraph>=0.2",
    "langchain-core>=0.3",
    "langchain-openai>=0.2",
    "pydantic>=2.6",
    "docker>=7.0",
    "prometheus-api-client>=0.5",
    "pytest>=8.0",
    "pytest-django>=4.8",
]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.development"
python_files = ["test_*.py", "*_test.py"]
''')

make_file("README.md", '''
# IncidentOps-AI

AI-powered incident investigation & remediation platform.

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. (Optional) generate uv.lock for reproducible builds
uv lock

# 3. Start Postgres + Redis
docker compose up -d db redis

# 4. Run migrations
python manage.py migrate

# 5. Create admin user
python manage.py createsuperuser

# 6. Run server
python manage.py runserver

# 7. In another terminal, run Celery worker
celery -A config worker -l info
''')