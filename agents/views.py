from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from payments import models as payment_models


# Create your views here.
class AgentMixin(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_agent


class AgentAnalytics(AgentMixin, View):
    template_name = "agent/index.html"

    def get(self, request):
        users = request.user.agent_user.subscribers.all()
        invoices = payment_models.Invoice.objects.filter(user__in=users)
        context = {"users": users, "invoices": invoices}
        return render(request, self.template_name, context)