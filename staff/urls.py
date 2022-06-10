from django.urls import path
from staff import views


urlpatterns = [
    path("admin", views.Admin.as_view())
]