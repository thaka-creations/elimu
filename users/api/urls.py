from rest_framework.routers import DefaultRouter
from users.api import views

router = DefaultRouter(trailing_slash=False)

router.register("registration", views.Registration, basename="registration")
router.register("auth", views.Authentication, basename="auth")
router.register("user", views.UserViewSet, basename="user")

urlpatterns = router.urls
