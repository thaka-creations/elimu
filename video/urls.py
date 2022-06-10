from django.urls import path
from video.api import views

urlpatterns = [
    path("get-video-otp", views.GetVideoOtp.as_view(), name="get-video-otp")
]