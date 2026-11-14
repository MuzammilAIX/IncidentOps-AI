
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/incidents/", include("apps.incidents.urls")),
    path("api/investigations/", include("apps.investigations.urls")),
    path("api/approvals/", include("apps.approvals.urls")),
    path("api/monitoring/", include("apps.monitoring.urls")),
]