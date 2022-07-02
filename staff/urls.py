from django.urls import path
from staff import views

urlpatterns = [
    path("admin", views.Admin.as_view()),
    path("admin/videos", views.ListVideos.as_view()),
    path("admin/videos/add-video", views.AddVideo.as_view()),
    path("admin/videos/cover-video", views.CoverVideo.as_view()),
    path("admin/videos/cover-video-id", views.cover_videoid),
    path("admin/forms", views.ListForm.as_view()),
    path("admin/forms/add-form", views.AddForm.as_view()),
    path("admin/subjects", views.ListSubjects.as_view()),
    path("admin/subjects/add-subject", views.AddSubject.as_view()),
    path("admin/units", views.ListUnits.as_view()),
    path("admin/units/add-unit", views.AddUnit.as_view()),
    path("admin/units/view", views.UnitDetailView.as_view()),
    path("admin/payments/invoices", views.ListInvoices.as_view()),
    path("admin/payments/transactions", views.ListTransactions.as_view()),
    path("admin/subscriptions/active", views.ListCurrentSubscription.as_view()),
    path("admin/subscriptions/expired", views.ListExpiredSubscriptions.as_view()),
    path("admin/subscriptions/revoked", views.ListRevokedSubscriptions.as_view()),
    path("admin/counties", views.ListCounties.as_view()),
    path("admin/counties/add-county", views.AddCounty.as_view()),
    path("admin/payments/unit-amount", views.AddUnitAmountView.as_view()),
    path("admin/registration-codes", views.ListRegistrationCodes.as_view()),
    path("admin/registration-codes/add-code", views.AddRegistrationCodes.as_view()),
    path("admin/subjects/<pk>", views.RetrieveSubject.as_view(), name="retrieve_subjects"),
    path("admin/payments/add-amount", views.AddSubjectAmountView.as_view()),
    path("admin/forms/<pk>", views.RetrieveForm.as_view()),
    path("admin/payments/add-form-amount", views.AddFormAmountView.as_view())
]
