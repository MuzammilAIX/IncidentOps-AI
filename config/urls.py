
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required


def protected(template):
    """Serve a frontend page (requires login)."""
    return login_required(TemplateView.as_view(template_name=template))


urlpatterns = [
    path("admin/", admin.site.urls),

    # APIs
    path("api/incidents/", include("apps.incidents.urls")),
    path("api/investigations/", include("apps.investigations.urls")),
    path("api/approvals/", include("apps.approvals.urls")),
    path("api/monitoring/", include("apps.monitoring.urls")),
    path("api/auth/", include("apps.accounts.urls")),

    # Frontend pages (require login)
    path("", protected("index.html"), name="dashboard"),
    path("incidents/", protected("incidents.html"), name="incidents"),
    path("incident/", protected("incident.html"), name="incident"),
    path("approvals/", protected("approvals.html"), name="approvals"),

    # Login page (public)
    path("login/", TemplateView.as_view(template_name="login.html"), name="login"),
]
