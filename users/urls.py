from django.urls import path
from users import views

urlpatterns = [
    path('registration', views.RegistrationView.as_view()),
    path('login', views.LoginView.as_view()),
    path('logout', views.logout_view),
    path('', views.ProtectedView.as_view()),
    path('account-settings', views.account_settings),
    path('account-activity', views.account_activity),
    path('rest-password', views.ResetPasswordView.as_view())
]