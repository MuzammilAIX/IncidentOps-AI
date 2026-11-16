"""Runbook lookup tool."""
from apps.monitoring.models import Runbook


def search_runbooks(query="", service_name="", limit=3):
    qs = Runbook.objects.all()
    query_lower = (query or "").lower().strip()
    tokens = [t for t in query_lower.split() if len(t) >= 3]
    scored = []
    for rb in qs:
        score = 0
        if service_name and rb.service_hint and rb.service_hint.lower() == service_name.lower():
            score += 10
        for kw in (rb.keywords or []):
            if any(kw.lower() in t for t in tokens):
                score += 5
        for t in tokens:
            if t in rb.title.lower():
                score += 3
            if t in rb.content.lower():
                score += 1
        if score > 0:
            scored.append({"code": rb.code, "title": rb.title, "category": rb.category, "content": rb.content, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]