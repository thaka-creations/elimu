from rest_framework.routers import DefaultRouter
from mfa.api import views

router = DefaultRouter(trailing_slash=False)
router.register('otp', views.OtpViewSet, basename='otp')

urlpatterns = router.urls
