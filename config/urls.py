from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path("admin/", admin.site.urls),

    # APIs
    path("api/incidents/", include("apps.incidents.urls")),
    path("api/investigations/", include("apps.investigations.urls")),
    path("api/approvals/", include("apps.approvals.urls")),
    path("api/monitoring/", include("apps.monitoring.urls")),
    path("api/auth/", include("apps.accounts.urls")),

    # Login page (public)
    path("login/", TemplateView.as_view(template_name="login.html"), name="login"),

    # Frontend pages (auth handled client-side via api.me())
    path("", TemplateView.as_view(template_name="index.html"), name="dashboard"),
    path("incidents/", TemplateView.as_view(template_name="incidents.html"), name="incidents"),
    path("incident/", TemplateView.as_view(template_name="incident.html"), name="incident"),
    path("approvals/", TemplateView.as_view(template_name="approvals.html"), name="approvals"),
]
