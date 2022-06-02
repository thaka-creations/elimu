"""Elimu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

api_version = 'api/v1/'

api_patterns = [
    path('admin/', admin.site.urls),
    path(api_version + 'o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path(api_version + 'school/', include('school.api.urls')),
    path(api_version + 'users/', include('users.api.urls')),
    path(api_version + 'mfa/', include('mfa.api.urls'))
]

urlpatterns = api_patterns + [
    path('', include('school.urls')),
    path('', include('users.urls'))
]


