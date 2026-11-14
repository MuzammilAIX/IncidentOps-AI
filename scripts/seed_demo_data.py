"""Insert demo data for IncidentOps-AI."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.teams.models import Team, Membership
from apps.services.models import Service
from apps.incidents.models import Incident
from apps.investigations.models import Investigation, InvestigationStep
from apps.approvals.models import ApprovalRequest

User = get_user_model()


def main():
    print("=== Seeding demo data ===")

    admin, _ = User.objects.get_or_create(
        username="admin",
        defaults={"email": "admin@incidentops.local", "is_staff": True, "is_superuser": True},
    )

    teams_data = ["Platform", "Backend", "SRE"]
    teams = {}
    for name in teams_data:
        t, _ = Team.objects.get_or_create(name=name)
        teams[name] = t
        Membership.objects.get_or_create(team=t, user=admin, defaults={"role": "owner"})
        print(f"  Team: {t.name}")

    services_data = [
        {"name": "api-gateway", "kind": "docker", "endpoint": "http://api-gateway:8000"},
        {"name": "payment-service", "kind": "docker", "endpoint": "http://payment-service:8080"},
        {"name": "auth-service", "kind": "docker", "endpoint": "http://auth-service:8081"},
        {"name": "notification-worker", "kind": "worker", "endpoint": ""},
    ]
    services = {}
    for s_data in services_data:
        s, _ = Service.objects.get_or_create(name=s_data["name"], defaults=s_data)
        services[s.name] = s
        print(f"  Service: {s.name}")

    incidents_data = [
        {
            "title": "Payment API returning HTTP 500",
            "description": "Sudden spike in 500 errors from payment-service after deploy.",
            "severity": "critical",
            "status": "open",
            "service": services["payment-service"],
        },
        {
            "title": "Auth service latency above SLO",
            "description": "p99 latency jumped from 80ms to 2.1s over the past hour.",
            "severity": "high",
            "status": "investigating",
            "service": services["auth-service"],
        },
        {
            "title": "API gateway 502 Bad Gateway",
            "description": "Intermittent 502s from api-gateway in production.",
            "severity": "high",
            "status": "open",
            "service": services["api-gateway"],
        },
        {
            "title": "Notification worker OOM crash",
            "description": "notification-worker container restarting due to memory exhaustion.",
            "severity": "medium",
            "status": "open",
            "service": services["notification-worker"],
        },
        {
            "title": "Database connection pool exhausted",
            "description": "All DB connections in use, new queries timing out.",
            "severity": "critical",
            "status": "resolved",
            "service": services["payment-service"],
        },
        {
            "title": "SSL certificate expiring in 7 days",
            "description": "api-gateway TLS cert needs renewal.",
            "severity": "low",
            "status": "open",
            "service": services["api-gateway"],
        },
    ]
    incidents = []
    for i_data in incidents_data:
        i, _ = Incident.objects.get_or_create(
            title=i_data["title"], defaults={**i_data, "created_by": admin}
        )
        incidents.append(i)
        print(f"  Incident: [{i.severity}] {i.title} -> {i.status}")

    # Investigations with findings
    inv1, _ = Investigation.objects.get_or_create(
        incident=incidents[0],
        defaults={
            "status": "done",
            "root_cause": "Deployment #452 introduced a missing migration; payment inserts fail with NOT NULL violation.",
            "confidence": 0.87,
            "finished_at": timezone.now(),
            "findings": [
                {"source": "logs", "detail": "Found 428 ERROR entries: 'null value in column payment_id'"},
                {"source": "metrics", "detail": "Error rate 100% starting at 14:22 UTC"},
                {"source": "deployments", "detail": "Deploy #452 completed at 14:20 UTC"},
            ],
        },
    )
    InvestigationStep.objects.get_or_create(
        investigation=inv1, name="collect_logs",
        defaults={"payload": {"lines": 428, "errors": 428}},
    )
    InvestigationStep.objects.get_or_create(
        investigation=inv1, name="analyze_logs",
        defaults={"payload": {"pattern": "NOT NULL violation", "matches": 428}},
    )
    InvestigationStep.objects.get_or_create(
        investigation=inv1, name="propose_remediation",
        defaults={"payload": {"action": "rollback", "deployment_id": 452}},
    )
    print(f"  Investigation (done): incident={inv1.incident_id}")

    inv2, _ = Investigation.objects.get_or_create(
        incident=incidents[1],
        defaults={
            "status": "running",
            "root_cause": "",
            "confidence": 0.45,
            "findings": [
                {"source": "metrics", "detail": "p99 latency 2.1s, p50 110ms"},
                {"source": "logs", "detail": "Increased CPU throttling on auth-service"},
            ],
        },
    )
    print(f"  Investigation (running): incident={inv2.incident_id}")

    inv3, _ = Investigation.objects.get_or_create(
        incident=incidents[2],
        defaults={
            "status": "done",
            "root_cause": "Upstream payment-service returning 500s propagates as 502 at gateway.",
            "confidence": 0.92,
            "finished_at": timezone.now(),
            "findings": [
                {"source": "logs", "detail": "502 count correlates with payment-service 500 spike"},
                {"source": "topology", "detail": "api-gateway -> payment-service is sole upstream"},
            ],
        },
    )
    print(f"  Investigation (done): incident={inv3.incident_id}")

    # Approvals linked to investigations
    ApprovalRequest.objects.get_or_create(
        investigation=inv1,
        defaults={
            "status": "pending",
            "proposed_actions": [
                {"action": "rollback", "target": "payment-service", "deployment_id": 452, "risk": "low"},
            ],
        },
    )
    ApprovalRequest.objects.get_or_create(
        investigation=inv3,
        defaults={
            "status": "pending",
            "proposed_actions": [
                {"action": "restart", "target": "payment-service", "risk": "medium"},
                {"action": "rollback", "target": "payment-service", "deployment_id": 452, "risk": "low"},
            ],
        },
    )
    ApprovalRequest.objects.get_or_create(
        investigation=inv2,
        defaults={
            "status": "approved",
            "decided_by": admin,
            "decided_at": timezone.now(),
            "proposed_actions": [
                {"action": "scale_up", "target": "auth-service", "replicas": 4, "risk": "low"},
            ],
        },
    )
    print("  Approvals: 2 pending + 1 approved")

    print("=== Seed complete ===")
    print(f"  Teams: {Team.objects.count()}")
    print(f"  Services: {Service.objects.count()}")
    print(f"  Incidents: {Incident.objects.count()}")
    print(f"  Investigations: {Investigation.objects.count()}")
    print(f"  Approvals: {ApprovalRequest.objects.count()}")


if __name__ == "__main__":
    main()
