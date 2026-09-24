import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_reports_database_ok():
    response = APIClient().get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"
