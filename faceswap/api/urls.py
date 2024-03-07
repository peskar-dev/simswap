from django.urls import path

from .views import HealthView
from .views import (
    ImageUploadView,
    TaskStatusView,
)

urlpatterns = [
    path("health/", HealthView.as_view()),
    path("images/", ImageUploadView.as_view(), name="image_upload"),
    path(
        "jobs/<str:task_id>/",
        TaskStatusView.as_view(),
        name="job_status",
    ),
]

