from django.urls import path
from agents.views import AgentAnalytics

urlpatterns = [
    path('agent', AgentAnalytics.as_view(), name='agent-analytics')
]