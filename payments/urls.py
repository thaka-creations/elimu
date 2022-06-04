from django.urls import path
from rest_framework.routers import DefaultRouter
from payments import views

router = DefaultRouter(trailing_slash=False)

router.register("unit-amount", views.UnitAmountViewSet, basename="unit-amount")
router.register("subscription", views.SubscriptionViewSet, basename="subscription")

urlpatterns = router.urls


