from django.urls import path

from apps.refunds.api.views import RefundRequestDetailView, RefundRequestListCreateView

urlpatterns = [
    path("requests/", RefundRequestListCreateView.as_view(), name="refund-request-list-create"),
    path("requests/<uuid:pk>/", RefundRequestDetailView.as_view(), name="refund-request-detail"),
]
