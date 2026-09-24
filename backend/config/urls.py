from django.contrib import admin
from django.db import connection
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return Response({"status": "ok", "service": "worknoon-refund-backend", "database": "ok"})
    except Exception:
        return Response({"status": "degraded", "service": "worknoon-refund-backend", "database": "unavailable"}, status=503)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", health, name="health"),
    path("api/v1/refunds/", include("apps.refunds.api.urls")),
]
