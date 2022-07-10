from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from payments import models as payment_models
from users import models as user_models


# Create your views here.
class AgentMixin(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_agent


class AgentAnalytics(AgentMixin, View):
    template_name = "agent/index.html"

    def get(self, request):
        users = request.user.agent_user.subscribers.all()
        invoices = payment_models.Invoice.objects.filter(user__in=users)
        start_date = datetime.now().replace(day=1)
        end_date = start_date + relativedelta(months=1)
        default_invoices = invoices.filter(commission__isnull=False, transaction_date__gte=start_date,
                                           transaction_date__lte=end_date)
        commission = 0
        if default_invoices.exists():
            for invoice in default_invoices:
                commission += invoice.commission
        context = {"users": users, "invoices": invoices, "start_date": start_date.strftime("%Y-%m-%d"),
                   "end_date": end_date.strftime("%Y-%m-%d"), "commission": commission}
        return render(request, self.template_name, context)

    def post(self, request):
        data = request.POST
        agent_id = data['agent']
        format_ = '%Y-%m-%d'
        date_from = datetime.strptime(data['date_from'], format_)
        date_to = datetime.strptime(data['date_to'], format_)

        try:
            agent = user_models.User.objects.get(id=agent_id)
        except user_models.Agent.DoesNotExist:
            return JsonResponse({"message": "invalid agent"})

        users = list(agent.agent_user.subscribers.values_list("id", flat=True))
        invoices = payment_models.Invoice.objects.filter(
            user__id__in=users, commission__isnull=False, transaction_date__date__gte=date_from,
            transaction_date__date__lte=date_to)

        commission = 0
        if invoices.exists():
            for invoice in invoices:
                commission += invoice.commission
        return JsonResponse({"commission": commission})
