from django.urls import path

from . import views

urlpatterns = [
    path('form/<pk>', views.FormView.as_view()),
    path('form/subject/<pk>', views.SubjectView.as_view()),
    path('form/subject/unit/<pk>', views.UnitView.as_view()),
]
