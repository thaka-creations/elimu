from rest_framework.routers import DefaultRouter
from school.api import views as school_api_views

router = DefaultRouter()

router.register('subject', school_api_views.SubjectViewSet, basename='subject')
router.register('form', school_api_views.FormViewSet, basename='form')
router.register('unit', school_api_views.UnitViewSet, basename='unit')
router.register('video', school_api_views.VideoViewSet, basename='video')

urlpatterns = router.urls
