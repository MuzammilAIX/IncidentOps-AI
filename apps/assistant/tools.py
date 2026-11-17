"""Tools available to the AI assistant."""
from apps.incidents.models import Incident
from apps.services.models import Service
from ai_engine.tools.runbook_tool import search_runbooks as search_runbooks_impl
from apps.incidents.services import trigger_investigation


def create_incident(title, severity="high", service="", description=""):
    if severity not in ("low", "medium", "high", "critical"):
        severity = "high"
    svc = None
    if service:
        svc = Service.objects.filter(name=service).first()
    incident = Incident.objects.create(
        title=title[:255], description=description or title,
        severity=severity, status="open", service=svc,
    )
    result = {"incident_id": incident.id, "title": incident.title, "severity": severity}
    try:
        qr = trigger_investigation(incident)
        result["investigation_queued"] = qr.get("queued", False)
        result["task_id"] = qr.get("task_id")
    except Exception as e:
        result["investigation_error"] = str(e)
    return result


def search_runbooks_tool(query, limit=3):
    matches = search_runbooks_impl(query=query, service_name="", limit=limit)
    return {
        "count": len(matches),
        "runbooks": [
            {"code": r["code"], "title": r["title"], "category": r["category"], "score": r["score"]}
            for r in matches
        ],
    }


def search_incidents_tool(query, limit=5):
    qs = Incident.objects.all()
    if query:
        words = [w for w in query.lower().split() if len(w) > 3][:3]
        from django.db.models import Q
        q = Q()
        for w in words:
            q |= Q(title__icontains=w) | Q(description__icontains=w)
        qs = qs.filter(q) if q else qs
    incidents = qs.order_by("-created_at")[:limit]
    return {
        "count": incidents.count(),
        "incidents": [
            {
                "id": i.id, "title": i.title, "severity": i.severity,
                "status": i.status, "service": i.service.name if i.service else "",
                "created_at": i.created_at.isoformat(),
            }
            for i in incidents
        ],
    }


def answer_question(question):
    return {"answered": True, "question": question}
