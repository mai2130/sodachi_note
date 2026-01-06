from django.urls import path
from .views import guardian_attendance_upsert

app_name = "attendances"

urlpatterns = [
    path("guardian/upsert/", guardian_attendance_upsert, name="guardian_upsert"),
]
