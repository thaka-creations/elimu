from django.urls import path
from staff import views

urlpatterns = [
    path("admin", views.Admin.as_view()),
    path("admin/videos", views.ListVideos.as_view()),
    path("admin/videos/add-video", views.AddVideo.as_view()),
    path("admin/forms", views.ListForm.as_view()),
    path("admin/forms/add-form", views.AddForm.as_view()),
    path("admin/subjects", views.ListSubjects.as_view()),
    path("admin/subjects/add-subject", views.AddSubject.as_view()),
    path("admin/units", views.ListUnits.as_view()),
    path("admin/units/add-unit", views.AddUnit.as_view()),
    path("admin/units/view", views.UnitDetailView.as_view())
]
