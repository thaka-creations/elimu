from django.urls import path
from payments import views

urlpatterns = [
    path('subscription/check-status', views.check_status),
]
