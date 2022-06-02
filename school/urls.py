from django.urls import path

from . import views

urlpatterns = [
    path('form/<pk>', views.FormView.as_view())
]
