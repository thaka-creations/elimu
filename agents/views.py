from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin


# Create your views here.
class AgentMixin(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_agent


class AgentAnalytics(AgentMixin, View):
    template_name = "agent/index.html"

    def get(self, request):
        return render(request, self.template_name)