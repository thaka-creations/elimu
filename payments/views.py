from django.views import View
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseBadRequest
from payments import models as payment_models


@require_http_methods(["GET"])
def check_status(request):
    qs = payment_models.Subscription.objects.filter(user=request.user, status="ACTIVE")
    if not qs.exists():
        return HttpResponseBadRequest("Not subscribed")


class SubscriptionView(View):
    def check_status(self, request):
        pass
