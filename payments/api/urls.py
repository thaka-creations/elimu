from django.urls import path
from rest_framework.routers import DefaultRouter
from payments.api import views

router = DefaultRouter(trailing_slash=False)

router.register("unit-amount", views.UnitAmountViewSet, basename="unit-amount")
router.register("subscription", views.SubscriptionViewSet, basename="subscription")
router.register("subject-amounts", views.ListSubjectAmount, basename="subject-amounts")
router.register("form-amounts", views.ListFormAmount, basename="form-amounts")
router.register("topic-amounts", views.TopicAmountViewSet, basename="topic-amounts")
router.register("invoice", views.InvoiceViewSet, basename="invoice")

urlpatterns = [
    path("checkout", views.MpesaCheckout.as_view()),
    path("callback", views.MpesaCallBack.as_view()),
    path("check-form-subscription", views.CheckFormSubscription.as_view()),
]
urlpatterns += router.urls


