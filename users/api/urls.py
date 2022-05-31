from rest_framework.routers import DefaultRouter
from users.api.views import authentication, public, staff

router = DefaultRouter(trailing_slash=False)

router.register('auth', authentication.AuthenticationViewSet, basename='auth')
router.register('public', public.RegistrationViewSet, basename='public')

urlpatterns = router.urls
